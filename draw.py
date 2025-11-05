import pygame

# System important variables
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
FPS = 60
clock = pygame.time.Clock()
delta_time = 0.1
rect_colliders = []

# A 2D vector class
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# The player object for this game
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = Vector2(0, 0)
        self.rect = pygame.Rect(self.x, self.y, 50, 50)
        self.friction = 0.9

    def update(self):
        if abs(self.velocity.x) > 0.1:
            self.velocity.x *= self.friction
        elif abs(self.velocity.x) > 0 and abs(self.velocity.x) <= 0.1:
            self.velocity.x = 0

        if abs(self.velocity.y) > 0.1:
            self.velocity.y *= self.friction
        elif abs(self.velocity.y) > 0 and abs(self.velocity.y) <= 0.1:
            self.velocity.y = 0

        for collider in rect_colliders:
            if pygame.sprite.collide_rect(self, collider) and collider != self.rect:
                ########################
                # WIP
                colliderPos = Vector2(collider.x, collider.y)
                colliderDir = Vector2(abs(colliderPos.x - self.x), abs(colliderPos.y - self.y))
                ########################
                self.velocity.x *= -1
                self.velocity.y *= -1

        self.move()

        self.x += self.velocity.x * delta_time
        self.y += self.velocity.y * delta_time
        self.rect.topleft = (self.x, self.y)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.velocity.x -= 50
        if keys[pygame.K_d]:
            self.velocity.x += 50
        if keys[pygame.K_w]:
            self.velocity.y -= 50
        if keys[pygame.K_s]:
            self.velocity.y += 50

        
class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def spawn(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

# Game initialization
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

running = True
pygame.init

player1 = Player(0, 0)
wall1 = Wall(100, 100, 250, 25)
rect_colliders.append(player1)
rect_colliders.append(wall1)

# Runtime loop for the game
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    wall1.spawn()
    player1.update()

    pygame.display.flip()

    
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(delta_time, 0.1))

pygame.quit()
