import pygame
import math
import random
import sys
from setting import show_popup
from main import *
from PyQt5.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QDialog, QTextEdit, QPushButton, QFileDialog

WIDTH = 1400
HEIGHT = 800

class Snowflake:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-50, 0)
        self.speed = random.uniform(1, 3)
        self.size = random.uniform(2, 4)
        self.swing = random.uniform(-1, 1)
        self.swing_speed = random.uniform(0.01, 0.03)
        self.angle = 0

    def update(self):
        self.y += self.speed
        self.angle += self.swing_speed
        self.x += math.sin(self.angle) * self.swing
        
        if self.y > HEIGHT:
            self.y = random.randint(-50, 0)
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255, 100), (int(self.x), int(self.y)), self.size)

class ModernButton:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.x = x
        self.y = y
        self.original_y = y
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
        for i in range(3):
            self.current_color = tuple(
                c1 + (c2 - c1) * 0.1
                for c1, c2 in zip(self.current_color, target_color)
            )
        
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover_offset = min(self.hover_offset + 0.5, 5)
            self.glow_radius = min(self.glow_radius + 1, 20)
        else:
            self.hover_offset = max(self.hover_offset - 0.5, 0)
            self.glow_radius = max(self.glow_radius - 1, 0)
        
        self.y = self.original_y - self.hover_offset
        self.rect.y = self.y

    def draw(self, screen):
        if self.glow_radius > 0:
            for i in range(int(self.glow_radius)):
                alpha = int(100 * (1 - i/self.glow_radius))
                glow_surface = pygame.Surface((self.width + i*2, self.height + i*2), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*self.current_color, alpha), 
                               (0, 0, self.width + i*2, self.height + i*2), 
                               border_radius=15)
                screen.blit(glow_surface, 
                          (self.x - i, self.y - i))

        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=12, width=2)

        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_surf_shadow = self.font.render(self.text, True, (50, 50, 50))
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surf_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos())

def welcome_screen():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    
    # Initialize fonts
    font = pygame.font.Font(None, 64)
    title_font = pygame.font.Font(None, 120)
    
    # Initialize snowflakes
    snowflakes = [Snowflake() for _ in range(100)]
    
    try:
        background_image = pygame.image.load('assets/mygame.png')
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"Couldn't load background image: {e}")
        background_image = None
    
    start_button = ModernButton(
        WIDTH // 2 - 100,
        HEIGHT // 2 + 40,
        200,
        50,
        "Start",
        (41, 128, 185),
        (52, 152, 219),
        font
    )

    # Title animation variables
    title_offset = 0
    title_direction = 1
    title_speed = 0.5
    title_max_offset = 20
    
    # Mint color for title (RGB)
    MINT_COLOR = (98, 223, 181)  # Adjust these values to get your preferred shade of mint
    
    while running:
        # Draw background
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((20, 24, 35))
        
        # Update and draw snowflakes
        for snowflake in snowflakes:
            snowflake.update()
            snowflake.draw(screen)
        
        # Update title animation
        title_offset += title_direction * title_speed
        if abs(title_offset) > title_max_offset:
            title_direction *= -1
        
        # Draw title with shadow
        title_text = "Quiz Intelligence"
        shadow_offset = 3
        
        # Draw shadow
        title_shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = title_shadow.get_rect(center=(WIDTH//2 + shadow_offset, 
                                                  HEIGHT//3 + title_offset + shadow_offset))
        screen.blit(title_shadow, shadow_rect)
        
        # Draw main title in mint color
        title_surface = title_font.render(title_text, True, MINT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH//2, HEIGHT//3 + title_offset))
        screen.blit(title_surface, title_rect)
        
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