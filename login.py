import pygame
import sys
import math
from firebasecontrol import FirebaseManager

pygame.init()
font = pygame.font.Font("assets/thai.ttf", 24)


# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1400, 800
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
START_BUTTON_COLOR = (46, 204, 113)  # Nice green color
START_BUTTON_HOVER = (39, 174, 96)   # Darker green for hover

# User box constants
USER_BOX_WIDTH = 150
USER_BOX_HEIGHT = 80
USER_BOX_MARGIN = 20
USERS_PER_ROW = 4

class KahootUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Quiz Game")
        
        self.logged_in_users = []
        
        # Fonts
        self.title_font = pygame.font.SysFont('arial', 48, bold=True)
        self.user_font = pygame.font.SysFont('arial', 24)
        self.count_font = pygame.font.SysFont('arial', 28)
        
        # Load and scale background image
        self.background = pygame.image.load('assets/ok.png')  # You'll need to provide this image
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Load and scale QR code image
        self.qr_code_image = pygame.image.load('assets/qr.png')  # Provide the QR code image here
        qr_code_size = (200, 200)  # Adjust the size of the QR code
        self.qr_code_image = pygame.transform.scale(self.qr_code_image, qr_code_size)
        self.qr_code_position = (20, 20)  # Position the QR code near the top-left corner
        
        # Firebase setup
        self.firebase = FirebaseManager()
        
        # Animation states
        self.animations = {}
        self.animation_duration = 500
        
        # Enhanced start button
        button_width = 200
        button_height = 50
        self.start_button_rect = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            WINDOW_HEIGHT - 100,
            button_width,
            button_height
        )
        self.game_started = False
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.start_button_rect.collidepoint(event.pos):
                        if len(self.logged_in_users) > 0:
                            self.game_started = True
                            return False
        return True

    def draw_start_button(self):
        mouse_pos = pygame.mouse.get_pos()
        button_color = START_BUTTON_HOVER if self.start_button_rect.collidepoint(mouse_pos) else START_BUTTON_COLOR
        
        if len(self.logged_in_users) == 0:
            button_color = GRAY
        
        # Draw button with shadow
        shadow_rect = self.start_button_rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow_rect, border_radius=25)
        pygame.draw.rect(self.screen, button_color, self.start_button_rect, border_radius=25)
        
        # Draw text
        start_text = self.user_font.render("Start Game", True, WHITE)
        text_rect = start_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_text, text_rect)

    def draw_users_grid(self):
        if not self.logged_in_users:
            return

        start_y = 220
        current_time = pygame.time.get_ticks()
        total_users = len(self.logged_in_users)
        rows = math.ceil(total_users / USERS_PER_ROW)

        for idx, user in enumerate(self.logged_in_users):
            row = idx // USERS_PER_ROW
            col = idx % USERS_PER_ROW
            
            base_x = (WINDOW_WIDTH - (USERS_PER_ROW * (USER_BOX_WIDTH + USER_BOX_MARGIN))) // 2
            x = base_x + col * (USER_BOX_WIDTH + USER_BOX_MARGIN)
            y = start_y + row * (USER_BOX_HEIGHT + USER_BOX_MARGIN)

            if user not in self.animations:
                self.animations[user] = {
                    'start_time': current_time,
                    'scale': 0.0
                }

            animation = self.animations[user]
            scale = animation['scale'] = min(1.0, animation['scale'] + 0.1)

            scaled_width = USER_BOX_WIDTH * scale
            scaled_height = USER_BOX_HEIGHT * scale
            x_offset = (USER_BOX_WIDTH - scaled_width) / 2
            y_offset = (USER_BOX_HEIGHT - scaled_height) / 2

            # Draw user box with shadow
            shadow_rect = pygame.Rect(
                x + x_offset,
                y + y_offset + 4,
                scaled_width,
                scaled_height
            )
            pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow_rect, border_radius=10)
            
            user_box_rect = pygame.Rect(
                x + x_offset,
                y + y_offset,
                scaled_width,
                scaled_height
            )
            pygame.draw.rect(self.screen, WHITE, user_box_rect, border_radius=10)

            if scale > 0.5:
                user_text = self.user_font.render(user, True, (50, 50, 50))
                text_rect = user_text.get_rect(center=user_box_rect.center)
                self.screen.blit(user_text, text_rect)

    def draw_player_count(self):
        count_text = self.count_font.render(
            f"Players: {len(self.logged_in_users)}", 
            True, 
            WHITE
        )
        count_rect = count_text.get_rect(center=(WINDOW_WIDTH//2, 180))
        self.screen.blit(count_text, count_rect)

    def draw(self):
        # Draw background image
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        logo_text = self.title_font.render("Quiz intelligence", True, WHITE)
        logo_rect = logo_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(logo_text, logo_rect)
        
        # Draw QR code image on the left
        self.screen.blit(self.qr_code_image, self.qr_code_position)
        
        # Update and draw other elements
        self.update_players()
        self.draw_start_button()
        self.draw_player_count()
        self.draw_users_grid()
        
        pygame.display.flip()

    def update_players(self):
        current_players = self.firebase.get_players()
        for player_name in current_players:
            if player_name not in self.logged_in_users:
                self.logged_in_users.append(player_name)
                self.animations[player_name] = {
                    'start_time': pygame.time.get_ticks(),
                    'scale': 0.0
                }

def run_login():
    clock = pygame.time.Clock()
    ui = KahootUI()
    
    while True:
        if not ui.handle_events():
            break
        ui.draw()
        clock.tick(60)
    
    return ui.game_started, ui.firebase, ui.logged_in_users