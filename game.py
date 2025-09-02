import pgzrun

def detect_run_frames(prefix='heroi'):
    names = []
    base = f"{prefix}_correndo"

    i = 0
    while hasattr(images, f"{base}_{i}") and i < 20:
        names.append(f"{base}_{i}")
        i += 1
    if not names:

        i = 1
        while hasattr(images, f"{base}_{i}") and i < 20:
            names.append(f"{base}_{i}")
            i += 1
    if not names:
        if hasattr(images, base) and hasattr(images, f"{prefix}_parado"):
            names = [base, f"{prefix}_parado"]
        elif hasattr(images, base):
            names = [base]
        else:
            names = [f"{prefix}_parado"]
    return names


def play_sfx_hit():
  

    s = None
    try:
        s = getattr(sounds, 'hit')
    except Exception:
        try:
            s = sounds['hit']
        except Exception:
            s = None
    if s is None:
        return
    try:

        s.set_volume(1.0)
        try:
            s.stop()
        except Exception:
            pass
        s.play()
    except Exception:
        pass


def stop_bg_music():
    try:
        music.stop()
    except Exception:
        pass
    try:
        snd = getattr(sounds, 'trilha_sonora')
        snd.stop()
    except Exception:
        pass


def ensure_bg_music():
    """Ativa/desativa BGM conforme music_enabled.
    Preferência: music/trilha_sonora.*; fallback: sounds/trilha_sonora (loop).
    """

    stop_bg_music()
    if not music_enabled:
        return

    try:
        music.play('trilha_sonora')
        return
    except Exception:
        pass

    try:
        snd = getattr(sounds, 'trilha_sonora')
        snd.play(-1)
    except Exception:

        pass


def init_audio_once():
    global audio_inited
    if audio_inited:
        return

    try:
        sounds.hit.set_volume(1.0)
    except Exception:
        pass
    audio_inited = True
from pgzero.rect import Rect

WIDTH = 928
HEIGHT = 793
MAP_WIDTH = 2000
GROUND_LEVEL = 730

game_state = 'menu'
music_enabled = True
lives = 3
current_horde = 1
camera_x = 0
paused = False
btn_pause_ok = Rect(WIDTH/2 - 110, HEIGHT/2 + 40, 220, 56)
selected_skin = 'heroi'  
audio_inited = False


horde_data = {
    1: {'monsters': 3, 'type': 'monstro'},
    2: {'monsters': 7, 'type': 'monstro2'}
}

MENU_BTN_W = 360
MENU_BTN_H = 54
MENU_BTN_X = WIDTH / 2 - MENU_BTN_W / 2
btn_start = Rect(MENU_BTN_X, 480, MENU_BTN_W, MENU_BTN_H)
btn_music = Rect(MENU_BTN_X, 548, MENU_BTN_W, MENU_BTN_H)
btn_exit  = Rect(MENU_BTN_X, 616, MENU_BTN_W, MENU_BTN_H)

SKIN_BTN_W = 220
SKIN_BTN_H = 120
skin_row_y = 330
btn_skin_heroi = Rect(int(WIDTH/2 - (SKIN_BTN_W + 20)), skin_row_y, SKIN_BTN_W, SKIN_BTN_H)
btn_skin_rosa  = Rect(int(WIDTH/2 + 20),               skin_row_y, SKIN_BTN_W, SKIN_BTN_H)

btn_pause_game = Rect(WIDTH - 108, 12, 44, 44)
btn_music_game = Rect(WIDTH - 56, 12, 44, 44)


