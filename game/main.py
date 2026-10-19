import pygame

WIDTH, HEIGHT = 800, 450
FPS = 60
SPEED = 200  # pixels per second
WHITE = (255, 255, 255) # Hanuman
DARK_GREEN = (0, 100, 0) # Tosakan
GRAVITY = 1800 # Pixels per second
JUMP_SPEED = 700 # Pixels per second, Upwards
GROUND_Y = 230.0 # Top edge of the rect when standing on the floor
FIGHTER_W, FIGHTER_H = 60, 120

def step_fighter(fighter, inputs, dt):
    # This will work on any fighter dict, never reads the keyboard
    if inputs["left"]:
        fighter["x"] -= SPEED * dt
    if inputs["right"]:
        fighter["x"] += SPEED * dt

    if inputs["jump"] and fighter["y"] >= GROUND_Y:  # Fighter on the floor
        fighter["vy"] = -JUMP_SPEED  # Y grows downwards, so up is negative

    fighter["vy"] += GRAVITY * dt
    fighter["y"] += fighter["vy"] * dt

    if fighter["y"] >= GROUND_Y:  # Fighter has landed
        fighter["y"] = GROUND_Y
        fighter["vy"] = 0

    fighter["x"] = max(0, min(fighter["x"], WIDTH - FIGHTER_W))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hanuman vs Tosakan")
    clock = pygame.time.Clock()

    # This is the same shape as GameState.entities, so it ports across later
    hanuman_state = {"x": 150.0, "y": GROUND_Y, "vx": 0.0, "vy": 0.0}
    tosakan_state = {"x": 600.0, "y": GROUND_Y, "vx": 0.0, "vy": 0.0}

    # Rects are only for drawing, the dicts hold the real positions
    hanuman = pygame.Rect(0, 0, FIGHTER_W, FIGHTER_H)
    tosakan = pygame.Rect(0, 0, FIGHTER_W, FIGHTER_H)

    no_input = {"left": False, "right": False, "jump": False}  # Tosakan idles for now


    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        hanuman_inputs = {
            "left": keys[pygame.K_a],
            "right": keys[pygame.K_d],
            "jump": keys[pygame.K_SPACE],
        }

        step_fighter(hanuman_state, hanuman_inputs, dt)
        step_fighter(tosakan_state, no_input, dt)

        hanuman.x = hanuman_state["x"]
        hanuman.y = hanuman_state["y"]
        tosakan.x = tosakan_state["x"]
        tosakan.y = tosakan_state["y"]

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, WHITE, hanuman)
        pygame.draw.rect(screen, DARK_GREEN, tosakan)
            
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()