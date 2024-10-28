import pygame
from setting import show_popup
from main import *
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QDialog, QTextEdit, QPushButton, QFileDialog

# New button class with hover effects and shadows
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font, shadow=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.shadow = shadow
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        # Draw shadow
        if self.shadow:
            shadow_offset = 5
            pygame.draw.rect(screen, (50, 50, 50), (self.x + shadow_offset, self.y + shadow_offset, self.width, self.height))

        # Change color on hover
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=12)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=12)

        # Render text
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False

def welcome_screen():
    running = True
    start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "Start Quiz", (0, 102, 255), (0, 153, 255), font)

    # Set background color to black
    screen.fill((0, 0, 0))  # Black background

    while running:
        # Render welcome text with improved style
        welcome_text = font.render("Welcome to QI-game (Quiz Intelligence)", True, (255, 255, 255))  # White color for main text
        welcome_text_shadow = font.render("Welcome to QI-game (Quiz Intelligence)", True, (100, 100, 100))  # Gray shadow
        
        # Center the welcome text
        welcome_text_rect = welcome_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        welcome_text_shadow_rect = welcome_text_shadow.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))  # Shadow position

        # Blit the shadow and main text
        screen.blit(welcome_text_shadow, welcome_text_shadow_rect)  # Blit shadow first
        screen.blit(welcome_text, welcome_text_rect)  # Blit the main text

        start_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if start_button.is_clicked(event):
                show_popup()  # Show the popup when the button is clicked
                running = False  # Stop the loop by setting running to False

        pygame.display.flip()

