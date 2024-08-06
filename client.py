import pygame
import socket
import pickle
import sys

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50
FALLING_OBJECT_SIZE = 40
FPS = 60

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.68.73", 5555))
player_name = sys.argv[1]
client.sendall(player_name.encode())

def draw_triangle(screen, color, position, size):
    x, y = position
    half_size = size // 2
    points = [
        (x + half_size, y),
        (x , y + half_size),
        (x + size, y + half_size)
    ]
    pygame.draw.polygon(screen, color, points)

def main():
    run = True
    while run:
        clock.tick(FPS)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Send player input to server
        keys = pygame.key.get_pressed()
        client.sendall(pickle.dumps(keys))

        # Receive game state from server
        data = client.recv(4096)
        game_state = pickle.loads(data)

        players = game_state["players"]
        shots = game_state["shots"]
        falling_objects = game_state["falling_objects"]

        # Render game
        screen.fill((0, 0, 0))

        for player in players:
            color = (0, 255, 0) if player["alive"] else (255, 0, 0)
            # pygame.draw.rect(screen, color, (player["x"], player["y"], PLAYER_SIZE, PLAYER_SIZE))
            draw_triangle(screen, color, (player["x"], player["y"]), PLAYER_SIZE)
            # Display player name and shots remaining
            text = font.render(f"{player['name']}: {player['shots']} shots", True, (255, 255, 255))
            screen.blit(text, (player["x"], player["y"] + 25))

        for shot in shots:
            pygame.draw.rect(screen, (255, 255, 0), (shot["x"], shot["y"], 5, 10))

        for obj in falling_objects:
            pygame.draw.rect(screen, (255, 0, 0), (obj["x"], obj["y"], FALLING_OBJECT_SIZE, FALLING_OBJECT_SIZE))

        pygame.display.flip()

if __name__ == "__main__":
    main()
    
