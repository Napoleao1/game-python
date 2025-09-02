import pgzrun
from pgzero.rect import Rect
import random
import math

# =========================================================================
# 1. Global Settings
# =========================================================================

WIDTH = 1920
HEIGHT = 1080
MAP_WIDTH = 1920
GROUND_LEVEL = HEIGHT - 33

DARK_GREEN = (0, 50, 0)
GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

game_state = 'menu'
music_enabled = True
lives = 3
current_horde = 1

menu_font = 'silkscreen' 

# Menu buttons
btn_start = Rect(700, 550, 520, 50)
btn_music = Rect(700, 620, 520, 50)
btn_exit = Rect(700, 690, 520, 50)

camera_x = 0

# Horda settings
horde_data = {
    1: {'monsters': 5, 'type': 'monstro'},
    2: {'monsters': 7, 'type': 'monstro2'}
}

# =========================================================================
# 2. Character Classes
# =========================================================================

class Hero:
    def __init__(self):
        self.actor = Actor('heroi_parado', (50, 500))
        self.vx = 0
        self.vy = 0
        self.is_jumping = False
        self.jump_speed = -12
        self.run_speed = 7
        self.weapon = Actor('weapon', (self.actor.x + 15, self.actor.y))
        self.is_attacking = False

    def update(self):
        self.vy += 1
        self.actor.y += self.vy
        self.actor.x += self.vx
      
        if self.vx != 0 and not self.is_jumping:
            self.actor.image = 'heroi_correndo'
        else:
            self.actor.image = 'heroi_parado'

        if self.actor.y > GROUND_LEVEL:
            self.actor.y = GROUND_LEVEL
            self.vy = 0
            self.is_jumping = False

        self.weapon.pos = (self.actor.x + 15, self.actor.y)

class Monster:
    def __init__(self, x, y, image_name):
        self.actor = Actor(image_name, (x, y))
        self.speed = 1
        self.health = 3
    
    def update(self, hero_pos):
        if self.actor.x < hero_pos[0]:
            self.actor.x += self.speed
        else:
            self.actor.x -= self.speed

    def draw(self):
        self.actor.draw()

# =========================================================================
# 3. Game Elements (Single Map)
# =========================================================================

hero = Hero()
door = Actor('porta', (MAP_WIDTH - 100, 500)) 

platforms = [
    Rect(0, HEIGHT - 33, MAP_WIDTH, 33),
]

monsters = []

cacti = [
    Actor('cactus', (500, GROUND_LEVEL - 15)),
    Actor('cactus', (1000, GROUND_LEVEL - 15)),
    Actor('cactus', (1500, GROUND_LEVEL - 15)),
    Actor('cactus', (1800, GROUND_LEVEL - 15)),
    Actor('cactus', (2200, GROUND_LEVEL - 15)),
]

def spawn_horda(horda_number):
    monsters.clear()
    horda_info = horde_data.get(horda_number)
    if horda_info:
        for i in range(horda_info['monsters']):
            monsters.append(Monster(MAP_WIDTH - 200 - i * 100, GROUND_LEVEL - 15, horda_info['type']))

def start_game():
    global game_state, camera_x, lives, current_horde
    game_state = 'playing'
    lives = 3
    current_horde = 1
    camera_x = 0
    hero.actor.pos = (50, 500)
    spawn_horda(current_horde)

def restart_game():
    global game_state, lives, current_horde
    game_state = 'playing'
    lives = 3
    current_horde = 1
    hero.actor.pos = (50, 500)
    spawn_horda(current_horde)

def next_horde():
    global current_horde, game_state
    current_horde += 1
    if current_horde in horde_data:
        spawn_horda(current_horde)
    else:
        game_state = 'victory'
    
# =========================================================================
# 4. Input and Game State Functions
# =========================================================================

def play_background_music():
    if music_enabled:
        music.play('trilha_sonora') 
        music.set_volume(0.5)

def handle_menu_click(pos):
    global music_enabled
    if btn_start.collidepoint(pos):
        start_game()
    elif btn_music.collidepoint(pos):
        music_enabled = not music_enabled
        if music_enabled:
            play_background_music()
        else:
            music.stop()
    elif btn_exit.collidepoint(pos):
        exit()

# =========================================================================
# 5. Game Loop (Draw and Update)
# =========================================================================

def draw():
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()
    elif game_state == 'game_over':
        draw_game_over()
    elif game_state == 'victory':
        draw_victory()

