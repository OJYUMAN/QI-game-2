import pygame
import json
from components import (
    ModernButton, display_question, CHOICE_COLORS, CHOICE_HOVER_COLORS,
    WIDTH, HEIGHT, BACKGROUND, init_game_display
)
from setting import get_countdown_time

def load_quiz(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def display_feedback(screen, font, small_font, is_correct, correct_answer, score, total_questions):
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

def display_timeout(screen, font):
    screen.fill(BACKGROUND)
    timeout_text = font.render("Time's up!", True, (231, 76, 60))
    timeout_rect = timeout_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(timeout_text, timeout_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

def display_final_score(screen, font, small_font, score, total_questions):
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
    screen, font, small_font = init_game_display()
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
                display_timeout(screen, font)
                question_index += 1
                if question_index >= len(quiz_data['quiz']):
                    display_final_score(screen, font, small_font, score, len(quiz_data['quiz']))
                    running = False
                break

            display_question(question, screen, font, small_font, buttons, time_left, 
                           question_index, len(quiz_data['quiz']), current_countdown)
            
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
                            display_feedback(screen, font, small_font, True, question['answer'], 
                                          score, len(quiz_data['quiz']))
                        else:
                            button.wrong = True
                            display_feedback(screen, font, small_font, False, question['answer'], 
                                          score, len(quiz_data['quiz']))
                        
                        answered = True
                        question_index += 1
                        if question_index >= len(quiz_data['quiz']):
                            display_final_score(screen, font, small_font, score, len(quiz_data['quiz']))
                            running = False
                        break

            pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    from welcome import welcome_screen
    welcome_screen()
    quiz_game()