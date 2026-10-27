import pygame

WIDTH, HEIGHT = 800, 450
FPS = 60
SPEED = 200  # pixels per second
WHITE = (255, 255, 255) # Hanuman
DARK_GREEN = (0, 100, 0) # Tosakan
RED = (200, 60, 60) # Hitbox outline
BLUE = (80, 140, 255) # Block outline
GREEN = (60, 180, 60) # Health bar
GREY = (60, 60, 60)
GRAVITY = 1800 # Pixels per second
JUMP_SPEED = 700 # Pixels per second, Upwards
GROUND_Y = 230.0 # Top edge of the rect when standing on the floor
FIGHTER_W, FIGHTER_H = 60, 120
MAX_HEALTH = 100
BAR_W, BAR_H = 300, 20
BLOCK_DIVISOR = 5 # A blocked attack will only deal a fifth of the damage


# One table describes every attack, cleaner code instead of a new variable each different attack added
ATTACKS = {
    "punch": {"duration": 0.3,  "start": 0.1, "end": 0.2, "damage": 10, "w": 50, "h": 30, "y_off": 30},
    "kick":  {"duration": 0.45, "start": 0.2, "end": 0.3, "damage": 15, "w": 70, "h": 25, "y_off": 70},
}

def new_fighter(x):
    return {
        "x": x, "y": GROUND_Y, "vx": 0.0, "vy": 0.0,
        "health": MAX_HEALTH,
        "facing": 1, # 1 = facing right, -1 = facing left
        "attack_kind": None,
        "attack_t": -1.0, # -1 represents the fighter not attacking
        "hit_done": False, # Stops one punch damaging every frame of active window
    }

def step_fighter(fighter, inputs, dt):
    # This will work on any fighter dict, never reads the keyboard
    on_floor = fighter["y"] >= GROUND_Y
    attacking = fighter["attack_t"] >= 0

    # Block only works on the ground and not mid-attack animation
    blocking = inputs["block"] and on_floor and not attacking 
    fighter["blocking"] = blocking

    # A grounded fighter is rooted while attacking, every attack becomes a commitment, reduces spamming of attacks
    if not (attacking and on_floor) and not blocking:
        if inputs["left"]:
            fighter["x"] -= SPEED * dt
        if inputs["right"]:
            fighter["x"] += SPEED * dt

    # No jumping out of an attack (animation cancel) or a block
    if inputs["jump"] and on_floor and not attacking and not blocking:  # Fighter on the floor
        fighter["vy"] = -JUMP_SPEED  # Y grows downwards, so up is negative

    fighter["vy"] += GRAVITY * dt
    fighter["y"] += fighter["vy"] * dt

    if fighter["y"] >= GROUND_Y:  # Fighter has landed
        fighter["y"] = GROUND_Y
        fighter["vy"] = 0

    fighter["x"] = max(0, min(fighter["x"], WIDTH - FIGHTER_W))

    # Start an attack only if one isn't already running and if fighter is not blocking. If both keys are held, punch wins.
    if fighter["attack_t"] < 0 and not blocking:
        kind = None
        if inputs["punch"]:
            kind = "punch"
        elif inputs["kick"]:
            kind = "kick"  # Punch wins if both keys are held
        if kind is not None:
            fighter["attack_kind"] = kind
            fighter["attack_t"] = 0.0
            fighter["hit_done"] = False

    # Attack timer counts with dt, not real time. 
    if fighter["attack_t"] >= 0:
        fighter["attack_t"] += dt
        if fighter["attack_t"] >= ATTACKS[fighter["attack_kind"]]["duration"]:
            fighter["attack_t"] = -1.0
            fighter["attack_kind"] = None

def attack_rect(fighter):
    # Returns the punch hitbox, or None if the fighter isn't in the active window
    if fighter["attack_kind"] is None:
        return None
    atk = ATTACKS[fighter["attack_kind"]]
    t = fighter["attack_t"]
    if t < atk["start"] or t > atk["end"]:
        return None
    if fighter["facing"] == 1:
        x = fighter["x"] + FIGHTER_W  # Starts at the right edge
    else:
        x = fighter["x"] - atk["w"]  # Starts at the left edge
    y = fighter["y"] + atk["y_off"]
    return pygame.Rect(int(x), int(y), atk["w"], atk["h"])

def resolve_hit(attacker, defender):
    # Needs both fighters, so it can't live inside step_fighter
    hitbox = attack_rect(attacker)
    if hitbox is None or attacker["hit_done"]:
        return
    defender_rect = pygame.Rect(int(defender["x"]), int(defender["y"]), FIGHTER_W, FIGHTER_H)
    if hitbox.colliderect(defender_rect):
        damage = ATTACKS[attacker["attack_kind"]]["damage"]
        if defender["blocking"]:
            damage = damage // BLOCK_DIVISOR # Fighters always face each other, so a block always covers the front of the fighter
        defender["health"] = max(0, defender["health"] - damage)
        attacker["hit_done"] = True

def seperate(mover, blocker):
    # Pushes the mover out of the blocker, so the blocker is never shoved
    overlap_x = FIGHTER_W - abs(mover["x"] - blocker["x"])
    overlap_y = FIGHTER_H - abs(mover["y"] - blocker["y"])
    if overlap_x > 0 and overlap_y > 0:
        if mover["x"] < blocker["x"]:
            mover["x"] -= overlap_x  # Mover is on the left, so push left
        else:
            mover["x"] += overlap_x  # Mover is on the right, so push right
        # Keep the mover inside the window
        mover["x"] = max(0, min(mover["x"], WIDTH - FIGHTER_W))

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

    no_input = {"left": False, "right": False, "jump": False, "punch": False, "kick": False, "block": False}  # Tosakan idles for now
 
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
            "kick": keys[pygame.K_q],
            "block": keys[pygame.K_f],
        }

        # TEMPORARY TOSAKAN ATTACK TO TEST BLOCKING
        tosakan_inputs = dict(no_input)
        tosakan_inputs["punch"] = keys[pygame.K_t]

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
            step_fighter(tosakan_state, tosakan_inputs, dt)

            seperate(hanuman_state, tosakan_state)

            resolve_hit(hanuman_state, tosakan_state)
            resolve_hit(tosakan_state, hanuman_state)

        hanuman.x = hanuman_state["x"]
        hanuman.y = hanuman_state["y"]
        tosakan.x = tosakan_state["x"]
        tosakan.y = tosakan_state["y"]

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, WHITE, hanuman)
        pygame.draw.rect(screen, DARK_GREEN, tosakan)

        # Blue outline represents a fighter is blocking
        if hanuman_state["blocking"]:
            pygame.draw.rect(screen, BLUE, hanuman, 4)
        if tosakan_state["blocking"]:
            pygame.draw.rect(screen, BLUE, tosakan, 4)

        # Show both fighters' active hitboxes
        for state in (hanuman_state, tosakan_state):
            hitbox = attack_rect(state)
            if hitbox is not None:
                pygame.draw.rect(screen, RED, hitbox, 2) # Outline only, so active window is still visible

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