import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://qi-game-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Store the current user name
current_user = None

# Function to handle incoming data from Firebase
def listen_for_changes(event):
    global current_user
    if event.data:
        data = event.data
        name = data.get('name', 'Unknown')
        command = data.get('command', 'None')
        
        if command == 'login':
            current_user = name
            print(f"New user logged in: {name}")
        else:
            print(f"{name} pressed {command}")

# Set Firebase listener for real-time updates
control_ref = db.reference('controls')
control_ref.listen(listen_for_changes)

# Keep the script running
if __name__ == "__main__":
    while True:
        pass  # Keep the script running to continue listening for Firebase events