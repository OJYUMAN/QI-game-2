

# quiz_game.py
import pygame
import json
from components import (
    ModernButton, CHOICE_COLORS, CHOICE_HOVER_COLORS,
    WIDTH, HEIGHT, BACKGROUND, init_game_display
)
from firebasecontrol import FirebaseManager
from setting import get_countdown_time

class MultiplayerQuiz:
    def __init__(self):
        self.screen, self.font, self.small_font = init_game_display()
        self.quiz_data = self.load_quiz('quiz.json')
        self.firebase = FirebaseManager()
        self.current_question = 0
        
    def load_quiz(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
            
    def display_question(self, question, time_left, players):
        self.screen.fill(BACKGROUND)
        
        # Question text
        question_text = self.font.render(question['question'], True, CHOICE_COLORS[0])
        question_rect = question_text.get_rect(center=(WIDTH//2, 100))
        self.screen.blit(question_text, question_rect)
        
        # Choices
        for i, choice in enumerate(question['choices']):
            button = ModernButton(
                50, 200 + i * 70, WIDTH - 100, 60,
                choice, CHOICE_COLORS[i], CHOICE_HOVER_COLORS[i],
                self.font, i + 1
            )
            button.draw(self.screen)
        
        # Timer and player count
        timer_text = self.small_font.render(f"Time: {time_left//1000}s", True, CHOICE_COLORS[0])
        players_text = self.small_font.render(f"Players: {len(players)}", True, CHOICE_COLORS[0])
        
        # Player answers status
        answered_count = sum(1 for p in players.values() if p['answer'] is not None)
        status_text = self.small_font.render(
            f"Answered: {answered_count}/{len(players)}", 
            True, 
            CHOICE_COLORS[0]
        )
        
        self.screen.blit(timer_text, (10, 10))
        self.screen.blit(players_text, (WIDTH - 150, 10))
        self.screen.blit(status_text, (WIDTH//2 - 50, 40))
        
        pygame.display.flip()
    
    def display_results(self, players):
        self.screen.fill(BACKGROUND)
        
        # Sort players by score
        sorted_players = sorted(
            players.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        title_text = self.font.render("Current Standings", True, CHOICE_COLORS[0])
        title_rect = title_text.get_rect(center=(WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        y_pos = 150
        for name, data in sorted_players:
            score_text = self.small_font.render(
                f"{name}: {data['score']} points", 
                True, 
                CHOICE_COLORS[0]
            )
            score_rect = score_text.get_rect(center=(WIDTH//2, y_pos))
            self.screen.blit(score_text, score_rect)
            y_pos += 40
        
        pygame.display.flip()
        pygame.time.wait(2000)
    
    def update_scores(self, players, correct_answer_index):
        for player_data in players.values():
            if player_data['answer'] == correct_answer_index:
                player_data['score'] += 1
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running and self.current_question < len(self.quiz_data['quiz']):
            question = self.quiz_data['quiz'][self.current_question]
            self.firebase.update_game_state(question)
            self.firebase.reset_answers()
            
            start_time = pygame.time.get_ticks()
            countdown = get_countdown_time()
            
            while running:
                clock.tick(60)
                current_time = pygame.time.get_ticks()
                time_left = countdown - (current_time - start_time)
                
                if time_left <= 0:
                    break
                
                current_players = self.firebase.get_players()
                self.display_question(question, time_left, current_players)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                
                # Check if all players answered
                all_answered = all(
                    p['answer'] is not None 
                    for p in current_players.values()
                )
                if all_answered and len(current_players) > 0:
                    break
            
            if running:
                correct_answer_index = question['choices'].index(question['answer'])
                current_players = self.firebase.get_players()
                self.update_scores(current_players, correct_answer_index)
                self.display_results(current_players)
                self.current_question += 1
        
        self.firebase.game_ref.update({'game_over': True})
        pygame.quit()

def quiz_game():
    game = MultiplayerQuiz()
    game.run()