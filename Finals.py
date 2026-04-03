import pygame
import sys
import math
import os
import random

pygame.init()

WIDTH, HEIGHT = 750, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bad Dog")
clock = pygame.time.Clock()
FPS = 60

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Load images ───────────────────────────────────────────────────────────────
def load_img(name, h, remove_black=False):
    path = os.path.join(SCRIPT_DIR, name)
    if not os.path.exists(path):
        print(f"Missing: {path}"); pygame.quit(); sys.exit()
    img = pygame.image.load(path).convert_alpha()
    if remove_black:
        for px in range(img.get_width()):
            for py in range(img.get_height()):
                r, g, b, a = img.get_at((px, py))
                if r < 20 and g < 20 and b < 20:
                    img.set_at((px, py), (0, 0, 0, 0))
    aspect = img.get_width() / img.get_height()
    w = int(h * aspect)
    return pygame.transform.scale(img, (w, h))

DOG_BASE = load_img("dogie.png", 80)
DOG_R    = DOG_BASE
DOG_L    = pygame.transform.flip(DOG_R, True, False)

NPC_BASE = load_img("human.png", 96, remove_black=True)
NPC_R    = NPC_BASE
NPC_L    = pygame.transform.flip(NPC_R, True, False)

OBJ_BASE = load_img("objects.png", 40, remove_black=True)
FOOD_IMG = load_img("food.png", 36, remove_black=True)

DOG_W  = DOG_R.get_width();  DOG_H  = DOG_R.get_height()
NPC_W  = NPC_R.get_width();  NPC_H  = NPC_R.get_height()
OBJ_W  = OBJ_BASE.get_width(); OBJ_H = OBJ_BASE.get_height()
FOOD_W = FOOD_IMG.get_width(); FOOD_H = FOOD_IMG.get_height()

# ── Colors ────────────────────────────────────────────────────────────────────
BG_COLOR   = (245, 240, 232)
GROUND_Y   = HEIGHT - 80
SHADOW_COL = (180, 165, 145, 120)
DARK_BROWN = (80, 40, 15)
TAN        = (210, 165, 100)
POWER_COL  = (255, 80, 180)

# ── Physics ───────────────────────────────────────────────────────────────────
GRAVITY    = 0.55
JUMP_VEL   = -13.0
WALK_SPEED = 3.0
BOB_AMP    = 4
BOB_FREQ   = 6.0
WAG_FREQ   = 8.0
WAG_AMP    = 6

# ── Fonts ─────────────────────────────────────────────────────────────────────
title_font = pygame.font.SysFont("Arial", 72, bold=True)
sub_font   = pygame.font.SysFont("Arial", 18)
btn_font   = pygame.font.SysFont("Arial", 22, bold=True)
hint_font  = pygame.font.SysFont("Arial", 15)
hud_font   = pygame.font.SysFont("Arial", 20, bold=True)
power_font = pygame.font.SysFont("Arial", 16, bold=True)

# ── Button rects ──────────────────────────────────────────────────────────────
BTN_SIZE  = 64
BTN_PAD   = 20
BTN_Y     = HEIGHT - BTN_SIZE - BTN_PAD
btn_left  = pygame.Rect(BTN_PAD, BTN_Y, BTN_SIZE, BTN_SIZE)
btn_right = pygame.Rect(BTN_PAD + BTN_SIZE + 10, BTN_Y, BTN_SIZE, BTN_SIZE)
btn_jump  = pygame.Rect(WIDTH - BTN_SIZE - BTN_PAD, BTN_Y, BTN_SIZE, BTN_SIZE)

