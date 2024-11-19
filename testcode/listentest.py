import tkinter as tk
from tkinter import ttk, scrolledtext
import firebase_admin
from firebase_admin import credentials, db
from typing import List, Dict
from datetime import datetime
from queue import Queue
import threading
import time

class FirebaseDataCollector:
    def __init__(self):
        self.data_queue = Queue()
        self.is_listening = False
        self.listener = None
        self.collected_data = []
        self.start_time = None
        self.logged_in_users = set()    # Track logged in users
        self.latest_selections = {}      # Track latest selections per user
        
    def handle_changes(self, event):
        if event.data:
            data = event.data
            name = data.get('name', 'Unknown')
            command = data.get('command', 'None')
            selection = data.get('selection', None)  # Track selection instead of answer
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = {
                'timestamp': timestamp,
                'name': name,
                'command': command,
                'selection': selection
            }
            
            # Store in queue for real-time display
            self.data_queue.put(message)
            
            # Store in collected_data for summary
            if self.start_time:  # Only collect if started
                self.collected_data.append(message)
                
                # Track login users
                if command == 'login':
                    self.logged_in_users.add(name)
                # Track latest selections
                if selection is not None:
                    self.latest_selections[name] = {
                        'selection': selection,
                        'timestamp': timestamp
                    }

    def start_listening(self):
        """Start the Firebase listener thread"""
        if not self.is_listening:
            self.is_listening = True
            # Initialize Firebase
            if not firebase_admin._apps:
                cred = credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://qi-game-default-rtdb.asia-southeast1.firebasedatabase.app/'
                })
            
            # Start listener in a separate thread
            def listen_loop():
                ref = db.reference('controls')
                self.listener = ref.listen(self.handle_changes)
            
            self.firebase_thread = threading.Thread(target=listen_loop, daemon=True)
            self.firebase_thread.start()

    def stop_listening(self):
        """Stop the Firebase listener"""
        if self.is_listening:
            self.is_listening = False
            if self.listener:
                self.listener.close()
    
    def clear_tracking_data(self):
        """Clear tracking data when starting new collection"""
        self.logged_in_users.clear()
        self.latest_selections.clear()

class FirebaseListenerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Firebase Listener Control")
        self.root.geometry("800x600")
        
        # Initialize Firebase collector
        self.collector = FirebaseDataCollector()
        
        # Start Firebase listener thread immediately
        self.collector.start_listening()
        
        # Initialize variables
        self.is_collecting = False
        
        # Create GUI elements
        self.create_gui()
        
        # Start queue processing
        self.process_queue()

    def create_gui(self):
        """Create the GUI elements"""
        # Control Frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # Start Button
        self.start_button = ttk.Button(
            control_frame,
            text="Start Data Collection",
            command=self.start_collection
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop Button
        self.stop_button = ttk.Button(
            control_frame,
            text="Stop Data Collection",
            command=self.stop_collection,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Get Login Users Button
        self.login_button = ttk.Button(
            control_frame,
            text="Get Login Users",
            command=self.show_login_users,
            state=tk.DISABLED
        )
        self.login_button.pack(side=tk.LEFT, padx=5)

        # Status Label
        self.status_label = ttk.Label(
            control_frame,
            text="Status: Not Collecting"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)

        # Create Text Area
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=80,
            height=30
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def process_queue(self):
        """Process the queue of incoming messages"""
        try:
            while True:
                message = self.collector.data_queue.get_nowait()
                if self.is_collecting:  # Only display if collecting
                    display_text = f"[{message['timestamp']}] {message['name']}: {message['command']}"
                    if message['selection'] is not None:
                        display_text += f" (Selection: {message['selection']})"
                    self.text_area.insert(tk.END, display_text + "\n")
                    self.text_area.see(tk.END)
        except:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def start_collection(self):
        """Start collecting and displaying data"""
        self.is_collecting = True
        self.collector.start_time = datetime.now()
        self.collector.collected_data = []  # Reset collected data
        self.collector.clear_tracking_data()  # Clear tracking data
        
        # Update GUI
        self.text_area.delete(1.0, tk.END)
        self.status_label.config(text="Status: Collecting")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.login_button.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_area.insert(tk.END, f"[{timestamp}] Started collecting data...\n")

    def stop_collection(self):
        """Stop collecting data and display summary"""
        if self.is_collecting:
            self.is_collecting = False
            
            # Update GUI
            self.status_label.config(text="Status: Not Collecting")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.login_button.config(state=tk.DISABLED)
            
            # Display summary
            self.display_summary()

    def show_login_users(self):
        """Display all users who logged in during collection period"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"\n[{timestamp}] === LOGGED IN USERS ===\n"
        
        if not self.collector.logged_in_users:
            summary += "No users logged in during this session.\n"
        else:
            summary += "Users who logged in:\n"
            for user in sorted(self.collector.logged_in_users):
                summary += f"- {user}\n"
        
        self.text_area.insert(tk.END, summary)
        self.text_area.see(tk.END)

    def display_summary(self):
        """Display summary of collected data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"\n[{timestamp}] === COLLECTION STOPPED ===\n"
        summary += f"Collection period: {self.collector.start_time.strftime('%Y-%m-%d %H:%M:%S')} to {timestamp}\n"
        summary += f"Total events collected: {len(self.collector.collected_data)}\n"
        summary += f"Total unique users logged in: {len(self.collector.logged_in_users)}\n\n"
        
        # Display last selections for all users
        summary += "=== LAST SELECTIONS ===\n"
        if not self.collector.latest_selections:
            summary += "No selections recorded during this session.\n"
        else:
            for user in sorted(self.collector.latest_selections.keys()):
                selection_data = self.collector.latest_selections[user]
                summary += f"- {user}: {selection_data['selection']} (at {selection_data['timestamp']})\n"
        
        # Display last action for each user
        summary += "\n=== LAST ACTIONS ===\n"
        if not self.collector.collected_data:
            summary += "No actions recorded during this session.\n"
        else:
            # Group by user and get last action only
            user_last_actions = {}
            for data in self.collector.collected_data:
                user_last_actions[data['name']] = data
            
            # Display last action for each user
            for name in sorted(user_last_actions.keys()):
                action = user_last_actions[name]
                action_text = f"- {name}: [{action['timestamp']}] {action['command']}"
                if action['selection'] is not None:
                    action_text += f" (Selection: {action['selection']})"
                summary += action_text + "\n"
        
        self.text_area.insert(tk.END, summary)
        self.text_area.see(tk.END)

    def on_closing(self):
        """Handle window closing"""
        self.collector.stop_listening()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FirebaseListenerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
