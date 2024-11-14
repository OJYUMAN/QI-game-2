# firebase_manager.py
import firebase_admin
from firebase_admin import credentials, db

class FirebaseManager:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase-credentials.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://qi-game-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        
        self.players = {}
        self.control_ref = db.reference('controls')
        self.game_ref = db.reference('game')
        self.setup_listeners()
    
    def setup_listeners(self):
        def control_handler(event):
            if event.data:
                data = event.data
                name = data.get('name', 'Unknown')
                command = data.get('command', 'None')
                
                if command == 'login':
                    self.players[name] = {'score': 0, 'answer': None}
                    print(f"New user logged in: {name}")
                elif command in ['1', '2', '3', '4']:
                    if name in self.players:
                        self.players[name]['answer'] = int(command) - 1
                        print(f"{name} pressed {command}")
        
        self.control_ref.listen(control_handler)
    
    def update_game_state(self, question_data):
        self.game_ref.update({
            'current_question': question_data['question'],
            'choices': question_data['choices'],
            'status': 'waiting'
        })
    
    def reset_answers(self):
        for player in self.players.values():
            player['answer'] = None
    
    def get_players(self):
        return self.players.copy()

    def cleanup(self):
        # Reset game state when finished
        self.game_ref.update({
            'status': 'finished',
            'current_question': None,
            'choices': None
        })