menu_btn_w, menu_btn_h = 200, 52
start_btn  = pygame.Rect(WIDTH//2 - menu_btn_w//2, 240, menu_btn_w, menu_btn_h)
quit_btn   = pygame.Rect(WIDTH//2 - menu_btn_w//2, 308, menu_btn_w, menu_btn_h)
retry_btn  = pygame.Rect(WIDTH//2 - menu_btn_w//2, 270, menu_btn_w, menu_btn_h)
gomenu_btn = pygame.Rect(WIDTH//2 - menu_btn_w//2, 338, menu_btn_w, menu_btn_h)

final_score = 0

# ── Scenes ────────────────────────────────────────────────────────────────────
STATE_MENU     = "menu"
STATE_GAME     = "game"
STATE_GAMEOVER = "gameover"
scene = STATE_MENU

y_base = float(GROUND_Y - DOG_H)
NPC_Y  = GROUND_Y - NPC_H

# ── Game state vars (reset each game) ────────────────────────────────────────
dog_x = dog_y = dog_vy = 0.0
on_ground = True
facing = moving = False
jumps_left = 2
walk_time = wag_time = idle_time = 0.0
lives = hit_flash = 0
npc_x = npc_dir = npc_throw_timer = npc_walk_time = 0.0
npc_hit_flash = 0.0
projectiles = []
score = dodge_timer = 0.0

# Power-up state
power_active   = False
power_timer    = 0.0
POWER_DURATION = 4.0
food_item      = None        # {x, y, bob_t}
food_spawn_timer = 0.0
FOOD_SPAWN_MIN = 5.0
FOOD_SPAWN_MAX = 12.0

# Menu
menu_time    = 0.0
dog_menu_x   = float(-DOG_W)
dog_menu_dir = 1

# Bite effect particles
bite_particles = []


def reset_game():
    global dog_x, dog_y, dog_vy, on_ground, facing, moving, jumps_left
    global walk_time, wag_time, idle_time, lives, hit_flash
    global npc_x, npc_dir, npc_throw_timer, npc_walk_time, npc_hit_flash
    global projectiles, score, dodge_timer
    global power_active, power_timer, food_item, food_spawn_timer
    global bite_particles
    dog_x = float(WIDTH // 2)
    dog_y = y_base
    dog_vy = 0.0
    on_ground = True
    facing = 1
    moving = False
    jumps_left = 2
    walk_time = wag_time = idle_time = 0.0
    lives = 3
    hit_flash = 0.0
    npc_x = float(WIDTH - NPC_W - 20)
    npc_dir = -1
    npc_throw_timer = 2.0
    npc_walk_time = 0.0
    npc_hit_flash = 0.0
    projectiles = []
    score = 0
    dodge_timer = 0.0
    power_active = False
    power_timer  = 0.0
    food_item    = None
    food_spawn_timer = random.uniform(FOOD_SPAWN_MIN, FOOD_SPAWN_MAX)
    bite_particles = []


def throw_object():
    sx = npc_x + (NPC_W * 0.2 if npc_dir == -1 else NPC_W * 0.8)
    sy = NPC_Y + NPC_H * 0.35
    tx = dog_x + DOG_W // 2
    ty = dog_y + DOG_H // 2
    dx, dy = tx - sx, ty - sy
    dist = math.hypot(dx, dy) or 1
    speed = random.uniform(5.0, 8.0)
    vx = dx / dist * speed
    vy = dy / dist * speed - random.uniform(1.5, 3.0)
    projectiles.append({"x": sx, "y": sy, "vx": vx, "vy": vy,
                        "angle": 0.0, "spin": random.uniform(-8, 8)})


def spawn_food():
    global food_item
    fx = random.uniform(60, WIDTH - 60 - FOOD_W)
    food_item = {"x": fx, "y": float(GROUND_Y - FOOD_H - 4), "bob_t": 0.0}


def spawn_bite_particles(cx, cy):
    for _ in range(18):
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(3, 9)
        bite_particles.append({
            "x": cx, "y": cy,
            "vx": math.cos(angle)*speed,
            "vy": math.sin(angle)*speed - 2,
            "life": 1.0,
            "col": random.choice([(255,80,80),(255,200,50),(255,120,30)]),
            "size": random.randint(4,9),
        })


def draw_shadow(surf, cx, scale=1.0):
    w = int(50 * scale); h = int(8 * scale)
    if w < 2 or h < 2: return
    s = pygame.Surface((w*2, h*2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, SHADOW_COL, s.get_rect())
    surf.blit(s, (cx-w, GROUND_Y-h))


def blit_rotated(surf, image, cx, cy, angle_deg):
    rot  = pygame.transform.rotate(image, angle_deg)
    rect = rot.get_rect(center=(cx, cy))
    surf.blit(rot, rect)


def draw_game_button(surf, rect, label, pressed):
    col = (180,155,120) if pressed else (210,190,160)
    pygame.draw.rect(surf, col,          rect, border_radius=12)
    pygame.draw.rect(surf, (140,110,80), rect, 3, border_radius=12)
    txt = btn_font.render(label, True, (80,50,20))
    surf.blit(txt, txt.get_rect(center=rect.center))


def draw_menu_button(surf, rect, label, hovered):
    col = (210,175,120) if hovered else (235,210,170)
    pygame.draw.rect(surf, (160,130,90), rect.move(4,4), border_radius=14)
    pygame.draw.rect(surf, col,          rect, border_radius=14)
    pygame.draw.rect(surf, DARK_BROWN,   rect, 3, border_radius=14)
    txt = btn_font.render(label, True, DARK_BROWN)
    surf.blit(txt, txt.get_rect(center=rect.center))


def draw_background(surf):
    surf.fill(BG_COLOR)
    for gx in range(0, WIDTH, 18):
        for gy in range(0, HEIGHT, 18):
            pygame.draw.circle(surf, (225,215,205), (gx,gy), 1)
    pygame.draw.line(surf, (200,185,165), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)


def draw_lives(surf, lv):
    hc = (220,60,60)
    for i in range(3):
        cx = 20 + i*28; cy = 36
        filled = i < lv
        col = hc if filled else (180,160,140)
        pygame.draw.circle(surf, col, (cx-5, cy-3), 6)
        pygame.draw.circle(surf, col, (cx+5, cy-3), 6)
        pygame.draw.polygon(surf, col, [(cx-10,cy),(cx,cy+10),(cx+10,cy)])


def draw_power_bar(surf, timer, duration):
    bw, bh = 120, 12
    bx = WIDTH//2 - bw//2
    by = 12
    pygame.draw.rect(surf, (200,180,160), (bx, by, bw, bh), border_radius=6)
    fill = int(bw * (timer / duration))
    pygame.draw.rect(surf, POWER_COL,    (bx, by, fill, bh), border_radius=6)
    pygame.draw.rect(surf, DARK_BROWN,   (bx, by, bw, bh), 2, border_radius=6)
    lbl = power_font.render("🐾 BITE MODE!", True, POWER_COL)
    surf.blit(lbl, (WIDTH//2 - lbl.get_width()//2, by + bh + 2))


running = True

while running:
    dt = clock.tick(FPS) / 1000.0
    mx, my = pygame.mouse.get_pos()

    # ══════════════════════════════════════════════════════════════════════════
    #  MENU
    # ══════════════════════════════════════════════════════════════════════════
    if scene == STATE_MENU:
        menu_time  += dt
        dog_menu_x += WALK_SPEED * 0.8 * dog_menu_dir
        if dog_menu_x > WIDTH + DOG_W:  dog_menu_x = float(-DOG_W);       dog_menu_dir =  1
        if dog_menu_x < -DOG_W * 2:     dog_menu_x = float(WIDTH + DOG_W); dog_menu_dir = -1

        menu_bob   = math.sin(menu_time * BOB_FREQ * 2*math.pi) * BOB_AMP
        menu_dog_y = y_base + menu_bob
        menu_sway  = math.sin(menu_time * WAG_FREQ * 2*math.pi) * WAG_AMP * 0.35

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos): reset_game(); scene = STATE_GAME
                if quit_btn.collidepoint(event.pos):  running = False
            if event.type == pygame.FINGERDOWN:
                tx,ty = int(event.x*WIDTH), int(event.y*HEIGHT)
                if start_btn.collidepoint(tx,ty): reset_game(); scene = STATE_GAME
                if quit_btn.collidepoint(tx,ty):  running = False

        draw_background(screen)
        menu_cx = int(dog_menu_x + DOG_W//2)
        draw_shadow(screen, menu_cx)
        img = DOG_R if dog_menu_dir==1 else DOG_L
        blit_rotated(screen, img, menu_cx, int(menu_dog_y+DOG_H//2), menu_sway)

        ts = title_font.render("BAD DOG", True, (160,110,50))
        tt = title_font.render("BAD DOG", True, DARK_BROWN)
        txp = WIDTH//2 - tt.get_width()//2
        screen.blit(ts,(txp+4,74)); screen.blit(tt,(txp,70))
        sub = sub_font.render("a very naughty pixel puppy", True, TAN)
        screen.blit(sub,(WIDTH//2-sub.get_width()//2, 152))

        draw_menu_button(screen, start_btn, "▶  START", start_btn.collidepoint(mx,my))
        draw_menu_button(screen, quit_btn,  "✕  QUIT",  quit_btn.collidepoint(mx,my))
        hint = hint_font.render("A/D move   SPACE jump   ESC menu", True, (180,160,135))
        screen.blit(hint,(WIDTH//2-hint.get_width()//2, HEIGHT-28))
        pygame.display.flip()

    # ══════════════════════════════════════════════════════════════════════════
    #  GAME
    # ══════════════════════════════════════════════════════════════════════════
    elif scene == STATE_GAME:
        touch_jump_event = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: scene = STATE_MENU
                if event.key in (pygame.K_SPACE, pygame.K_w) and jumps_left > 0:
                    dog_vy = JUMP_VEL; on_ground = False; jumps_left -= 1
            if event.type == pygame.FINGERDOWN:
                tx,ty = int(event.x*WIDTH), int(event.y*HEIGHT)
                if btn_jump.collidepoint(tx,ty) and jumps_left > 0: touch_jump_event = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_jump.collidepoint(event.pos) and jumps_left > 0: touch_jump_event = True

        if touch_jump_event and jumps_left > 0:
            dog_vy = JUMP_VEL; on_ground = False; jumps_left -= 1

        mb          = pygame.mouse.get_pressed()[0]
        touch_left  = mb and btn_left.collidepoint(mx,my)
        touch_right = mb and btn_right.collidepoint(mx,my)

        keys = pygame.key.get_pressed()
        move_x = 0
        if keys[pygame.K_a] or touch_left:  move_x = -WALK_SPEED; facing = -1
        if keys[pygame.K_d] or touch_right: move_x =  WALK_SPEED; facing =  1
        moving = move_x != 0

        dog_x = max(0.0, min(float(WIDTH - DOG_W), dog_x + move_x))

        if not on_ground:
            dog_vy += GRAVITY
            dog_y  += dog_vy
            if dog_y >= y_base:
                dog_y = y_base; dog_vy = 0.0; on_ground = True; jumps_left = 2

        if moving and on_ground:
            walk_time += dt; idle_time = 0.0
        else:
            walk_time = 0.0; idle_time += dt
        wag_time  += dt
        hit_flash  = max(0.0, hit_flash - dt)

        bob    = math.sin(walk_time*BOB_FREQ*2*math.pi)*BOB_AMP if (on_ground and moving) else 0.0
        draw_y = dog_y + bob

        height_above = max(0.0, y_base - dog_y)
        shadow_scale = max(0.0, 1.0 - height_above/(DOG_H*0.4))

        if not on_ground:
            draw_angle = facing*(-12 if dog_vy<0 else 8)
        elif moving:
            draw_angle = math.sin(wag_time*WAG_FREQ*2*math.pi)*WAG_AMP*0.35
        else:
            draw_angle = math.sin(idle_time*1.5*2*math.pi)*1.5

        # ── Power-up timer ────────────────────────────────────────────────────
        if power_active:
            power_timer -= dt
            if power_timer <= 0:
                power_active = False
                power_timer  = 0.0

        # ── Food spawn ────────────────────────────────────────────────────────
        if food_item is None and not power_active:
            food_spawn_timer -= dt
            if food_spawn_timer <= 0:
                spawn_food()
                food_spawn_timer = random.uniform(FOOD_SPAWN_MIN, FOOD_SPAWN_MAX)

        # Animate food bob
        if food_item:
            food_item["bob_t"] += dt
            food_bob = math.sin(food_item["bob_t"]*4)*5
            food_draw_y = food_item["y"] + food_bob

            # Dog eats food
            dog_rect  = pygame.Rect(int(dog_x)+4, int(draw_y)+4, DOG_W-8, DOG_H-8)
            food_rect = pygame.Rect(int(food_item["x"]), int(food_draw_y), FOOD_W, FOOD_H)
            if dog_rect.colliderect(food_rect):
                food_item    = None
                power_active = True
                power_timer  = POWER_DURATION
                spawn_bite_particles(int(dog_x+DOG_W//2), int(draw_y+DOG_H//2))

        # ── NPC AI ────────────────────────────────────────────────────────────
        npc_walk_time += dt
        npc_hit_flash = max(0.0, npc_hit_flash - dt)
        dist_to_dog = dog_x - npc_x

        if power_active:
            # Dog is powered up — NPC runs away!
            npc_dir = 1 if dog_x < npc_x else -1
            npc_speed_cur = 2.8
        else:
            if abs(dist_to_dog) > 200:
                npc_dir = 1 if dist_to_dog > 0 else -1
            else:
                npc_dir = -1 if npc_x > WIDTH*0.6 else 1
            npc_speed_cur = 1.2

        npc_x += npc_speed_cur * npc_dir
        npc_x  = max(0.0, min(float(WIDTH-NPC_W), npc_x))
        npc_bob    = math.sin(npc_walk_time*BOB_FREQ*2*math.pi)*3
        npc_facing = -1 if dog_x < npc_x else 1

        # Throw objects only when NOT powered-up mode
        if not power_active:
            npc_throw_timer -= dt
            if npc_throw_timer <= 0:
                throw_object()
                npc_throw_timer = random.uniform(1.8, 3.5)

        # ── Dog bites NPC during power-up ────────────────────────────────────
        if power_active:
            npc_rect = pygame.Rect(int(npc_x)+8, int(NPC_Y+npc_bob)+8, NPC_W-16, NPC_H-16)
            dog_rect = pygame.Rect(int(dog_x)+4, int(draw_y)+4, DOG_W-8, DOG_H-8)
            if dog_rect.colliderect(npc_rect) and npc_hit_flash <= 0:
                score += 5
                npc_hit_flash = 1.0  # 1 second invincibility
                spawn_bite_particles(int(npc_x+NPC_W//2), int(NPC_Y+NPC_H//2))
                # push NPC away
                npc_x += 60 * npc_dir

        # ── Projectiles ───────────────────────────────────────────────────────
        dog_rect = pygame.Rect(int(dog_x)+8, int(draw_y)+8, DOG_W-16, DOG_H-16)
        for p in projectiles[:]:
            p["vy"] += GRAVITY*0.6
            p["x"]  += p["vx"];  p["y"] += p["vy"]
            p["angle"] += p["spin"]
            if p["y"] > GROUND_Y or p["x"] < -OBJ_W or p["x"] > WIDTH+OBJ_W:
                projectiles.remove(p); continue
            # power-up: deflect projectiles
            obj_rect = pygame.Rect(int(p["x"]), int(p["y"]), OBJ_W, OBJ_H)
            if dog_rect.colliderect(obj_rect):
                if power_active:
                    p["vx"] *= -1.2; p["vy"] = -6   # deflect back!
                elif hit_flash <= 0:
                    lives -= 1; hit_flash = 1.2
                    projectiles.remove(p)
                    if lives <= 0:
                        final_score = score
                        scene = STATE_GAMEOVER
                continue

        # Score
        dodge_timer += dt
        if dodge_timer >= 1.0:
            score += 1; dodge_timer = 0.0

        # Bite particles
        for bp in bite_particles[:]:
            bp["x"] += bp["vx"]; bp["y"] += bp["vy"]
            bp["vy"] += 0.3;     bp["life"] -= dt*1.5
            if bp["life"] <= 0: bite_particles.remove(bp)

        # ── Draw ─────────────────────────────────────────────────────────────
        draw_background(screen)

        # Power-up glow on ground
        if power_active:
            glow = pygame.Surface((WIDTH, GROUND_Y), pygame.SRCALPHA)
            glow.fill((255,80,180, 18))
            screen.blit(glow, (0,0))

        # Food item
        if food_item:
            # glow ring
            glow_r = pygame.Surface((FOOD_W+20, FOOD_H+20), pygame.SRCALPHA)
            t = food_item["bob_t"]
            alpha = int(80 + 60*math.sin(t*4))
            pygame.draw.ellipse(glow_r, (255,100,200,alpha), glow_r.get_rect())
            screen.blit(glow_r, (int(food_item["x"])-10, int(food_draw_y)-10))
            screen.blit(FOOD_IMG, (int(food_item["x"]), int(food_draw_y)))

        # NPC shadow + sprite
        npc_cx = int(npc_x + NPC_W//2)
        draw_shadow(screen, npc_cx)
        npc_img = NPC_L if npc_facing==-1 else NPC_R
        # NPC shakes when dog is powered up
        shake = random.randint(-2,2) if power_active else 0
        # Flash white during invincibility after being bitten
        if npc_hit_flash > 0 and int(npc_hit_flash * 8) % 2 == 0:
            npc_draw = npc_img.copy()
            npc_draw.fill((255, 255, 255, 160), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(npc_draw, (int(npc_x)+shake, int(NPC_Y+npc_bob)))
        else:
            screen.blit(npc_img, (int(npc_x)+shake, int(NPC_Y+npc_bob)))

        # Projectiles
        for p in projectiles:
            blit_rotated(screen, OBJ_BASE, int(p["x"]+OBJ_W//2), int(p["y"]+OBJ_H//2), p["angle"])

        # Bite particles
        for bp in bite_particles:
            alpha = int(bp["life"]*220)
            size  = max(1, int(bp["size"]*bp["life"]))
            s = pygame.Surface((size,size), pygame.SRCALPHA)
            r,g,b = bp["col"]
            s.fill((r,g,b,alpha))
            screen.blit(s, (int(bp["x"]-size//2), int(bp["y"]-size//2)))

        # Dog shadow + sprite
        dog_cx = int(dog_x + DOG_W//2)
        draw_shadow(screen, dog_cx, shadow_scale)  # FIXED: removed extra GROUND_Y argument

        dog_img = DOG_R if facing==1 else DOG_L
        # Power-up: tint dog pink
        if power_active:
            tinted = dog_img.copy()
            tinted.fill((255,100,220,120), special_flags=pygame.BLEND_RGBA_ADD)
            blit_rotated(screen, tinted, int(dog_x+DOG_W//2), int(draw_y+DOG_H//2), draw_angle)
        elif hit_flash > 0 and int(hit_flash*8)%2==0:
            flash = dog_img.copy()
            flash.fill((255,80,80,160), special_flags=pygame.BLEND_RGBA_MULT)
            blit_rotated(screen, flash, int(dog_x+DOG_W//2), int(draw_y+DOG_H//2), draw_angle)
        else:
            blit_rotated(screen, dog_img, int(dog_x+DOG_W//2), int(draw_y+DOG_H//2), draw_angle)

        # On-screen buttons
        draw_game_button(screen, btn_left,  "◀", touch_left)
        draw_game_button(screen, btn_right, "▶", touch_right)
        draw_game_button(screen, btn_jump,  "▲", not on_ground)

        # HUD
        draw_lives(screen, lives)
        score_txt = hud_font.render(f"Score: {score}", True, DARK_BROWN)
        screen.blit(score_txt, (WIDTH - score_txt.get_width()-12, 10))
        hint = hint_font.render("A/D move   SPACE jump   ESC menu", True, (180,160,135))
        screen.blit(hint, (10, 10))

        if power_active:
            draw_power_bar(screen, power_timer, POWER_DURATION)

        pygame.display.flip()

    # ══════════════════════════════════════════════════════════════════════════
    #  GAME OVER
    # ══════════════════════════════════════════════════════════════════════════
    elif scene == STATE_GAMEOVER:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                reset_game(); scene = STATE_MENU
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    reset_game(); scene = STATE_GAME
                if gomenu_btn.collidepoint(event.pos):
                    reset_game(); scene = STATE_MENU
            if event.type == pygame.FINGERDOWN:
                tx, ty = int(event.x*WIDTH), int(event.y*HEIGHT)
                if retry_btn.collidepoint(tx, ty):
                    reset_game(); scene = STATE_GAME
                if gomenu_btn.collidepoint(tx, ty):
                    reset_game(); scene = STATE_MENU

        draw_background(screen)

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 15, 5, 170))
        screen.blit(overlay, (0, 0))

        # "YOU LOSE" title
        lose_shadow = title_font.render("YOU LOSE", True, (100, 40, 10))
        lose_text   = title_font.render("YOU LOSE", True, (220, 70, 50))
        lx = WIDTH//2 - lose_text.get_width()//2
        screen.blit(lose_shadow, (lx+4, 104))
        screen.blit(lose_text,   (lx,   100))

        # Score display
        sc_txt = hud_font.render(f"Final Score: {final_score}", True, TAN)
        screen.blit(sc_txt, (WIDTH//2 - sc_txt.get_width()//2, 200))

        # Buttons
        draw_menu_button(screen, retry_btn,  "↺  RETRY",      retry_btn.collidepoint(mx, my))
        draw_menu_button(screen, gomenu_btn, "⌂  MAIN MENU",  gomenu_btn.collidepoint(mx, my))

        pygame.display.flip()

pygame.quit()
sys.exit()