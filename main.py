import pygame
import json

# Load quiz data from JSON file
def load_quiz(filename):
    with open(filename, 'r') as f:
        return json.load(f)

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("QI-game")
font = pygame.font.Font("thai.ttf", 24)


COUNTDOWN_TIME = 5000  # 5 seconds in milliseconds


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
    
    def draw(self, screen):
        # Check if the mouse is over the button
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw the text in the button
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event):
        # Check if the button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# Display a question and choice buttons on the screen
def display_question(question_data, screen, font, buttons, time_left):
    screen.fill(WHITE)
    question_text = font.render(question_data['question'], True, BLACK)
    screen.blit(question_text, (50, 50))
    
    # Draw buttons for each choice
    for button in buttons:
        button.draw(screen)
    
    # Draw the countdown progress bar
    bar_width = 700 * (time_left / COUNTDOWN_TIME)
    pygame.draw.rect(screen, GREEN, (50, 500, bar_width, 20))

# Display feedback for correct and incorrect answers
def display_feedback(is_correct, correct_answer):
    screen.fill(WHITE)
    if is_correct:
        feedback_text = font.render("Correct!", True, GREEN)
    else:
        feedback_text = font.render(f"Wrong! Correct answer: {correct_answer}", True, RED)
    
    screen.blit(feedback_text, (WIDTH // 2 - 150, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(2000)  # Pause for 2 seconds before proceeding

# Display the timeout screen
def display_timeout():
    screen.fill(WHITE)
    timeout_text = font.render("Time's up!", True, RED)
    screen.blit(timeout_text, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(2000)  # Pause for 2 seconds before proceeding




def quiz_game():
    quiz_data = load_quiz('quiz.json')
    running = True
    question_index = 0
    score = 0

    while running:
        question = quiz_data['quiz'][question_index]
        start_time = pygame.time.get_ticks()  # Start time for the countdown

        # Create buttons for each choice
        buttons = []
        for i, choice in enumerate(question['choices']):
            button = Button(50, 150 + i * 70, 700, 50, f"{choice}", BLUE, LIGHT_BLUE, font)
            buttons.append(button)

        answered = False

        while not answered and running:
            # Calculate the time left
            current_time = pygame.time.get_ticks()
            time_left = COUNTDOWN_TIME - (current_time - start_time)
            
            if time_left <= 0:
                display_timeout()  # Show timeout screen
                question_index += 1  # Move to next question
                if question_index >= len(quiz_data['quiz']):
                    running = False
                break

            display_question(question, screen, font, buttons, time_left)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Check for button clicks
                for i, button in enumerate(buttons):
                    if button.is_clicked(event):
                        selected_choice = question['choices'][i]
                        if selected_choice == question['answer']:
                            print("Correct!")
                            display_feedback(True, question['answer'])
                            score += 1
                        else:
                            print(f"Wrong! The correct answer is: {question['answer']}")
                            display_feedback(False, question['answer'])
                        
                        answered = True  # The user answered the question
                        question_index += 1
                        if question_index >= len(quiz_data['quiz']):
                            running = False
                        break

            pygame.display.flip()

    print(f"Final Score: {score}/{len(quiz_data['quiz'])}")
    pygame.quit()

if __name__ == '__main__':
    from welcome import welcome_screen
    welcome_screen()  # Show the welcome screen first
    quiz_game()  # Then start the quiz after the user clicks "Start Quiz"
