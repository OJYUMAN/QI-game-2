import tkinter as tk
from tkinter import ttk, scrolledtext
import firebase_admin
from firebase_admin import credentials, db
from typing import List, Dict
from datetime import datetime
from queue import Queue
import threading

class FirebaseListenerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Firebase Listener Control")
        self.root.geometry("600x400")
        
        # Initialize variables
        self.listeners: List[db.ListenerRegistration] = []
        self.current_user = None
        self.is_listening = False
        self.data_queue = Queue()
        self.user_last_actions: Dict = {}  # Store last action for each user
        
        # Initialize Firebase
        self.initialize_firebase()
        
        # Create GUI elements
        self.create_gui()
        
        # Start queue processing
        self.process_queue()

    def initialize_firebase(self):
        """Initialize Firebase connection"""
        cred = credentials.Certificate("firebase-credentials.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://qi-game-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

    def create_gui(self):
        """Create the GUI elements"""
        # Control Frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # Start Button
        self.start_button = ttk.Button(
            control_frame, 
            text="Start Listening", 
            command=self.start_listening
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop Button
        self.stop_button = ttk.Button(
            control_frame, 
            text="Stop Listening", 
            command=self.stop_listening,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Status Label
        self.status_label = ttk.Label(
            control_frame, 
            text="Status: Not Listening"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)

        # Create Text Area
        self.text_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            width=60, 
            height=20
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def handle_changes(self, event):
        """Handle incoming Firebase events"""
        if event.data:
            data = event.data
            name = data.get('name', 'Unknown')
            command = data.get('command', 'None')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Store the last action for this user
            self.user_last_actions[name] = {
                'timestamp': timestamp,
                'command': command
            }
            
            if command == 'login':
                message = f"New user logged in: {name}"
            else:
                message = f"{name} pressed {command}"
            
            # Add to queue for display
            self.data_queue.put(f"[{timestamp}] {message}\n")

    def process_queue(self):
        """Process the queue of incoming messages"""
        try:
            while True:
                message = self.data_queue.get_nowait()
                self.text_area.insert(tk.END, message)
                self.text_area.see(tk.END)
        except:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def start_listening(self):
        """Start the Firebase listener"""
        if not self.is_listening:
            self.is_listening = True
            self.text_area.delete(1.0, tk.END)
            self.user_last_actions.clear()
            
            # Create listener
            ref = db.reference('controls')
            listener = ref.listen(self.handle_changes)
            self.listeners.append(listener)
            
            # Update GUI
            self.status_label.config(text="Status: Listening")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Add start message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.text_area.insert(tk.END, f"[{timestamp}] Started listening...\n")

    def stop_listening(self):
        """Stop the Firebase listener and display last actions"""
        if self.is_listening:
            # Stop all listeners
            for listener in self.listeners:
                listener.close()
            self.listeners.clear()
            
            # Update GUI
            self.is_listening = False
            self.status_label.config(text="Status: Not Listening")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Display last actions
            self.display_last_actions()

    def display_last_actions(self):
        """Display last action of each user"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"\n[{timestamp}] === LISTENING STOPPED ===\n"
        summary += "Last Action for Each User:\n"
        
        if not self.user_last_actions:
            summary += "No actions were recorded during this session.\n"
        else:
            # Sort users alphabetically
            for name in sorted(self.user_last_actions.keys()):
                action = self.user_last_actions[name]
                summary += f"User: {name}\n"
                summary += f"  - Last Command: {action['command']}\n"
                summary += f"  - Time: {action['timestamp']}\n"

        self.text_area.insert(tk.END, summary)
        self.text_area.see(tk.END)

def main():
    root = tk.Tk()
    app = FirebaseListenerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()