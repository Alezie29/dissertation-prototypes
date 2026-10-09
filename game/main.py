import pygame

WIDTH, HEIGHT = 800, 450
FPS = 60
SPEED = 200  # pixels per second
WHITE = (255, 255, 255) # Hanuman
DARK_GREEN = (0, 100, 0) # Tosakan

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hanuman vs Tosakan")
    clock = pygame.time.Clock()

    hanuman = pygame.Rect(150, 230, 60, 120) # Creating the two rectangles to represent hanuman and tosakan
    tosakan = pygame.Rect(600, 230, 60, 120)
    hanuman_x = 150.0
    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        # TODO: if A is held, move Hanuman left by SPEED * dt; if D, move right
        if keys[pygame.K_a]:
            hanuman_x -= SPEED * dt 
        if keys[pygame.K_d]:
            hanuman_x += SPEED * dt

        hanuman.x = hanuman_x # The float holds the real position, this line copies it into Rect just before drawing.

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, WHITE, hanuman)
        pygame.draw.rect(screen, DARK_GREEN, tosakan)
            
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()