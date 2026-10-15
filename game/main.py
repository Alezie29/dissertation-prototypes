import pygame

WIDTH, HEIGHT = 800, 450
FPS = 60
SPEED = 200  # pixels per second
WHITE = (255, 255, 255) # Hanuman
DARK_GREEN = (0, 100, 0) # Tosakan
GRAVITY = 1800 # Pixels per second
JUMP_SPEED = 700 # Pixels per second, Upwards
GROUND_Y = 230.0 # Top edge of the rect when standing on the floor

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hanuman vs Tosakan")
    clock = pygame.time.Clock()

    hanuman = pygame.Rect(150, 230, 60, 120) # Creating the two rectangles to represent hanuman and tosakan
    tosakan = pygame.Rect(600, 230, 60, 120)
    hanuman_x = 150.0
    hanuman_y = GROUND_Y
    hanuman_vy = 0.0
    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            hanuman_x -= SPEED * dt 
        if keys[pygame.K_d]:
            hanuman_x += SPEED * dt

        if keys[pygame.K_SPACE] and hanuman_y >= GROUND_Y: # Hanuman is on the floor
            hanuman_vy = -JUMP_SPEED # Y grows downwards, so jump is negative
        hanuman_vy += GRAVITY * dt # Gravity changes velocity each frame
        hanuman_y += hanuman_vy * dt # same position as x now with a changing velocity

        if hanuman_y >= GROUND_Y:
            hanuman_y = GROUND_Y # Making sure hanuman doesn't overshoot the flow and stops the fall of the jump
            hanuman_vy = 0

        hanuman_x = max(0, min(hanuman_x, WIDTH - hanuman.width))

        hanuman.x = hanuman_x # The float holds the real position, this line copies it into Rect just before drawing.
        hanuman.y = hanuman_y

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, WHITE, hanuman)
        pygame.draw.rect(screen, DARK_GREEN, tosakan)
            
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()