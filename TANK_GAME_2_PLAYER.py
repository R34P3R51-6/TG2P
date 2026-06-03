import pgzrun
import pygame
import random
import math

# ===================
#  © R34P3R51-6 2026
#  Apache-2.0
# ===================

# =========
# SETTINGS
# =========
BASE_WIDTH = 1200
BASE_HEIGHT = 600

WIDTH = BASE_WIDTH
HEIGHT = BASE_HEIGHT

SPEED = 0.5
ROT_SPEED = 1
BULLET_SPEED = 10
COOLDOWN = 200

P1_KEYS = ("w", "s", "a", "d", "space")
P2_KEYS = ("up", "down", "left", "right", "return")

FULLSCREEN = False
# ===========
# GAME STATE
# ===========
score1 = 0
score2 = 0

health_blue = 5
health_red = 5

winner = None
reset_timer = 200

walls = []
bullets = []
explosions = []

# =======
# ACTORS
# =======
background = Actor("dev_2")

wall_image = "dev_wall"

player1 = Actor("ac1_sentinel_test", (600, 550))
player2 = Actor("type_97_chi_ha", (600, 50))
player2.angle = 180

player1.alive = True
player2.alive = True

p1_cooldown = 0
p2_cooldown = 0

# ======
# SOUND
# ======
sounds.shot.set_volume(0.3)
sounds.explo_1.set_volume(1.0)

music.play("tankshots")

# ========
# HELPERS
# ========


def rotated_hitbox(player, width=97, height=58):

    angle = math.radians(-player.angle)

    hw = width / 2
    hh = height / 2

    corners = [
        (-hw, -hh),
        ( hw, -hh),
        ( hw,  hh),
        (-hw,  hh)
    ]

    points = []

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    for x, y in corners:

        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a

        points.append((player.x + rx, player.y + ry))

    return points


def point_in_polygon(x, y, polygon):

    inside = False
    j = len(polygon) - 1

    for i in range(len(polygon)):

        xi, yi = polygon[i]
        xj, yj = polygon[j]

        intersect = (
            ((yi > y) != (yj > y)) and
            (x < (xj - xi) * (y - yi) / (yj - yi + 0.00001) + xi)
        )

        if intersect:
            inside = not inside

        j = i

    return inside


def tank_collides(player, walls):

    poly = rotated_hitbox(player)

    for wall in walls:

        corners = [
            (wall.left, wall.top),
            (wall.right, wall.top),
            (wall.right, wall.bottom),
            (wall.left, wall.bottom)
        ]

        for x, y in corners:
            if point_in_polygon(x, y, poly):
                return True


    return False
def build_walls():
    result = []

    for x in range(16):
        for y in range(8):

            if random.random() < 0.4:
                wall = Actor(wall_image, (x * 50 + 225, y * 50 + 125))

                result.append(wall)

    return result


def create_explosion(pos):
    exp = Actor("explosion1", pos)

    exp.frame = 1
    exp.timer = 0

    explosions.append(exp)

    sounds.explo_1.play()


def move_player(player, keys_set):

    forward = keys_set[0]
    backward = keys_set[1]
    left = keys_set[2]
    right = keys_set[3]

    old_angle = player.angle

    if getattr(keyboard, left):
        player.angle += ROT_SPEED

    if getattr(keyboard, right):
        player.angle -= ROT_SPEED

    if tank_collides(player, walls):
        player.angle = old_angle

    rad = math.radians(player.angle)

    dx = 0
    dy = 0

    if getattr(keyboard, forward):
        dx += math.cos(rad) * SPEED
        dy -= math.sin(rad) * SPEED

    if getattr(keyboard, backward):
        dx -= math.cos(rad) * SPEED
        dy += math.sin(rad) * SPEED

    player.x += dx

    if tank_collides(player, walls):
        player.x -= dx

    player.y += dy

    if tank_collides(player, walls):
        player.y -= dy

    player.x = max(225, min(1000, player.x))
    player.y = max(50, min(HEIGHT - 50, player.y))

def shoot(player, owner):

    bullet = Actor("bulletblue2")

    rad = math.radians(player.angle)

    bullet.x = player.x + math.cos(rad) * 30
    bullet.y = player.y - math.sin(rad) * 30

    bullet.dx = math.cos(rad) * BULLET_SPEED
    bullet.dy = -math.sin(rad) * BULLET_SPEED

    bullet.owner = owner

    bullets.append(bullet)

    sounds.shot.play()