def update():
    global camera_x, game_state, lives, current_horde
    
    if game_state == 'playing':
        hero.update()
        
        # A camera segue o herói
        camera_x = hero.actor.x - WIDTH / 2
        
        # Limita a camera nas bordas do mapa
        if camera_x < 0:
            camera_x = 0
        if camera_x > MAP_WIDTH - WIDTH:
            camera_x = MAP_WIDTH - WIDTH

        # Impede que o herói saia da tela
        if hero.actor.x < camera_x:
            hero.actor.x = camera_x
        if hero.actor.x > camera_x + WIDTH:
            hero.actor.x = camera_x + WIDTH

        for monster in monsters:
            monster.update(hero.actor.pos)
            if hero.actor.colliderect(monster.actor):
                if hero.is_attacking and hero.weapon.colliderect(monster.actor):
                    music.play('hit')
                    monster.health -= 1
                    if monster.health <= 0:
                        monsters.remove(monster)
                        if not monsters:
                            next_horde()
                    hero.is_attacking = False
                elif hero.vy > 0 and hero.actor.bottom < monster.actor.centery:
                    music.play('hit')
                    monster.health -= 1
                    if monster.health <= 0:
                        monsters.remove(monster)
                        if not monsters:
                            next_horde()
                    hero.vy = hero.jump_speed
                else:
                    lives -= 1
                    if lives <= 0:
                        game_state = 'game_over'
                        return
                    else:
                        hero.actor.pos = (50, 500)
        
        for platform in platforms:
            if hero.actor.colliderect(platform):
                if hero.vy > 0 and hero.actor.bottom <= platform.top + hero.vy:
                    hero.actor.bottom = platform.top
                    hero.vy = 0
                    hero.is_jumping = False
        
        for cactus in cacti:
            if hero.actor.colliderect(cactus):
                lives -= 1
                if lives <= 0:
                    game_state = 'game_over'
                    return
                else:
                    hero.actor.pos = (50, 500)

        if hero.is_attacking:
            animate_weapon()

        if not monsters and hero.actor.colliderect(door):
            game_state = 'victory'
            return
        
def on_mouse_down(pos):
    global game_state
    if game_state == 'playing':
        hero.is_attacking = True
    elif game_state == 'menu':
        handle_menu_click(pos)

def on_key_down(key):
    if game_state == 'playing':
        if key == keys.SPACE and not hero.is_jumping:
            hero.vy = hero.jump_speed
            hero.is_jumping = True
        
        if key == keys.A:
            hero.vx = -hero.run_speed
        elif key == keys.D:
            hero.vx = hero.run_speed

def on_key_up(key):
    if game_state == 'playing':
        if key in (keys.A, keys.D):
            hero.vx = 0
    hero.is_attacking = False

def animate_weapon():
    hero.weapon.x += 10
    if hero.weapon.x > hero.actor.x + 50:
        hero.weapon.x = hero.actor.x + 15
        
def draw_menu():
    screen.fill('black')
    screen.draw.text('Heroi da Floresta', center=(WIDTH/2, 100), fontsize=70, color=WHITE)
    screen.draw.filled_rect(btn_start, 'green')
    screen.draw.text('Comecar Jogo', center=btn_start.center, fontsize=30, color='white')
    music_color = 'green' if music_enabled else 'red'
    screen.draw.filled_rect(btn_music, music_color)
    screen.draw.text('Musica On/Off', center=btn_music.center, fontsize=30, color='white')
    screen.draw.filled_rect(btn_exit, 'red')
    screen.draw.text('Sair', center=btn_exit.center, fontsize=30, color='white')

def draw_game():
    screen.blit('background', (0,0))
    
    # Desenha o chão de grama e faz a rolagem com o mapa
    grass_x_pos = -camera_x
    screen.blit('grass', (grass_x_pos, HEIGHT - 33))

    hero.actor.draw()
    hero.weapon.draw()

    for monster in monsters:
        monster.draw()
    
    for cactus in cacti:
        cactus.draw()

    door.draw()

    screen.draw.text('LIFES', topleft=(10, 10), fontsize=40, color='red')
    for i in range(lives):
        screen.blit('heart', (100 + i * 40, 10))
        
    screen.draw.text('Horda ' + str(current_horde), topleft=(WIDTH - 150, 10), fontsize=40, color='red')

def draw_game_over():
    screen.fill('black')
    screen.draw.text('Fim de Jogo', center=(WIDTH/2, HEIGHT/2), fontsize=70, color='red')
    screen.draw.text('Pressione ESPAÇO para reiniciar', center=(WIDTH/2, 400), fontsize=30, color=WHITE)

def draw_victory():
    screen.fill('gold')
    screen.draw.text('Voce Venceu!', center=(WIDTH/2, HEIGHT/2), fontsize=70, color='blue')
    screen.draw.text('Pressione ESPAÇO para reiniciar', center=(WIDTH/2, 400), fontsize=30, color=WHITE)

# =========================================================================
# 6. Initialization
# =========================================================================

pgzrun.go()
