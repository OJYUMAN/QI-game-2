# quiz_game.py
import pygame
import json
import math
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
        self.animation_progress = 0
        self.animation_speed = 0.05
        
        # Load background image
        self.background = pygame.image.load('631.png')  # Make sure this file exists
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        
        # Colors
        self.BLUE = (37, 58, 177)
        self.WHITE = (255, 255, 255)
        self.NAVY = (20, 29, 89)
        
    def load_quiz(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
            
    def animate_score(self, start_pos, end_pos, progress):
        x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        if progress > 0.8:
            y += math.sin((progress - 0.8) * math.pi * 5) * 10
        return (x, y)
            
    def display_question(self, question, time_left, players):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Header
        pygame.draw.rect(self.screen, self.WHITE, (WIDTH//2 - 300, 20, 600, 60), border_radius=10)
        question_text = self.font.render(question['question'], True, (0, 0, 0))
        question_rect = question_text.get_rect(center=(WIDTH//2, 50))
        self.screen.blit(question_text, question_rect)
        
        # Grid layout for choices (2x2)
        button_width = (WIDTH - 150) // 2
        button_height = 120
        grid_positions = [
            (50, 200),                    # Top left
            (75 + button_width, 200),     # Top right
            (50, 200 + button_height + 25), # Bottom left
            (75 + button_width, 200 + button_height + 25)  # Bottom right
        ]
        
        for i, choice in enumerate(question['choices']):
            button = ModernButton(
                grid_positions[i][0], grid_positions[i][1],
                button_width, button_height,
                choice, CHOICE_COLORS[i], CHOICE_HOVER_COLORS[i],
                self.font, i + 1
            )
            button.draw(self.screen)
        
        # Game info
        timer_text = self.small_font.render(f"Time: {time_left//1000}s", True, self.WHITE)
        players_text = self.small_font.render(f"Players: {len(players)}", True, self.WHITE)
        answered_count = sum(1 for p in players.values() if p['answer'] is not None)
        status_text = self.small_font.render(
            f"Answered: {answered_count}/{len(players)}", 
            True, 
            self.WHITE
        )
        
        self.screen.blit(timer_text, (10, 10))
        self.screen.blit(players_text, (WIDTH - 150, 10))
        self.screen.blit(status_text, (WIDTH//2 - 50, 120))
        
        pygame.display.flip()
    
    def display_results(self, players):
        clock = pygame.time.Clock()
        self.animation_progress = 0
        
        while self.animation_progress < 1:
            self.screen.blit(self.background, (0, 0))
            
            # Header
            pygame.draw.rect(self.screen, self.WHITE, (WIDTH//2 - 100, 20, 200, 50), border_radius=10)
            title = self.font.render("Scoreboard", True, (0, 0, 0))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
            
            # Sort and display players
            sorted_players = sorted(
                players.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            y_start = 120
            for i, (name, data) in enumerate(sorted_players):
                start_pos = (-300, y_start + i * 80)
                end_pos = (WIDTH//2 - 200, y_start + i * 80)
                current_pos = self.animate_score(start_pos, end_pos, self.animation_progress)
                
                # Player card
                bg_color = self.WHITE if i == 0 else self.NAVY
                pygame.draw.rect(self.screen, bg_color, 
                               (current_pos[0], current_pos[1], 400, 60), 
                               border_radius=10)
                
                # Player info
                text_color = (0, 0, 0) if i == 0 else self.WHITE
                name_text = self.font.render(name, True, text_color)
                score_text = self.font.render(str(data['score']), True, text_color)
                
                self.screen.blit(name_text, (current_pos[0] + 20, current_pos[1] + 15))
                self.screen.blit(score_text, (current_pos[0] + 300, current_pos[1] + 15))
                
                # Leading indicator
                if i < len(sorted_players) - 1 and data['score'] > sorted_players[i + 1][1]['score']:
                    arrow = self.font.render("▲", True, text_color)
                    self.screen.blit(arrow, (current_pos[0] + 350, current_pos[1] + 15))
            
            # Progress indicator
            progress_text = self.small_font.render(f"{self.current_question + 1}/{len(self.quiz_data['quiz'])} ▲", True, self.WHITE)
            self.screen.blit(progress_text, (20, HEIGHT - 35))
            
            pygame.display.flip()
            self.animation_progress = min(1, self.animation_progress + self.animation_speed)
            clock.tick(60)
            
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

if __name__ == "__main__":
    quiz_game()