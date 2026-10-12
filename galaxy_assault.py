import tkinter as tk
import random
import math
import time

W, H = 800, 700

root = tk.Tk()
root.title("NEBULA STRIKE | Space Combat")
root.resizable(False, False)

canvas = tk.Canvas(
    root, width=W, height=H,
    bg="#050816", highlightthickness=0
)
canvas.pack()

# Colors
CYAN = "#39F5FF"
PINK = "#FF3CAC"
PURPLE = "#8A5CFF"
WHITE = "#F4F7FF"
BG = "#050816"

state = "menu"
score = 0
health = 100
level = 1
frame = 0

bullets = []
enemies = []
particles = []
stars = []

player_x = W // 2
player_y = H - 100

keys = set()


def text(x, y, value, size, color=WHITE, font="Arial"):
    return canvas.create_text(
        x, y, text=value, fill=color,
        font=(font, size, "bold")
    )


def polygon(points, color, outline=""):
    return canvas.create_polygon(
        points, fill=color, outline=outline
    )


def make_background():
    canvas.delete("all")
    stars.clear()

    for _ in range(110):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.choice([1, 1, 2, 3])

        item = canvas.create_oval(
            x, y, x+r, y+r,
            fill=random.choice([WHITE, CYAN, PURPLE]),
            outline=""
        )
        stars.append([
            item, random.uniform(0.5, 2.5), r
        ])


def draw_player():
    x, y = player_x, player_y

    # Engine glow
    canvas.create_oval(
        x-9, y+12, x+9, y+38,
        fill=PURPLE, outline=""
    )

    # Wings
    polygon([
        x, y-30,
        x-33, y+22,
        x-12, y+15,
        x, y+25,
        x+12, y+15,
        x+33, y+22
    ], CYAN, WHITE)

    # Cockpit
    polygon([
        x, y-19,
        x-8, y+5,
        x+8, y+5
    ], WHITE)


def draw_hud():
    canvas.create_rectangle(
        20, 18, W-20, 72,
        fill="#10172D", outline="#26385D", width=2
    )

    text(105, 34, "NEBULA STRIKE", 14, CYAN)
    text(360, 34, f"SCORE  {score:06}", 15)
    text(555, 34, f"WAVE  {level}", 14, PURPLE)

    # Health bar
    canvas.create_rectangle(
        655, 29, 765, 43,
        fill="#252B45", outline=""
    )

    canvas.create_rectangle(
        655, 29, 655 + 110*max(0, health)/100, 43,
        fill=CYAN if health > 30 else PINK,
        outline=""
    )

    text(708, 55, "SHIELD", 9, WHITE)