class Hero:
    def __init__(self, skin_prefix='heroi'):

        self.skin_prefix = skin_prefix
        self.actor = Actor(f'{self.skin_prefix}_parado', (200, GROUND_LEVEL - 50))
        self.vx = 0
        self.vy = 0
        self.is_jumping = False
        self.jump_speed = -12
        self.run_speed = 7
        self.facing_right = False


        self.run_frames = detect_run_frames(self.skin_prefix)
        self.run_anim_index = 0
        self.run_anim_counter = 0
        self.run_anim_speed = 6


        self.weapon = Actor('weapon', (self.actor.x + 15, self.actor.y))
        self.weapon.angle = 0

        self.is_attacking = False
        self.attack_forward = True
        self.weapon_speed = 12
        self.weapon_reach = 50
        self.attack_hits = set()

    def update(self):

        self.vy += 1
        self.actor.y += self.vy
        self.actor.x += self.vx


        if self.vx > 0 and not self.is_jumping:
            self.facing_right = True
        elif self.vx < 0 and not self.is_jumping:
            self.facing_right = False


        
        if self.vx != 0 and not self.is_jumping and len(self.run_frames) > 1:
            self.run_anim_counter += 1
            if self.run_anim_counter >= self.run_anim_speed:
                self.run_anim_counter = 0
                self.run_anim_index = (self.run_anim_index + 1) % len(self.run_frames)


        if self.vx != 0 and not self.is_jumping:
            base = self.run_frames[self.run_anim_index] if self.run_frames else f'{self.skin_prefix}_correndo'
        else:
            base = f'{self.skin_prefix}_parado'

        if self.facing_right and hasattr(images, base + '_d'):
            self.actor.image = base + '_d'
        else:
            self.actor.image = base


        if self.actor.y > GROUND_LEVEL:
            self.actor.y = GROUND_LEVEL
            self.vy = 0
            self.is_jumping = False


        self.weapon.y = self.actor.y


        if not self.is_attacking:
            edge = int(self.actor.width / 2) - 4
            forward = 8
            offset = edge + forward
            self.weapon.x = self.actor.x + (offset if self.facing_right else -offset)
        else:
            self.animate_weapon()


        self.weapon.angle = 0 if self.facing_right else 180

    def animate_weapon(self):
        
        direction = 1 if self.facing_right else -1
        base_offset = int(self.actor.width / 2) - 4 + 8  
        base_x = self.actor.x + (base_offset if self.facing_right else -base_offset)
        if self.attack_forward:
            self.weapon.x += self.weapon_speed * direction
            
            if (direction == 1 and self.weapon.x >= self.actor.x + self.weapon_reach) or \
               (direction == -1 and self.weapon.x <= self.actor.x - self.weapon_reach):
                self.attack_forward = False
        else:
            
            self.weapon.x -= self.weapon_speed * direction
            if (direction == 1 and self.weapon.x <= base_x) or \
               (direction == -1 and self.weapon.x >= base_x):
                
                self.weapon.x = base_x
                self.is_attacking = False
                self.attack_forward = True
                self.attack_hits.clear()  

    def start_attack(self):
        """Inicia ataque se não houver um em andamento."""
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_forward = True

            self.weapon.x = self.actor.x + (15 if self.facing_right else -15)
            self.attack_hits.clear()

    def get_weapon_hitbox(self):
        return self.weapon

    def get_actor_hitbox(self):
        return self.actor


class Monster:
    def __init__(self, x, y, image_name):
        self.actor = Actor(image_name, (x, y))
        self.speed = 0.6
        self.max_hp = 3
        self.hp = self.max_hp

        self.actor.bottom = GROUND_LEVEL

    def update(self, hero_pos):

        if self.actor.x < hero_pos[0]:
            self.actor.x += self.speed
        else:
            self.actor.x -= self.speed

    def draw(self):

        original_x = self.actor.x
        self.actor.x = self.actor.x - camera_x
        self.actor.draw()


        bar_w = 40
        bar_h = 6
        x = self.actor.x - bar_w / 2
        y = self.actor.y - self.actor.height / 2 - 12

        screen.draw.filled_rect(Rect((x, y), (bar_w, bar_h)), (180, 40, 40))

        current_w = int(bar_w * (self.hp / self.max_hp))
        screen.draw.filled_rect(Rect((x, y), (current_w, bar_h)), (40, 200, 40))


        self.actor.x = original_x
    
    def damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            if self in monsters:
                monsters.remove(self)


