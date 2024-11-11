import pygame
import json
import math
from setting import *

def load_quiz(filename):
    with open(filename, 'r') as f:
        return json.load(f)

pygame.init()

# color palette
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BACKGROUND = (236, 240, 241)
GRAY = (149, 165, 166)
themecolor = (40,40,40)

CHOICE_COLORS = [
    (226, 27, 60),   # Red
    (19, 104, 206),  # Blue
    (216, 158, 0),   # Yellow
    (38, 137, 12)    # Green
]

CHOICE_HOVER_COLORS = [
    (255, 66, 95),   # Light Red
    (48, 144, 255),  # Light Blue
    (255, 194, 26),  # Light Yellow
    (76, 175, 49)    # Light Green
]

# Screen settings
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("QI-game")
font = pygame.font.Font("thai.ttf", 24)
small_font = pygame.font.Font("thai.ttf", 18)

class ModernButton:
    def __init__(self, x, y, width, height, text, color, hover_color, font, number):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = font
        self.alpha = 255
        self.hover_offset = 0
        self.original_y = y
        self.animation_progress = 0
        self.selected = False
        self.correct = False
        self.wrong = False
        self.number = number
    
    def update(self):
        # Smooth color transition
        target_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        self.current_color = tuple(
            c1 + (c2 - c1) * 0.1
            for c1, c2 in zip(self.current_color, target_color)
        )
        
        # Hover animation
        if self.rect.collidepoint(pygame.mouse.get_pos()) and not self.selected:
            self.hover_offset = min(self.hover_offset + 0.5, 5)
        else:
            self.hover_offset = max(self.hover_offset - 0.5, 0)
        
        self.rect.y = self.original_y - self.hover_offset
        
        # Entrance animation
        if self.animation_progress < 1:
            self.animation_progress += 0.05
            self.alpha = int(255 * self.animation_progress)
    
    def draw(self, screen):
        # Draw shadow
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 30), 
                        (0, 5, self.rect.width, self.rect.height),
                        border_radius=10)
        screen.blit(shadow_surface, (self.rect.x, self.rect.y))
        
        # Draw button background with alpha
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.selected:
            if self.correct:
                color = (46, 204, 113, self.alpha)  # Green
            elif self.wrong:
                color = (231, 76, 60, self.alpha)   # Red
            else:
                color = (*self.current_color, self.alpha)
        else:
            color = (*self.current_color, self.alpha)
        
        pygame.draw.rect(button_surface, color, 
                        (0, 0, self.rect.width, self.rect.height),
                        border_radius=10)
        
        # Add subtle gradient
        gradient = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient, (255, 255, 255, 30), 
                        (0, 0, self.rect.width, self.rect.height//2),
                        border_radius=10)
        button_surface.blit(gradient, (0, 0))
        
        screen.blit(button_surface, self.rect)
        
        # Draw number and text
        number_text = self.font.render(f"{self.number}. ", True, WHITE)
        text_surface = self.font.render(self.text, True, WHITE)
        
        # Calculate positions
        number_rect = number_text.get_rect(midleft=(self.rect.x + 20, self.rect.centery))
        text_rect = text_surface.get_rect(midleft=(number_rect.right + 10, self.rect.centery))
        
        # Draw text shadows
        screen.blit(self.font.render(f"{self.number}. ", True, (0, 0, 0, 100)), 
                   (number_rect.x + 2, number_rect.y + 2))
        screen.blit(self.font.render(self.text, True, (0, 0, 0, 100)), 
                   (text_rect.x + 2, text_rect.y + 2))
        
        # Draw actual text
        screen.blit(number_text, number_rect)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.rect.collidepoint(event.pos))