def show_menu():
    global state
    state = "menu"

    make_background()

    text(W//2, 220, "N E B U L A", 42, CYAN)
    text(W//2, 275, "S T R I K E", 25, WHITE)

    text(W//2, 345, "GALACTIC COMBAT SYSTEM", 13, PURPLE)

    canvas.create_rectangle(
        265, 405, 535, 465,
        fill="#13223C", outline=CYAN, width=2
    )

    text(W//2, 435, "START MISSION", 17, WHITE)

    text(W//2, 510, "MOVE  :  A / D  or  ARROW KEYS", 12)
    text(W//2, 540, "FIRE  :  SPACEBAR", 12)
    text(W//2, 620, "SURVIVE THE WAVES. DEFEND THE GALAXY.", 11, PURPLE)

    animate_menu()


def animate_menu():
    if state != "menu":
        return

    for item in stars:
        obj, speed, size = item
        canvas.move(obj, 0, speed)

        coords = canvas.coords(obj)

        if coords and coords[1] > H:
            x = random.randint(0, W)
            canvas.coords(obj, x, 0, x+size, size)

    root.after(35, animate_menu)


def start_game(event=None):
    global state, score, health, level
    global player_x, player_y, frame

    if state == "playing":
        return

    state = "playing"
    score = 0
    health = 100
    level = 1
    frame = 0

    player_x = W // 2
    player_y = H - 100

    bullets.clear()
    enemies.clear()
    particles.clear()

    canvas.delete("all")
    make_background()

    game_loop()


def fire(event=None):
    if state != "playing":
        return

    bullets.append({
        "x": player_x,
        "y": player_y - 25,
        "speed": 12
    })


def spawn_enemy():
    x = random.randint(45, W-45)

    enemies.append({
        "x": x,
        "y": 95,
        "hp": 1 if level < 3 else 2,
        "speed": random.uniform(1.5, 2.7) + level*0.25,
        "phase": random.random()*6
    })


def explosion(x, y, color):
    for _ in range(14):
        angle = random.random()*math.pi*2
        speed = random.uniform(1, 5)

        particles.append({
            "x": x, "y": y,
            "dx": math.cos(angle)*speed,
            "dy": math.sin(angle)*speed,
            "life": 18,
            "color": color
        })


def game_loop():
    global frame, player_x, health, score, level, state

    if state != "playing":
        return

    frame += 1

    canvas.delete("all")

    # Starfield animation
    for item in stars:
        obj, speed, size = item

        canvas.move(obj, 0, speed)

        coords = canvas.coords(obj)

        if coords and coords[1] > H:
            x = random.randint(0, W)
            canvas.coords(obj, x, 0, x+size, size)

    # Player movement
    if "Left" in keys or "a" in keys:
        player_x -= 7

    if "Right" in keys or "d" in keys:
        player_x += 7

    player_x = max(35, min(W-35, player_x))

    # Player bullets
    if "space" in keys and frame % 9 == 0:
        fire()

    for bullet in bullets[:]:
        bullet["y"] -= bullet["speed"]

        x, y = bullet["x"], bullet["y"]

        canvas.create_line(
            x, y+12, x, y-7,
            fill=PURPLE, width=7
        )

        canvas.create_line(
            x, y+10, x, y-8,
            fill=CYAN, width=3
        )

        if y < 80:
            bullets.remove(bullet)

    # Enemy waves
    spawn_delay = max(18, 55-level*3)

    if frame % spawn_delay == 0:
        spawn_enemy()

    for enemy in enemies[:]:
        enemy["y"] += enemy["speed"]
        enemy["x"] += math.sin(
            enemy["y"]*0.025 + enemy["phase"]
        )*2

        x, y = enemy["x"], enemy["y"]

        # Enemy craft
        polygon([
            x, y+20,
            x-24, y-10,
            x-10, y-7,
            x, y-19,
            x+10, y-7,
            x+24, y-10
        ], PINK, WHITE)

        # Collision with bullets
        hit = False

        for bullet in bullets[:]:
            if abs(bullet["x"]-x) < 25 and abs(bullet["y"]-y) < 24:
                bullets.remove(bullet)
                enemy["hp"] -= 1
                hit = True
                break

        if hit and enemy["hp"] <= 0:
            explosion(x, y, PINK)
            enemies.remove(enemy)
            score += 100
            level = 1 + score // 1000
            continue

        # Enemy hits player
        if abs(x-player_x) < 28 and abs(y-player_y) < 30:
            explosion(x, y, PINK)
            enemies.remove(enemy)
            health -= 20
            continue

        # Enemy escapes
        if y > H:
            enemies.remove(enemy)
            health -= 10

    # Particle effects
    for p in particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 1

        r = max(1, p["life"]//3)

        canvas.create_oval(
            p["x"]-r, p["y"]-r,
            p["x"]+r, p["y"]+r,
            fill=p["color"], outline=""
        )

        if p["life"] <= 0:
            particles.remove(p)

    draw_player()
    draw_hud()

    if health <= 0:
        state = "over"

        text(W//2, H//2-35, "MISSION FAILED", 34, PINK)

        text(
            W//2, H//2+15,
            f"FINAL SCORE: {score}", 20, WHITE
        )

        text(
            W//2, H//2+65,
            "PRESS ENTER TO PLAY AGAIN", 13, CYAN
        )

        return

    root.after(25, game_loop)


def key_down(event):
    key = event.keysym

    keys.add(key)

    if key == "Return" and state in ("menu", "over"):
        start_game()


def key_up(event):
    keys.discard(event.keysym)


root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)

show_menu()
root.mainloop()

