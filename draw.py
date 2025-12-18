import pygame
import math

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

    def getMagnitude(self) -> int:
        magnitude : float = math.sqrt((self.x ** 2) + (self.y ** 2))
        return magnitude

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

    def setXY(self, x, y):
        self.x = x
        self.y = y

# The player object for this game
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = Vector2(0, 0)
        self.rect = pygame.Rect(self.x, self.y, 50, 50)
        self.friction = 0.8
        # Create a mask for player collision
        rectSurface = pygame.Surface(self.rect.size)
        self.mask = pygame.mask.from_surface(rectSurface)
        self.maskSurface = self.mask.to_surface()
        self.maskSurface.set_colorkey((100, 50, 0))
        self.maskSurface.fill((0, 255, 0, 100), special_flags=pygame.BLEND_RGBA_ADD)

    def update(self):
        if abs(self.velocity.x) > 0.1:
            self.velocity.x *= self.friction
        elif abs(self.velocity.x) > 0 and abs(self.velocity.x) <= 0.1:
            self.velocity.x = 0

        if abs(self.velocity.y) > 0.1:
            self.velocity.y *= self.friction
        elif abs(self.velocity.y) > 0 and abs(self.velocity.y) <= 0.1:
            self.velocity.y = 0

        self.move()


    def move(self):
        colliding = False
        for collider in rect_colliders:

            # Make the player bounce the opposite direction from the collider
            if pygame.sprite.collide_rect(self, collider) and collider != self.rect:
                colliding = True
                collisionDirection : Vector2 = getDirection((self.x, self.y), (collider.x, collider.y))
                maskOverlap = self.mask.overlap(collider.mask, (collisionDirection.x, collisionDirection.y))

                bounceDirection : Vector2 = getNormalizedDirection((self.getCenter()), maskOverlap)
                self.velocity.x -= bounceDirection.x * 50
                self.velocity.y -= bounceDirection.y * 50

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and not colliding:
            self.velocity.x -= 50
        if keys[pygame.K_d] and not colliding:
            self.velocity.x += 50
        if keys[pygame.K_w] and not colliding:
            self.velocity.y -= 50
        if keys[pygame.K_s] and not colliding:
            self.velocity.y += 50

        self.x += self.velocity.x * delta_time
        self.y += self.velocity.y * delta_time
        self.rect.topleft = (self.x, self.y)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        screen.blit(self.maskSurface, self.rect)

    def getCenter(self) -> tuple:
        return self.rect.center


# A wall that blocks the player from moving past it
class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Create a mask for wall collision
        rectSurface = pygame.Surface(self.rect.size)
        self.mask = pygame.mask.from_surface(rectSurface)
    
    def spawn(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def getCenter(self) -> tuple:
        return self.rect.center

# Get the normalized direction from 1 object (usually a vector) to another returned as a vector
def getDirection(obj1 : tuple, obj2 : tuple) -> Vector2:
    direction = Vector2(obj2[0] - obj1[0], obj2[1] - obj1[1])
    return direction

# Get the normalized direction from 1 object (usually a vector) to another returned as a vector
def getNormalizedDirection(obj1 : tuple, obj2 : tuple) -> Vector2:
    direction = Vector2(obj2[0] - obj1[0], obj2[1] - obj1[1])
    normalizedDirection = Vector2(direction.x / direction.getMagnitude(), direction.y / direction.getMagnitude())
    return normalizedDirection

# Game initialization
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

running = True
pygame.init

objectList : list[object] = []
playerList : list[Player] = []

player1 = Player(0, 0)
wall1 = Wall(100, 100, 250, 25)

playerList.append(player1)
objectList.append(wall1)

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