def handle_shooting(player, keys_set, cooldown, owner):

    shoot_key = keys_set[4]

    if cooldown > 0:
        return cooldown - 1

    if keyboard[shoot_key]:
        shoot(player, owner)
        return COOLDOWN

    return 0


def reset_round():

    global health_blue
    global health_red
    global winner
    global reset_timer
    global walls
    global wall_image

    player1.pos = (600, 550)
    player2.pos = (600, 50)

    player1.alive = True
    player2.alive = True

    wall_image = wall_image

    health_blue = 5
    health_red = 5

    walls = build_walls()

    winner = None
    reset_timer = 20


def toggle_max_fullscreen():
    screen.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


def on_key_down(key):

    global wall_image
    global background_image
    global FULLSCREEN
    global wall_image

    FULLSCREEN = False

    if key == keys.K_2:

        wall_image = "dev_wall"
        background.image = "dev_2"

        for wall in walls:
            wall.image = wall_image

    elif key == keys.K_1:

        wall_images = ["city_wall1", "city_wall2", "city_wall3", "city_wall4"]

        background.image = "city"

        for wall in walls:
            wall.image = random.choice(wall_images)
            wall_image = wall.image

    if key == keys.F11 and FULLSCREEN == False:

        FULLSCREEN = True

    elif key == keys.F11 and FULLSCREEN == True:
        FULLSCREEN = False

    elif key == keys.ESCAPE:

        quit()


# =======
# UPDATE
# =======
def update():

    global p1_cooldown
    global p2_cooldown

    global health_blue
    global health_red

    global winner
    global reset_timer

    global score1
    global score2

    global FULLSCREEN

    if FULLSCREEN == True:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    if winner:

        reset_timer -= 1

        if reset_timer <= 0:
            reset_round()

        return

    if player1.alive:

        move_player(player1, P1_KEYS)

        p1_cooldown = handle_shooting(player1, P1_KEYS, p1_cooldown, "p1")

    if player2.alive:

        move_player(player2, P2_KEYS)

        p2_cooldown = handle_shooting(player2, P2_KEYS, p2_cooldown, "p2")

    for b in bullets[:]:

        b.x += b.dx
        b.y += b.dy

        hit = b.collidelist(walls)

        if hit != -1:

            create_explosion(b.pos)

            del walls[hit]

            bullets.remove(b)

            continue

        if b.owner != "p1" and b.colliderect(player1):

            health_blue -= 1

            create_explosion(b.pos)

            bullets.remove(b)

            continue

        if b.owner != "p2" and b.colliderect(player2):

            health_red -= 1

            create_explosion(b.pos)

            bullets.remove(b)

            continue

        if not (0 <= b.x <= WIDTH and 0 <= b.y <= HEIGHT):

            bullets.remove(b)

    for e in explosions[:]:

        e.timer += 1

        if e.timer % 5 == 0:

            e.frame += 1

            if e.frame > 4:

                explosions.remove(e)

            else:

                e.image = "explosion" + str(e.frame)

    if health_red <= 0:

        winner = "BLUE"
        score1 += 1

    elif health_blue <= 0:

        winner = "RED"
        score2 += 1


out1 = 600, 25
# =====
# DRAW
# =====

def draw():

    screen.clear()

    background.draw()

    for w in walls:
        w.draw()

    for e in explosions:
        e.draw()

    for b in bullets:
        b.draw()

    if player1.alive:
        player1.draw()

    if player2.alive:
        player2.draw()

    screen.draw.text("BLUE: " + str(score1), (110, 40), color="blue")

    screen.draw.text("RED: " + str(score2), (10, 40), color="red")

    screen.draw.text("HP: " + str(health_blue), (110, 25), color="blue")

    screen.draw.text("HP: " + str(health_red), (10, 25), color="red")

    if winner:

        screen.draw.text(
            winner + " WINS!",
            center=(WIDTH // 2, HEIGHT // 2),
            fontsize=80,
            color="yellow",
        )

    for player in [player1, player2]:

        player.draw()

        p = rotated_hitbox(player)

        screen.draw.line(p[0], p[1], "red")
        screen.draw.line(p[1], p[2], "red")
        screen.draw.line(p[2], p[3], "red")
        screen.draw.line(p[3], p[0], "red")
# ======
# START
# ======
walls = build_walls()


def start(player):

    hit = player.collidelist(walls)

    if hit != -1:
        del walls[hit]


start(player1)
start(player2)
pgzrun.go()