def draw_hud_buttons():

    def round_button(rect, fill, border=(210, 230, 245)):
        x, y, w, h = rect.x, rect.y, rect.w, rect.h
        r = 8
        screen.draw.filled_rect(Rect((x + r, y), (w - 2*r, h)), fill)
        screen.draw.filled_rect(Rect((x, y + r), (w, h - 2*r)), fill)
        screen.draw.filled_circle((x + r, y + r), r, fill)
        screen.draw.filled_circle((x + w - r, y + r), r, fill)
        screen.draw.filled_circle((x + r, y + h - r), r, fill)
        screen.draw.filled_circle((x + w - r, y + h - r), r, fill)
        screen.draw.rect(Rect((x, y), (w, h)), border)

    def icon_pause(center, color):
        x, y = center
        screen.draw.filled_rect(Rect((x - 8, y - 12), (6, 24)), color)
        screen.draw.filled_rect(Rect((x + 2, y - 12), (6, 24)), color)

    def icon_play(center, color):
        x, y = center

        p1 = (x - 8, y - 12)
        p2 = (x - 8, y + 12)
        p3 = (x + 12, y)
        screen.draw.line(p1, p2, color)
        screen.draw.line(p2, p3, color)
        screen.draw.line(p3, p1, color)

    def icon_music(center, color, crossed=False):
        x, y = center

        screen.draw.filled_circle((x - 5, y + 6), 5, color)

        screen.draw.line((x - 1, y + 6), (x - 1, y - 10), color)

        screen.draw.line((x - 1, y - 10), (x + 9, y - 6), color)
        if crossed:
            screen.draw.line((x - 14, y - 14), (x + 14, y + 14), color)


    pause_fill = (26, 200, 230) if not paused else (255, 190, 80)
    music_fill = (60, 140, 250) if music_enabled else (120, 120, 130)
    icon_col = (12, 16, 22)


    round_button(btn_pause_game, pause_fill)
    c1 = (btn_pause_game.x + btn_pause_game.w // 2, btn_pause_game.y + btn_pause_game.h // 2)
    if paused:
        icon_play(c1, icon_col)
    else:
        icon_pause(c1, icon_col)


    round_button(btn_music_game, music_fill)
    c2 = (btn_music_game.x + btn_music_game.w // 2, btn_music_game.y + btn_music_game.h // 2)
    icon_music(c2, icon_col, crossed=not music_enabled)


def draw_pause_overlay():

    panel_w, panel_h = 520, 220
    panel_x, panel_y = WIDTH//2 - panel_w//2, HEIGHT//2 - panel_h//2
    panel_rect = Rect(panel_x, panel_y, panel_w, panel_h)


    def rounded(rect, color, r=16):
        x, y, w, h = rect
        screen.draw.filled_rect(Rect((x + r, y), (w - 2*r, h)), color)
        screen.draw.filled_rect(Rect((x, y + r), (w, h - 2*r)), color)
        screen.draw.filled_circle((x + r, y + r), r, color)
        screen.draw.filled_circle((x + w - r, y + r), r, color)
        screen.draw.filled_circle((x + r, y + h - r), r, color)
        screen.draw.filled_circle((x + w - r, y + h - r), r, color)

    rounded(panel_rect, (24, 30, 44))
    screen.draw.rect(panel_rect, (150, 200, 255))


    screen.draw.text('Este jogo foi pausado', center=(WIDTH/2, panel_y + 72), fontsize=44, color=(230, 245, 255))
    screen.draw.text('Aperte OK para continuar', center=(WIDTH/2, panel_y + 115), fontsize=28, color=(180, 210, 235))


    global btn_pause_ok
    btn_pause_ok = Rect(WIDTH/2 - 110, panel_y + panel_h - 70, 220, 56)
    rounded(btn_pause_ok, (20, 220, 240), 14)
    inner = btn_pause_ok.inflate(-4, -4)
    rounded(inner, (30, 180, 200), 12)
    screen.draw.text('OK', center=btn_pause_ok.center, fontsize=36, color=(10, 20, 28))


hero = Hero(selected_skin)
door = None
cacti = []
platforms = [Rect(0, GROUND_LEVEL, MAP_WIDTH, 33)]
monsters = []




def spawn_horda(horda_number):
    monsters.clear()
    horda_info = horde_data.get(horda_number)
    if horda_info:

        for i in range(horda_info['monsters']):
            x = MAP_WIDTH + 100 + i * 90
            y = GROUND_LEVEL
            m = Monster(x, y, horda_info['type'])
            monsters.append(m)


def start_game():
    global game_state, camera_x, lives, current_horde, hero
    game_state = 'playing'
    lives = 3
    current_horde = 1
    camera_x = 0

    hero = Hero(selected_skin)
    hero.actor.pos = (200, GROUND_LEVEL - 50)
    offset = int(hero.actor.width / 2) - 4
    hero.weapon.pos = (hero.actor.x - offset, hero.actor.y)
    spawn_horda(current_horde)
    ensure_bg_music()


def restart_game():
    start_game()


def next_horde():
    global current_horde, game_state
    current_horde += 1
    if current_horde in horde_data:
        spawn_horda(current_horde)
    else:
        game_state = 'victory'


def handle_menu_click(pos):
    global music_enabled, selected_skin
    if btn_skin_heroi.collidepoint(pos):
        selected_skin = 'heroi'
    elif btn_skin_rosa.collidepoint(pos):
        selected_skin = 'heroi_rosa'
    elif btn_start.collidepoint(pos):
        start_game()
    elif btn_music.collidepoint(pos):
        music_enabled = not music_enabled
        ensure_bg_music()
    elif btn_exit.collidepoint(pos):
        exit()


def draw():
    init_audio_once()

    screen.clear()

    bg_w, bg_h = images.background.get_size()
    start_x = (camera_x // bg_w) * bg_w
    x = start_x
    while x < camera_x + WIDTH:
        screen.blit('background', (x - camera_x, 0))
        x += bg_w


    def draw_with_camera(actor):
        original_x = actor.x
        actor.x = actor.x - camera_x
        actor.draw()
        actor.x = original_x


    draw_with_camera(hero.actor)
    draw_with_camera(hero.weapon)


    for m in monsters:
        m.draw()


    screen.draw.text('LIFES', topleft=(10, 10), fontsize=32, color='red')
    for i in range(lives):
        screen.blit('heart', (100 + i * 36, 8))


    if game_state == 'playing':
        draw_hud_buttons()
        if paused:
            draw_pause_overlay()


    if game_state == 'menu':
        draw_menu()
    elif game_state == 'game_over':
        draw_game_over()
    elif game_state == 'victory':
        draw_victory()


def update():
    global camera_x, game_state, lives, current_horde

    if game_state != 'playing' or paused:
        return


    hero.update()


    camera_x = int(hero.actor.x - WIDTH / 2)
    if camera_x < 0:
        camera_x = 0
    if camera_x > MAP_WIDTH - WIDTH:
        camera_x = MAP_WIDTH - WIDTH


    if hero.actor.x < 10:
        hero.actor.x = 10
    if hero.actor.x > MAP_WIDTH - 10:
        hero.actor.x = MAP_WIDTH - 10


    for m in monsters[:]:
        m.update(hero.actor.pos)


        if hero.is_attacking and hero.attack_forward and hero.weapon.colliderect(m.actor):
            if m not in hero.attack_hits:
                play_sfx_hit()
                m.damage(1)
                hero.attack_hits.add(m)
                continue


        if hero.vy > 0 and hero.actor.bottom <= m.actor.centery and hero.actor.colliderect(m.actor):
            play_sfx_hit()
            m.damage(1)
            hero.vy = hero.jump_speed
            continue


        if hero.actor.colliderect(m.actor):

            lives -= 1
            if lives <= 0:
                game_state = 'game_over'
                return
            else:

                hero.actor.pos = (200, GROUND_LEVEL - 50)
                hero.weapon.pos = (hero.actor.x + 15, hero.actor.y)


    for p in platforms:
        if hero.actor.colliderect(p):
            if hero.vy > 0 and hero.actor.bottom <= p.top + hero.vy:
                hero.actor.bottom = p.top
                hero.vy = 0
                hero.is_jumping = False


    if not monsters:
        if current_horde in horde_data:
            next_horde()
        else:
            game_state = 'victory'


def on_mouse_down(pos):
    global game_state, paused, music_enabled
    if game_state == 'playing':

        if btn_pause_game.collidepoint(pos):
            paused = not paused
            return
        if btn_music_game.collidepoint(pos):
            music_enabled = not music_enabled
            ensure_bg_music()
            return
        if paused:

            if btn_pause_ok.collidepoint(pos):
                paused = False
            return
        else:
            hero.start_attack()
    elif game_state == 'menu':
        handle_menu_click(pos)


def on_key_down(key):
    global game_state, paused, music_enabled
    if game_state == 'playing':
        if key == keys.P:
            paused = not paused
            return
        if key == keys.M:
            music_enabled = not music_enabled
            ensure_bg_music()
            return
        if paused:
            if key in (keys.SPACE, keys.RETURN):
                paused = False
            return
        if key == keys.SPACE and not hero.is_jumping:
            hero.vy = hero.jump_speed
            hero.is_jumping = True
        if key == keys.A:
            hero.vx = -hero.run_speed
        elif key == keys.D:
            hero.vx = hero.run_speed
        elif key == keys.Z:
            hero.start_attack()
    elif game_state in ('game_over', 'victory'):
        if key == keys.SPACE:
            restart_game()


def on_key_up(key):
    if game_state == 'playing':
        if key in (keys.A, keys.D):
            hero.vx = 0


def draw_menu():

    title = 'Heroi da Floresta'
    screen.draw.text(title, center=(WIDTH/2, 140), fontsize=72, color=(200, 230, 255))


    CYAN = (20, 220, 240)
    BLUE = (40, 120, 255)
    MAGENTA = (240, 70, 200)
    SLATE = (28, 34, 48)
    SLATE_D = (18, 22, 32)


    def clamp(x):
        return max(0, min(255, int(x)))

    def lighten(c, f):
        r, g, b = c
        return (clamp(r + (255 - r) * f), clamp(g + (255 - g) * f), clamp(b + (255 - b) * f))

    def darken(c, f):
        r, g, b = c
        return (clamp(r * (1 - f)), clamp(g * (1 - f)), clamp(b * (1 - f)))

    def draw_rounded_rect(rect, color, radius=14):
        x, y, w, h = rect.x, rect.y, rect.w, rect.h
        r = max(0, min(radius, min(w, h) // 2))

        screen.draw.filled_rect(Rect((x + r, y), (w - 2 * r, h)), color)
        screen.draw.filled_rect(Rect((x, y + r), (w, h - 2 * r)), color)

        screen.draw.filled_circle((x + r, y + r), r, color)
        screen.draw.filled_circle((x + w - r, y + r), r, color)
        screen.draw.filled_circle((x + r, y + h - r), r, color)
        screen.draw.filled_circle((x + w - r, y + h - r), r, color)

    def draw_button_tech(rect, label, base_color, active=False):

        panel = rect.inflate(28, 16)
        screen.draw.filled_rect(panel, SLATE_D)
        screen.draw.rect(panel, SLATE)


        base = base_color
        main = base
        shadow = (0, 0, 0)
        border = lighten(base, 0.25)
        glow = lighten(base, 0.45)


        sh = Rect(rect.x, rect.y + 5, rect.w, rect.h)
        draw_rounded_rect(sh, shadow, 16)


        draw_rounded_rect(rect, main, 16)


        inner = rect.inflate(-3, -3)
        draw_rounded_rect(inner, border, 14)
        inner2 = rect.inflate(-8, -8)
        draw_rounded_rect(inner2, main, 12)


        k = 16
        screen.draw.line((rect.left + 6, rect.top + k), (rect.left + 6, rect.top + 6), glow)
        screen.draw.line((rect.left + 6, rect.top + 6), (rect.left + k, rect.top + 6), glow)
        screen.draw.line((rect.right - 6, rect.top + k), (rect.right - 6, rect.top + 6), glow)
        screen.draw.line((rect.right - 6, rect.top + 6), (rect.right - k, rect.top + 6), glow)
        screen.draw.line((rect.left + 6, rect.bottom - k), (rect.left + 6, rect.bottom - 6), glow)
        screen.draw.line((rect.left + 6, rect.bottom - 6), (rect.left + k, rect.bottom - 6), glow)
        screen.draw.line((rect.right - 6, rect.bottom - k), (rect.right - 6, rect.bottom - 6), glow)
        screen.draw.line((rect.right - 6, rect.bottom - 6), (rect.right - k, rect.bottom - 6), glow)


        tx, ty = rect.center
        screen.draw.text(label, center=(tx, ty + 2), fontsize=40, color=(0, 0, 0))
        txt_color = (230, 255, 255)
        if active:
            txt_color = (255, 250, 210)
        screen.draw.text(label, center=(tx, ty), fontsize=40, color=txt_color)


    def draw_skin_card(rect, title, prefix, selected):
        panel = rect.inflate(12, 12)
        screen.draw.filled_rect(panel, SLATE_D)
        screen.draw.rect(panel, SLATE)
        base = CYAN if selected else BLUE
        draw_rounded_rect(rect, base, 14)
        inner = rect.inflate(-6, -6)
        draw_rounded_rect(inner, lighten(base, 0.1), 12)


        try:
            preview = Actor(f"{prefix}_parado")
            preview.pos = (inner.centerx, inner.centery + 8)
            preview.draw()
        except Exception:
            pass

        screen.draw.text(title, midtop=(inner.centerx, inner.top + 6), fontsize=28, color=(230, 255, 255))

    draw_skin_card(btn_skin_heroi, 'Green Hero', 'heroi', selected_skin == 'heroi')
    draw_skin_card(btn_skin_rosa, 'Pink Hero', 'heroi_rosa', selected_skin == 'heroi_rosa')


    green = (35, 200, 120)
    gray = (90, 100, 110)
    red = (230, 60, 80)

    draw_button_tech(btn_start, 'Comecar Jogo', CYAN, active=True)
    draw_button_tech(btn_music, 'Musica On/Off', BLUE if music_enabled else gray, active=music_enabled)
    draw_button_tech(btn_exit, 'Sair', MAGENTA)



def draw_game_over():

    panel_w, panel_h = 620, 260
    panel_x, panel_y = WIDTH//2 - panel_w//2, HEIGHT//2 - panel_h//2
    panel_rect = Rect(panel_x, panel_y, panel_w, panel_h)

    def rounded(rect, color, r=16):
        x, y, w, h = rect
        screen.draw.filled_rect(Rect((x + r, y), (w - 2*r, h)), color)
        screen.draw.filled_rect(Rect((x, y + r), (w, h - 2*r)), color)
        screen.draw.filled_circle((x + r, y + r), r, color)
        screen.draw.filled_circle((x + w - r, y + r), r, color)
        screen.draw.filled_circle((x + r, y + h - r), r, color)
        screen.draw.filled_circle((x + w - r, y + h - r), r, color)

    rounded(panel_rect, (24, 30, 44))
    screen.draw.rect(panel_rect, (255, 120, 120))

    title_y = panel_y + 80
    sub_y = title_y + 60
    screen.draw.text('Fim de Jogo', center=(WIDTH/2, title_y), fontsize=72, color=(255, 60, 60))
    screen.draw.text('Pressione ESPAÇO para reiniciar', center=(WIDTH/2, sub_y), fontsize=34, color=(235, 245, 255))


def draw_victory():

    panel_w, panel_h = 620, 260
    panel_x, panel_y = WIDTH//2 - panel_w//2, HEIGHT//2 - panel_h//2
    panel_rect = Rect(panel_x, panel_y, panel_w, panel_h)


    def rounded(rect, color, r=16):
        x, y, w, h = rect
        screen.draw.filled_rect(Rect((x + r, y), (w - 2*r, h)), color)
        screen.draw.filled_rect(Rect((x, y + r), (w, h - 2*r)), color)
        screen.draw.filled_circle((x + r, y + r), r, color)
        screen.draw.filled_circle((x + w - r, y + r), r, color)
        screen.draw.filled_circle((x + r, y + h - r), r, color)
        screen.draw.filled_circle((x + w - r, y + h - r), r, color)

    rounded(panel_rect, (24, 30, 44))
    screen.draw.rect(panel_rect, (150, 200, 255))


    title_y = panel_y + 80
    sub_y = title_y + 60
    screen.draw.text('Você Venceu!', center=(WIDTH/2, title_y), fontsize=72, color=(90, 170, 255))
    screen.draw.text('Pressione ESPAÇO para reiniciar', center=(WIDTH/2, sub_y), fontsize=34, color=(235, 245, 255))


pgzrun.go()
