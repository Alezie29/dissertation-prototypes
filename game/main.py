import pygame

MAX_HEALTH = 100
GREEN = (60, 180, 60)
GREY = (60, 60, 60)
BAR_W, BAR_H = 300, 20

WIDTH, HEIGHT = 800, 450
FPS = 60
SPEED = 200  # pixels per second
WHITE = (255, 255, 255) # Hanuman
DARK_GREEN = (0, 100, 0) # Tosakan
RED = (200, 60, 60) # Hitbox outline
GRAVITY = 1800 # Pixels per second
JUMP_SPEED = 700 # Pixels per second, Upwards
GROUND_Y = 230.0 # Top edge of the rect when standing on the floor
FIGHTER_W, FIGHTER_H = 60, 120

PUNCH_DURATION = 0.3 # Seconds from the start until the end of the punch
PUNCH_ACTIVE_START = 0.1 # Hitbox exists between these two times
PUNCH_ACTIVE_END = 0.2
PUNCH_DAMAGE = 10
PUNCH_W, PUNCH_H = 50, 30

def new_fighter(x):
    return {
        "x": x, "y": GROUND_Y, "vx": 0.0, "vy": 0.0,
        "health": MAX_HEALTH,
        "facing": 1, # 1 = facing right, -1 = facing left
        "attack_t": -1.0, # -1 represents the fighter not attacking
        "hit_done": False, # Stops one punch damaging every frame of active window
    }

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

    # Punch timer counts with dt, not real time. 
    if inputs["punch"] and fighter["attack_t"] < 0:
        fighter["attack_t"] = 0.0
        fighter["hit_done"] = False
    if fighter["attack_t"] >= 0:
        fighter["attack_t"] += dt
        if fighter["attack_t"] >= PUNCH_DURATION:
            fighter["attack_t"] = -1.0

def attack_rect(fighter):
    # Returns the punch hitbox, or None if the fighter isn't in the active window
    t = fighter["attack_t"]
    if t < PUNCH_ACTIVE_START or t > PUNCH_ACTIVE_END:
        return None
    if fighter["facing"] == 1:
        x = fighter["x"] + FIGHTER_W # Starts at the right edge
    else:
        x = fighter["x"] - PUNCH_W # Starts at the left edge
    y = fighter["y"] + 30 # Chest height
    return pygame.Rect(int(x), int(y), PUNCH_W, PUNCH_H)

def resolve_hit(attacker, defender):
    # Needs both fighters, so it can't live inside step_fighter
    hitbox = attack_rect(attacker)
    if hitbox is None or attacker["hit_done"]:
        return
    defender_rect = pygame.Rect(int(defender["x"]), int(defender["y"]), FIGHTER_W, FIGHTER_H)
    if hitbox.colliderect(defender_rect):
        defender["health"] = max(0, defender["health"] - PUNCH_DAMAGE)
        attacker["hit_done"] = True

def draw_health_bar(screen, fighter, x, align_right):
    ratio = fighter["health"] / MAX_HEALTH
    fill = int(BAR_W * ratio)
    pygame.draw.rect(screen, GREY, (x, 20, BAR_W, BAR_H)) # Empty health bar
    if align_right:
        pygame.draw.rect(screen, GREEN, (x + BAR_W - fill, 20, fill, BAR_H)) # Drains towards the far right edge
    else:
        pygame.draw.rect(screen, GREEN, (x, 20, fill, BAR_H))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hanuman vs Tosakan")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 72)

    hanuman_state = new_fighter(150.0)
    tosakan_state = new_fighter(600.0)

    # Rects are only for drawing, the dicts hold the real positions
    hanuman = pygame.Rect(0, 0, FIGHTER_W, FIGHTER_H)
    tosakan = pygame.Rect(0, 0, FIGHTER_W, FIGHTER_H)

    no_input = {"left": False, "right": False, "jump": False, "punch": False}  # Tosakan idles for now
 
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
            "punch": keys[pygame.K_e],
        }

        ko = hanuman_state["health"] <= 0 or tosakan_state["health"] <= 0

        if ko:
            if keys[pygame.K_r]: # Resets the round
                hanuman_state = new_fighter(150.0)
                tosakan_state = new_fighter(600.0)

        else:
            # Each fighter always faces the other one
            hanuman_state["facing"] = 1 if tosakan_state["x"] > hanuman_state["x"] else -1
            tosakan_state["facing"] = -hanuman_state["facing"]

            step_fighter(hanuman_state, hanuman_inputs, dt)
            step_fighter(tosakan_state, no_input, dt)

            resolve_hit(hanuman_state, tosakan_state)
            resolve_hit(tosakan_state, hanuman_state)

        hanuman.x = hanuman_state["x"]
        hanuman.y = hanuman_state["y"]
        tosakan.x = tosakan_state["x"]
        tosakan.y = tosakan_state["y"]

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, WHITE, hanuman)
        pygame.draw.rect(screen, DARK_GREEN, tosakan)

        hitbox = attack_rect(hanuman_state)
        if hitbox is not None:
            pygame.draw.rect(screen, RED, hitbox, 2) # Outline only, so active window is visible

        draw_health_bar(screen, hanuman_state, 20, False)
        draw_health_bar(screen, tosakan_state, WIDTH - 20 - BAR_W, True)

        if ko:
            winner = "Hanuman wins" if tosakan_state["health"] <= 0 else "Tosakan wins"
            text = font.render(winner, True, WHITE)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            hint = font.render("Press R", True, WHITE)
            screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()