def draw_progress_bar(screen, progress, total, x, y, width, height):
    # Background
    pygame.draw.rect(screen, GRAY, (x, y, width, height), border_radius=height//2)
    
    # Progress
    progress_width = (width * progress) // total
    if progress_width > 0:
        pygame.draw.rect(screen, themecolor, 
                        (x, y, progress_width, height),
                        border_radius=height//2)

def draw_timer(screen, time_left, total_time):
    angle = (time_left / total_time) * 360
    center = (WIDTH - 50, 50)
    radius = 30
    
    pygame.draw.circle(screen, GRAY, center, radius)
    
    if angle > 0:
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.arc(surface, themecolor, 
                       (0, 0, radius * 2, radius * 2),
                       -90 * (math.pi / 180),
                       (angle - 90) * (math.pi / 180),
                       radius)
        screen.blit(surface, (center[0] - radius, center[1] - radius))
    
    pygame.draw.circle(screen, WHITE, center, radius - 5)
    
    time_text = small_font.render(f"{int(time_left/1000)}", True, BLACK)
    time_rect = time_text.get_rect(center=center)
    screen.blit(time_text, time_rect)

def display_question(question_data, screen, font, buttons, time_left, question_number, total_questions):
    screen.fill(BACKGROUND)
    
    progress_text = small_font.render(f"Question {question_number + 1}/{total_questions}", True, GRAY)
    screen.blit(progress_text, (50, 20))
    
    draw_progress_bar(screen, question_number + 1, total_questions, 50, 50, WIDTH - 200, 10)
    
    current_countdown = get_countdown_time()
    draw_timer(screen, time_left, current_countdown)
    
    words = question_data['question'].split()
    lines = []
    current_line = words[0]
    for word in words[1:]:
        if font.size(current_line + " " + word)[0] <= WIDTH - 100:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    
    for i, line in enumerate(lines):
        question_text = font.render(line, True, BLACK)
        screen.blit(question_text, (50, 100 + i * 30))
    
    for button in buttons:
        button.update()
        button.draw(screen)

def display_feedback(is_correct, correct_answer, score, total_questions):
    screen.fill(BACKGROUND)
    
    if is_correct:
        message = "Correct!"
        color = CHOICE_COLORS[2]  # Green
    else:
        message = f"Wrong! Correct answer: {correct_answer}"
        color = (231, 76, 60)  # Red
    
    feedback_text = font.render(message, True, color)
    feedback_rect = feedback_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    score_text = small_font.render(f"Score: {score}/{total_questions}", True, CHOICE_COLORS[0])
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    
    screen.blit(feedback_text, feedback_rect)
    screen.blit(score_text, score_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

def display_timeout():
    screen.fill(BACKGROUND)
    timeout_text = font.render("Time's up!", True, (231, 76, 60))
    timeout_rect = timeout_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(timeout_text, timeout_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

def display_final_score(score, total_questions):
    screen.fill(BACKGROUND)
    
    percentage = (score / total_questions) * 100
    
    score_text = font.render(f"Final Score: {score}/{total_questions}", True, CHOICE_COLORS[0])
    percentage_text = font.render(f"{percentage:.1f}%", True, CHOICE_COLORS[0])
    
    if percentage >= 80:
        message = "Excellent work!"
        color = CHOICE_COLORS[2]  # Green
    elif percentage >= 60:
        message = "Good job!"
        color = CHOICE_COLORS[0]  # Blue
    else:
        message = "Keep practicing!"
        color = (231, 76, 60)  # Red
    
    message_text = font.render(message, True, color)
    
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    percentage_rect = percentage_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    message_rect = message_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    
    screen.blit(score_text, score_rect)
    screen.blit(percentage_text, percentage_rect)
    screen.blit(message_text, message_rect)
    pygame.display.flip()
    pygame.time.wait(3000)

def quiz_game():
    quiz_data = load_quiz('quiz.json')
    clock = pygame.time.Clock()
    running = True
    question_index = 0
    score = 0

    while running:
        question = quiz_data['quiz'][question_index]
        start_time = pygame.time.get_ticks()
        current_countdown = get_countdown_time()

        buttons = []
        for i, choice in enumerate(question['choices']):
            button = ModernButton(
                50, 200 + i * 70, WIDTH - 100, 60,
                choice, CHOICE_COLORS[i], CHOICE_HOVER_COLORS[i],
                font, i + 1
            )
            buttons.append(button)

        answered = False

        while not answered and running:
            clock.tick(60)
            
            current_time = pygame.time.get_ticks()
            time_left = current_countdown - (current_time - start_time)
            
            if time_left <= 0:
                display_timeout()
                question_index += 1
                if question_index >= len(quiz_data['quiz']):
                    display_final_score(score, len(quiz_data['quiz']))
                    running = False
                break

            display_question(question, screen, font, buttons, time_left, 
                           question_index, len(quiz_data['quiz']))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                for i, button in enumerate(buttons):
                    if button.is_clicked(event):
                        button.selected = True
                        selected_choice = question['choices'][i]
                        
                        if selected_choice == question['answer']:
                            button.correct = True
                            score += 1
                            display_feedback(True, question['answer'], 
                                          score, len(quiz_data['quiz']))
                        else:
                            button.wrong = True
                            display_feedback(False, question['answer'], 
                                          score, len(quiz_data['quiz']))
                        
                        answered = True
                        question_index += 1
                        if question_index >= len(quiz_data['quiz']):
                            display_final_score(score, len(quiz_data['quiz']))
                            running = False
                        break

            pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    from welcome import welcome_screen
    welcome_screen()
    quiz_game()