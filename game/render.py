import pygame

from engine.rules import FIGHTER_H, FIGHTER_W, MAX_HEALTH, WIDTH, attack_rect, is_ko

HEIGHT = 450
WHITE = (255, 255, 255)  # Hanuman
DARK_GREEN = (0, 100, 0)  # Tosakan
RED = (200, 60, 60)  # Hitbox outline
BLUE = (80, 140, 255)  # Block outline
YELLOW = (240, 200, 60)  # Bot wind-up warning outline
GREEN = (60, 180, 60)  # Health bar fill
GREY = (60, 60, 60)  # Health bar background
BACKGROUND = (30, 30, 30)
BAR_W, BAR_H = 300, 20


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
    # Draws a world dict, art will be swapped in here later
    player = world["player"]
    npc = world["npc"]
    ko = is_ko(world)

    hanuman = pygame.Rect(int(player["x"]), int(player["y"]), FIGHTER_W, FIGHTER_H)
    tosakan = pygame.Rect(int(npc["x"]), int(npc["y"]), FIGHTER_W, FIGHTER_H)

    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, WHITE, hanuman)
    pygame.draw.rect(screen, DARK_GREEN, tosakan)

    # Blue outline shows a fighter is blocking
    if player["blocking"]:
        pygame.draw.rect(screen, BLUE, hanuman, 4)
    if npc["blocking"]:
        pygame.draw.rect(screen, BLUE, tosakan, 4)

    # Yellow outline warns that the bot is about to attack
    if npc["warning"] and not ko:
        pygame.draw.rect(screen, YELLOW, tosakan, 4)

    # Show both fighters' active hitboxes
    for fighter in (player, npc):
        box = attack_rect(fighter)
        if box is not None:
            pygame.draw.rect(screen, RED, (int(box[0]), int(box[1]), box[2], box[3]), 2)

    draw_health_bar(screen, player, 20, False)
    draw_health_bar(screen, npc, WIDTH - 20 - BAR_W, True)

    if ko:
        winner = "Hanuman wins" if npc["health"] <= 0 else "Tosakan wins"
        text = font.render(winner, True, WHITE)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))