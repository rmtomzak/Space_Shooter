import pygame
import random
import socket
import threading
import pickle

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50
FALLING_OBJECT_SIZE = 30
FPS = 60

# Initialize server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.68.73", 5555))
server.listen(2)
players = []
shots = []
falling_objects = []

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

def handle_client(conn, player_id):
    global players, shots, falling_objects
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            keys = pickle.loads(data)
            player = players[player_id]

            # Move player based on keys
            if keys[pygame.K_q]:
                player["alive"] = True
                player["shots"] = 10
            if keys[pygame.K_LEFT]:
                player["x"] -= 5
            if keys[pygame.K_RIGHT]:
                player["x"] += 5
            if keys[pygame.K_UP]:
                player["y"] -= 5
            if keys[pygame.K_DOWN]:
                player["y"] += 5
            if keys[pygame.K_SPACE] and player["shots"] > 0:
                if len([s for s in shots if s["player_id"] == player_id]) == 0:
                    shots.append({"x": player["x"] + PLAYER_SIZE//2, "y": player["y"], "player_id": player_id})
                    player["shots"] -= 1
            
            # Keep player in bounds
            player["x"] = max(0, min(SCREEN_WIDTH - PLAYER_SIZE, player["x"]))
            player["y"] = max(0, min(SCREEN_HEIGHT - PLAYER_SIZE, player["y"]))

            # Check for collisions
            for obj in falling_objects:
                if pygame.Rect(player["x"], player["y"], PLAYER_SIZE, PLAYER_SIZE).colliderect(
                    pygame.Rect(obj["x"], obj["y"], FALLING_OBJECT_SIZE, FALLING_OBJECT_SIZE)
                ):
                    player["alive"] = False

            # Update falling objects
            for obj in falling_objects:
                obj["y"] += 1
            falling_objects = [obj for obj in falling_objects if obj["y"] < SCREEN_HEIGHT]

            # Update shots
            for shot in shots:
                shot["y"] -= 10
            shots = [shot for shot in shots if shot["y"] > 0]

            # Check if shots hit falling objects
            for shot in shots:
                for obj in falling_objects:
                    if pygame.Rect(shot["x"], shot["y"], 5, 10).colliderect(
                        pygame.Rect(obj["x"], obj["y"], FALLING_OBJECT_SIZE, FALLING_OBJECT_SIZE)
                    ):
                        falling_objects.remove(obj)
                        shots.remove(shot)
                        break

            # Send game state back to client
            conn.sendall(pickle.dumps({"players": players, "shots": shots, "falling_objects": falling_objects}))

        except Exception as e:
            print(f"Client {player_id} disconnected.")
            break

    conn.close()

def main():
    global players, falling_objects
    player_count = 0
    while player_count < 2:
        conn, addr = server.accept()
        print(f"Player {player_count} connected.")
        player_name = conn.recv(1024).decode()
        players.append({"name": player_name, "x": random.randint(0, SCREEN_WIDTH-PLAYER_SIZE), "y": SCREEN_HEIGHT-PLAYER_SIZE, "shots": 10, "alive": True})
        threading.Thread(target=handle_client, args=(conn, player_count)).start()
        player_count += 1

    while True:

        # Check for game over
        alive_players = [p for p in players if p["alive"]]
        if len(alive_players) <= 1:
            pass
        else:
            if random.random() < 0.04:  # Chance to spawn a falling object
                falling_objects.append({"x": random.randint(0, SCREEN_WIDTH-FALLING_OBJECT_SIZE), "y": 0})

        clock.tick(FPS)

if __name__ == "__main__":
    main()
