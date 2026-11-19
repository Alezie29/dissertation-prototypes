import time
from pathlib import Path

import pygame

from engine.rules import (
    ATTACKS, BOT_WARN, FIGHTER_H, FIGHTER_W, GROUND_Y, JUMP_SPEED, MAX_HEALTH,
    WIDTH, current_segment, is_ko,
)

HEIGHT = 450
WHITE = (255, 255, 255)  # Hanuman, and the text
DARK_GREEN = (0, 100, 0)  # Tosakan, only used if the art is missing
GREEN = (60, 180, 60)  # Health bar fill
GREY = (60, 60, 60)  # Health bar background
BACKGROUND = (30, 30, 30)
BAR_W, BAR_H = 300, 20

ASSETS = Path("assets")
SPRITE_SCALE = 2  # Frames are 96 pixels square, so this makes them 192
FOOT_OFFSET = 0  # Raise this if the fighters sink into the floor, lower it if they float
IDLE_SECONDS = 1.2  # Time for one full idle loop
WALK_SECONDS = 0.7  # Time for one full walk loop
HIT_SECONDS = 0.3  # How long the hit pose shows after taking damage

# Each character's folder, which way the art faces, and which animation folder is used for each pose
CHARACTERS = {
    "player": {
        "folder": "hanuman", "native": 1,
        "direction": "east",
        "poses": {
            "idle": "Breathing_Idle", "walk": "Walk", "jump": "Jumping",
            "punch": "Cross_Punch", "kick": "Roundhouse_Kick",
            "block": "Blocking_an_attack_with_his_hands",
            "hit": "Taking_Punch",
        },
    },
    "npc": {
        "folder": "tosakan", "native": -1,
        "direction": "west",
        "poses": {
            "idle": "Breathing_Idle", "walk": "Scary_Walk", "jump": "Jumping",
            "punch": "Cross_Punch", "kick": "Roundhouse_Kick",
            "block": "The_character_pulls_both_arms_inward_bracing_the_f",
            "windup": "Tosakan_winds_up_for_an_attack_he_pulls_his_right",
            "hit": "Taking_Punch",
        },
    },
}

_art = None  # Loaded once, on the first frame drawn. False means the art could not be found
_last_x = {}  # Where each fighter was drawn last time, only used to tell if they are walking
_last_health = {}  # Each fighter's health last frame, only used to notice a hit
_hit_until = {}  # Time until which each fighter's hit pose is shown


def load_art():
    # Loads every frame once, scaled up without blurring, plus a mirrored copy of each
    art = {}
    for key, info in CHARACTERS.items():
        art[key] = {}
        for pose, folder in info["poses"].items():
            path = ASSETS / info["folder"] / "Idle" / "animations" / folder / info["direction"]
            frames = []
            for file in sorted(path.glob("frame_*.png")):
                image = pygame.image.load(str(file)).convert_alpha()
                size = (image.get_width() * SPRITE_SCALE, image.get_height() * SPRITE_SCALE)
                image = pygame.transform.scale(image, size)  # Plain scale keeps the pixels sharp
                frames.append((image, pygame.transform.flip(image, True, False)))
            if not frames:
                raise FileNotFoundError(str(path))
            art[key][pose] = frames

    background = None
    found = sorted((ASSETS / "background").glob("*.png"))
    if found:
        image = pygame.image.load(str(found[0])).convert()
        background = pygame.transform.scale(image, (WIDTH, HEIGHT))
    art["background"] = background
    return art


def get_art():
    global _art
    if _art is None:
        try:
            _art = load_art()
        except (FileNotFoundError, pygame.error):
            _art = False  # No art found, so the plain rectangles are used
    return _art


def pick_frame(key, fighter, frames, now):
    # Chooses the pose from the world state, so a rollback restore shows the right pose automatically
    # The hit pose is the exception: It is drawing only, started when health is seen to drop
    previous = _last_health.get(key, fighter["health"])
    if fighter["health"] < previous:
        _hit_until[key] = now + HIT_SECONDS
    _last_health[key] = fighter["health"]

    if now < _hit_until.get(key, 0) and fighter["health"] > 0:
        pose, progress = "hit", 1 - (_hit_until[key] - now) / HIT_SECONDS
    elif fighter["attack_kind"] is not None and fighter["attack_t"] >= 0:
        duration = ATTACKS[fighter["attack_kind"]]["duration"]
        pose, progress = fighter["attack_kind"], fighter["attack_t"] / duration
    elif key == "npc" and fighter["warning"]:
        seg_t = current_segment(fighter["bot_t"])[1]
        pose, progress = "windup", seg_t / BOT_WARN
    elif fighter["blocking"]:
        pose, progress = "block", 0.4  # Holds one steady guard frame
    elif fighter["y"] < GROUND_Y - 1:
        pose, progress = "jump", (fighter["vy"] + JUMP_SPEED) / (2 * JUMP_SPEED)
    else:
        moving = abs(fighter["x"] - _last_x.get(key, fighter["x"])) > 0.05
        if moving:
            pose, progress = "walk", (now / WALK_SECONDS) % 1.0  # Drawing only, so it never affects the game
        else:
            pose, progress = "idle", (now / IDLE_SECONDS) % 1.0
    _last_x[key] = fighter["x"]
    options = frames[pose]
    return options[max(0, min(len(options) - 1, int(progress * len(options))))]


def draw_fighter(screen, key, fighter, art, now):
    normal, flipped = pick_frame(key, fighter, art[key], now)
    flip = fighter["facing"] != CHARACTERS[key]["native"]  # Mirror the art when facing the other way
    image = flipped if flip else normal
    rect = image.get_rect(midbottom=(int(fighter["x"]) + FIGHTER_W // 2, int(fighter["y"]) + FIGHTER_H + FOOT_OFFSET))
    screen.blit(image, rect)


def draw_health_bar(screen, fighter, x, align_right):
    ratio = fighter["health"] / MAX_HEALTH
    fill = int(BAR_W * ratio)
    pygame.draw.rect(screen, GREY, (x, 20, BAR_W, BAR_H))  # Empty bar
    if align_right:
        pygame.draw.rect(screen, GREEN, (x + BAR_W - fill, 20, fill, BAR_H))  # Drains toward the right edge
    else:
        pygame.draw.rect(screen, GREEN, (x, 20, fill, BAR_H))


def draw_waiting(screen, font):
    # Shown until the first server state arrives
    screen.fill(BACKGROUND)
    text = font.render("Connecting...", True, WHITE)
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


def draw_world(screen, font, world):
    # Draws a world dict and nothing else
    player = world["player"]
    npc = world["npc"]
    art = get_art()

    if art and art["background"] is not None:
        screen.blit(art["background"], (0, 0))
    else:
        screen.fill(BACKGROUND)

    if art:
        draw_fighter(screen, "player", player, art, time.monotonic())
        draw_fighter(screen, "npc", npc, art, time.monotonic())
    else:
        # Plain rectangles, only used if the art folder is missing
        pygame.draw.rect(screen, WHITE, (int(player["x"]), int(player["y"]), FIGHTER_W, FIGHTER_H))
        pygame.draw.rect(screen, DARK_GREEN, (int(npc["x"]), int(npc["y"]), FIGHTER_W, FIGHTER_H))

    draw_health_bar(screen, player, 20, False)
    draw_health_bar(screen, npc, WIDTH - 20 - BAR_W, True)

    if is_ko(world):
        winner = "Hanuman wins" if npc["health"] <= 0 else "Tosakan wins"
        text = font.render(winner, True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))