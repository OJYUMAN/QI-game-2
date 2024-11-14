# login_page.py
import pygame
import sys
import math

from firebasecontrol import FirebaseManager

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1400, 800
KAHOOT_BLUE = (46, 49, 146)
KAHOOT_PURPLE = (114, 88, 214)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

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
        self.game_pin = "625 250"
        
        # Fonts
        self.title_font = pygame.font.SysFont('arial', 48, bold=True)
        self.pin_font = pygame.font.SysFont('arial', 36)
        self.user_font = pygame.font.SysFont('arial', 24)
        self.count_font = pygame.font.SysFont('arial', 28)
        
        # Create gradient background
        self.gradient_surface = self.create_gradient()
        
        # Firebase setup
        self.firebase = FirebaseManager()
        
        # Animation states
        self.animations = {}
        self.animation_duration = 500
        
        # UI elements
        self.quit_button_rect = pygame.Rect(WINDOW_WIDTH - 120, 20, 100, 40)
        self.game_started = False

    def create_gradient(self):
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            factor = y / WINDOW_HEIGHT
            color = (
                int(KAHOOT_BLUE[0] * (1 - factor) + KAHOOT_PURPLE[0] * factor),
                int(KAHOOT_BLUE[1] * (1 - factor) + KAHOOT_PURPLE[1] * factor),
                int(KAHOOT_BLUE[2] * (1 - factor) + KAHOOT_PURPLE[2] * factor)
            )
            pygame.draw.line(surface, color, (0, y), (WINDOW_WIDTH, y))
        return surface

    def update_players(self):
        # Update logged in users from Firebase
        current_players = self.firebase.get_players()
        for player_name in current_players:
            if player_name not in self.logged_in_users:
                self.logged_in_users.append(player_name)
                self.animations[player_name] = {
                    'start_time': pygame.time.get_ticks(),
                    'scale': 0.0
                }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if self.quit_button_rect.collidepoint(mouse_pos):
                        if len(self.logged_in_users) > 0:  # Only start if there are players
                            self.game_started = True
                            return False
        return True

    def draw_start_button(self):
        button_color = (200, 0, 0) if len(self.logged_in_users) > 0 else GRAY
        hover_color = (255, 0, 0) if len(self.logged_in_users) > 0 else GRAY

        mouse_pos = pygame.mouse.get_pos()
        color = hover_color if self.quit_button_rect.collidepoint(mouse_pos) else button_color

        pygame.draw.rect(self.screen, color, self.quit_button_rect, border_radius=5)
        quit_text = self.user_font.render("Start", True, WHITE)
        text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        self.screen.blit(quit_text, text_rect)

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

            # Animation handling
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

            user_box_rect = pygame.Rect(
                x + x_offset, 
                y + y_offset, 
                scaled_width, 
                scaled_height
            )
            pygame.draw.rect(self.screen, WHITE, user_box_rect, border_radius=10)

            if scale > 0.5:
                user_text = self.user_font.render(user, True, KAHOOT_BLUE)
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
        # Draw background
        self.screen.blit(self.gradient_surface, (0, 0))
        
        # Draw title
        logo_text = self.title_font.render("Quiz intelligence", True, WHITE)
        logo_rect = logo_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(logo_text, logo_rect)
        
        # Draw subtitle
        work_text = self.user_font.render("at work", True, WHITE)
        work_rect = work_text.get_rect(center=(WINDOW_WIDTH//2, 90))
        self.screen.blit(work_text, work_rect)
        
        # Draw Game PIN
        pin_text = self.pin_font.render(f"Game PIN: {self.game_pin}", True, WHITE)
        pin_rect = pin_text.get_rect(center=(WINDOW_WIDTH//2, 140))
        self.screen.blit(pin_text, pin_rect)
        
        # Update and draw other elements
        self.update_players()
        self.draw_start_button()
        self.draw_player_count()
        self.draw_users_grid()
        
        pygame.display.flip()

def run_login():
    clock = pygame.time.Clock()
    ui = KahootUI()
    
    while True:
        if not ui.handle_events():
            break
        ui.draw()
        clock.tick(60)
    
    return ui.game_started, ui.firebase, ui.logged_in_users

# if __name__ == "__main__":
#     game_started, firebase, players = run_login()
#     if game_started:
#         print("Starting game with players:", players)
#     pygame.quit()
#     sys.exit()