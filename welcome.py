import pygame
import math
import random
from setting import show_popup
from main import *
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QDialog, QTextEdit, QPushButton, QFileDialog

# Updated screen dimensions
WIDTH = 1400
HEIGHT = 800

class ModernButton:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.x = x
        self.y = y
        self.original_y = y  # Store original y position for hover animation
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = font
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hover_offset = 0
        self.alpha = 255
        self.glow_radius = 0

    def update(self):
        target_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        # Smooth color transition
        for i in range(3):
            self.current_color = tuple(
                c1 + (c2 - c1) * 0.1
                for c1, c2 in zip(self.current_color, target_color)
            )
        
        # Hover animation
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover_offset = min(self.hover_offset + 0.5, 5)
            self.glow_radius = min(self.glow_radius + 1, 20)
        else:
            self.hover_offset = max(self.hover_offset - 0.5, 0)
            self.glow_radius = max(self.glow_radius - 1, 0)
        
        self.y = self.original_y - self.hover_offset
        self.rect.y = self.y

    def draw(self, screen):
        # Draw glow effect
        if self.glow_radius > 0:
            for i in range(int(self.glow_radius)):
                alpha = int(100 * (1 - i/self.glow_radius))
                glow_surface = pygame.Surface((self.width + i*2, self.height + i*2), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*self.current_color, alpha), 
                               (0, 0, self.width + i*2, self.height + i*2), 
                               border_radius=15)
                screen.blit(glow_surface, 
                          (self.x - i, self.y - i))

        # Draw main button
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=12, width=2)

        # Draw text with shadow
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_surf_shadow = self.font.render(self.text, True, (50, 50, 50))
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surf_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False

def welcome_screen():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    
    # Initialize font
    font = pygame.font.Font(None, 64)  # Default font with size 64
    
    # Load and scale background image
    try:
        background_image = pygame.image.load('background.jpg')  # Replace with your image path
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"Couldn't load background image: {e}")
        background_image = None
    
    # Create modern button
    start_button = ModernButton(
        WIDTH // 2 - 100,
        HEIGHT // 2 + 300,
        200,
        50,
        "Start Quiz",
        (41, 128, 185),  # Default color
        (52, 152, 219),  # Hover color
        font
    )

    # Animation variables
    title_offset = 0
    title_direction = 1
    alpha = 0
    
    while running:
        # Draw background
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            # Fallback to original background color if image fails to load
            screen.fill((20, 24, 35))
        
       
    
        
        # Update and draw button
        start_button.update()
        start_button.draw(screen)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if start_button.is_clicked(event):
                show_popup()
                running = False
        
        pygame.display.flip()
        clock.tick(60)

