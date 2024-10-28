import pygame
import firebase_admin
from firebase_admin import credentials, db



# Initialize Firebase Admin SDK
cred = credentials.Certificate("e-rhythm-firebase-adminsdk-6yoja-f6d1ff58cc.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://e-rhythm-default-rtdb.asia-southeast1.firebasedatabase.app'
})

pygame.init()
screen = pygame.display.set_mode((640, 480))

font = pygame.font.Font(None, 36)  # Use default font, size 36
display_text = ""

# Function to handle incoming data from Firebase
def listen_for_changes(event):
    global display_text
    if event.data:
        data = event.data
        name = data.get('name', 'Unknown')  # Default to 'Unknown' if 'name' is missing
        command = data.get('command', 'None')  # Default to 'None' if 'command' is missing
        print(f"{name} pressed {command}")
        display_text = f"{name} pressed {command}"


        # Handle commands in Pygame based on the button pressed
        if command == '1':
            print("1")
        elif command == '2':
            print("2")
        elif command == '3':
            print("3")
        elif command == '4':
            print("4")


# Set Firebase listener for real-time updates
control_ref = db.reference('controls')
control_ref.listen(listen_for_changes)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
      # Render the text and blit it to the screen
    text_surface = font.render(display_text, True, (255, 255, 255))  # White text
    screen.blit(text_surface, (20, 20))  # Position the text
    pygame.display.flip()
    

pygame.quit()
