import pygame
import sys
import firebase_admin
from firebase_admin import credentials, db
import math

# Initialize Pygame
pygame.init()

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

# Initialize the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Quiz Game")

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://qi-game-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

class KahootUI:
    def __init__(self):
        self.logged_in_users = []  # List to store all logged-in users
        self.game_pin = "625 250"
        
        # Initialize fonts
        self.title_font = pygame.font.SysFont('arial', 48, bold=True)
        self.pin_font = pygame.font.SysFont('arial', 36)
        self.user_font = pygame.font.SysFont('arial', 24)
        self.count_font = pygame.font.SysFont('arial', 28)
        
        # Create gradient surface
        self.gradient_surface = self.create_gradient()
        
        # Initialize Firebase listener
        self.control_ref = db.reference('controls')
        self.firebase_listener = None
        self.start_firebase_listener()

        # Animation variables
        self.animations = {}  # Dictionary to store animation states
        self.animation_duration = 500  # Animation duration in milliseconds
        
        # Quit button rectangle
        self.quit_button_rect = pygame.Rect(WINDOW_WIDTH - 120, 20, 100, 40)

    def start_firebase_listener(self):
        """Start the Firebase listener"""
        self.firebase_listener = self.control_ref.listen(self.listen_for_changes)

    def stop_firebase_listener(self):
        """Stop the Firebase listener"""
        if self.firebase_listener:
            self.firebase_listener.close()
            self.firebase_listener = None

    def cleanup(self):
        """Cleanup resources before quitting"""
        self.stop_firebase_listener()
        pygame.quit()

    def listen_for_changes(self, event):
        """Handle Firebase events"""
        if event.data:
            data = event.data
            name = data.get('name', 'Unknown')
            command = data.get('command', 'None')
            
            if command == 'login' and name not in self.logged_in_users:
                self.logged_in_users.append(name)
                
                # Initialize animation for new user
                if not hasattr(self, 'animations'):
                    self.animations = {}  # Ensure animations exists
                self.animations[name] = {
                    'start_time': pygame.time.get_ticks(),
                    'scale': 0.0
                }

    def create_gradient(self):
        """Create a gradient background similar to Kahoot"""
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

    def handle_events(self):
        """Handle all events including quit button clicks"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Return False to indicate quitting
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.quit_button_rect.collidepoint(mouse_pos):
                        return False  # Return False to indicate quitting
        return True  # Continue running

    def draw_quit_button(self):
        """Draw a quit button"""
        button_color = (200, 0, 0)  # Red color for the quit button
        hover_color = (255, 0, 0)  # Brighter red for hover

        # Detect mouse position and change color if hovering over the button
        mouse_pos = pygame.mouse.get_pos()
        color = hover_color if self.quit_button_rect.collidepoint(mouse_pos) else button_color

        # Draw the button
        pygame.draw.rect(screen, color, self.quit_button_rect, border_radius=5)
        quit_text = self.user_font.render("Quit", True, WHITE)
        text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        screen.blit(quit_text, text_rect)

    def draw_users_grid(self):
        """Draw all logged-in users in a grid layout"""
        if not self.logged_in_users:
            return

        # Calculate starting position for the grid
        start_y = 220
        current_time = pygame.time.get_ticks()

        # Calculate total rows needed
        total_users = len(self.logged_in_users)
        rows = math.ceil(total_users / USERS_PER_ROW)

        for idx, user in enumerate(self.logged_in_users):
            # Calculate grid position
            row = idx // USERS_PER_ROW
            col = idx % USERS_PER_ROW
            
            # Calculate base position
            base_x = (WINDOW_WIDTH - (USERS_PER_ROW * (USER_BOX_WIDTH + USER_BOX_MARGIN))) // 2
            x = base_x + col * (USER_BOX_WIDTH + USER_BOX_MARGIN)
            y = start_y + row * (USER_BOX_HEIGHT + USER_BOX_MARGIN)

            # Handle animation
            if user not in self.animations:
                self.animations[user] = {
                    'start_time': current_time,
                    'scale': 0.0
                }

            animation = self.animations[user]
            progress = min(1.0, (current_time - animation['start_time']) / self.animation_duration)
            scale = animation['scale'] = min(1.0, animation['scale'] + 0.1)  # Smooth scaling

            # Apply animation scaling
            scaled_width = USER_BOX_WIDTH * scale
            scaled_height = USER_BOX_HEIGHT * scale
            x_offset = (USER_BOX_WIDTH - scaled_width) / 2
            y_offset = (USER_BOX_HEIGHT - scaled_height) / 2

            # Draw user box with animation
            user_box_rect = pygame.Rect(
                x + x_offset, 
                y + y_offset, 
                scaled_width, 
                scaled_height
            )
            pygame.draw.rect(screen, WHITE, user_box_rect, border_radius=10)

            # Draw username if animation is sufficiently progressed
            if scale > 0.5:
                opacity = min(255, int(510 * (scale - 0.5)))  # Fade in text
                user_text = self.user_font.render(user, True, KAHOOT_BLUE)
                text_surf = pygame.Surface(user_text.get_size(), pygame.SRCALPHA)
                text_surf.fill((255, 255, 255, 0))
                text_surf.blit(user_text, (0, 0))
                
                # Center the text in the box
                text_rect = user_text.get_rect(center=user_box_rect.center)
                screen.blit(user_text, text_rect)

    def draw_player_count(self):
        """Draw the total player count"""
        count_text = self.count_font.render(f"Players: {len(self.logged_in_users)}", True, WHITE)
        count_rect = count_text.get_rect(center=(WINDOW_WIDTH//2, 180))
        screen.blit(count_text, count_rect)

    def draw(self):
        """Draw the complete UI"""
        # Draw gradient background
        screen.blit(self.gradient_surface, (0, 0))
        
        # Draw Kahoot logo text
        logo_text = self.title_font.render("Quiz intelligence", True, WHITE)
        logo_rect = logo_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(logo_text, logo_rect)
        
        # Draw "at work" text
        work_text = self.user_font.render("at work", True, WHITE)
        work_rect = work_text.get_rect(center=(WINDOW_WIDTH//2, 90))
        screen.blit(work_text, work_rect)
        
        self.draw_quit_button()
        
        # Draw player count
        self.draw_player_count()
        
        # Draw users grid
        self.draw_users_grid()
        
        pygame.display.flip()

def login():
    ui = KahootUI()
    clock = pygame.time.Clock()
    running = True  # Set running flag
    
    while running:
        running = ui.handle_events()  # Stop loop if handle_events returns False
        ui.draw()
        clock.tick(60)
    
    # Cleanup after exiting the loop
    ui.cleanup()

# Run the game
if __name__ == "__main__":
    login()