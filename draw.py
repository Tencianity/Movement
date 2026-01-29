import pygame # type: ignore
import math
import random

'''
Must install following geeneral dependencies (FedoraLinux-43 Syntax):
    sudo dnf install python3-devel
    sudo dnf install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
    sudo dnf install python3-pip
    pip install pygame-ce
'''

# System important variables
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
FPS = 60
clock = pygame.time.Clock()
delta_time = 0.1
rect_colliders = []
player_points = 0

# A 2D vector class
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getMagnitude(self) -> float:
        magnitude : float = math.sqrt((self.x ** 2) + (self.y ** 2))
        return magnitude

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

    def setXY(self, x, y):
        self.x = x
        self.y = y
    
    def getDistance(v1 : Vector2, v2 : Vector2) -> int:
        a = abs(v1.x - v2.x)
        b = abs(v1.y - v2.y)
        return int( math.sqrt(a**2 + b**2) )

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
        self.displayVelocity()
        self.displayPoints()


    def move(self):
        colliding = False
        for collider in rect_colliders:

            # Make the player bounce the opposite direction from the collider
            if pygame.sprite.collide_rect(self, collider) and collider is not self:
                colliding = True
                collisionDirection : Vector2 = getDirection((self.x, self.y), (collider.x, collider.y))
                maskOverlap = self.mask.overlap(collider.mask, (collisionDirection.x, collisionDirection.y))

                screenOverlap = self.x + maskOverlap[0], self.y + maskOverlap[1]

                bounceDirection : Vector2 = getNormalizedDirection((self.getCenter()), screenOverlap)
                self.velocity.x = bounceDirection.x * -50
                self.velocity.y = bounceDirection.y * -50

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and not colliding:
            self.velocity.x -= 70
        if keys[pygame.K_d] and not colliding:
            self.velocity.x += 70
        if keys[pygame.K_w] and not colliding:
            self.velocity.y -= 70
        if keys[pygame.K_s] and not colliding:
            self.velocity.y += 70

        self.x += self.velocity.x * delta_time
        self.y += self.velocity.y * delta_time
        self.rect.topleft = (self.x, self.y)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        screen.blit(self.maskSurface, self.rect)

        # Prevent player from leaving screen
        if self.x < 0:
            self.x = 0
        if self.x + self.rect.width > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.rect.width
        if self.y < 0:
            self.y = 0
        if self.y + self.rect.height > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.rect.height

    def getCenter(self) -> tuple:
        return self.rect.center
    
    def displayVelocity(self):
        text = f'Velocity: {(int) (self.velocity.x)}, {(int) (self.velocity.y)}'
        font = pygame.font.SysFont('Arial', 36)
        textSurface = font.render(text, True, (251, 255, 0))
        screen.blit(textSurface, (10, 670))

    def displayPoints(self):
        text = f'Points: {player_points}'
        font = pygame.font.SysFont('Arial', 30)
        textSurface = font.render(text, True, (251, 255, 0))
        screen.blit(textSurface, (980, 5))


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



class Apple:
    def __init__(self, x, y, points=1):
        self.x = x
        self.y = y
        self.points = points
        self.rect = pygame.Rect(self.x, self.y, 25, 25)
        check_near_player = False

    def spawn(self):
        pygame.draw.rect(screen, (0, 200, 0), self.rect)

        for collider in rect_colliders:
            if pygame.sprite.collide_rect(self, collider) and collider is not self:
                self.moveApple(collider, 100)

    # Move the Apple to a new location on the screen
    def moveApple(self, collider, dst_frm_player):
        if isinstance(collider, Player):
            global player_points
            player_points += self.points
                
        check_near_player = True

        # Make sure the Apple doesn't spawn within 100 pixels of the player
        while check_near_player:
            check_near_player = False
                
            newXY = Vector2(random.randint(0, 1030), random.randint(0, 680))
            if Vector2.getDistance(newXY, Vector2(collider.x, collider.y)) <= dst_frm_player:
                check_near_player = True
                continue
            self.rect.topleft = (newXY.x, newXY.y)



# Game initialization
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

running = True
pygame.init()
pygame.font.init()

objectList : list[object] = []
playerList : list[Player] = []

player1 = Player(0, 0)
wall1 = Wall(100, 100, 250, 25)
wall2 = Wall(300, 600, 30, 110)
apple = Apple(100, 100, 1)

playerList.append(player1)
objectList.append(wall1)
objectList.append(wall2)
objectList.append(apple)

rect_colliders.append(player1)
rect_colliders.append(wall1)
rect_colliders.append(wall2)

# Runtime loop for the game
while running:

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for obj in objectList:
        if isinstance(obj, Wall) or isinstance(obj, Apple):
            obj.spawn()

    player1.update()

    pygame.display.flip()

    
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(delta_time, 0.1))

pygame.quit()
