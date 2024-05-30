import pygame as pg

pg.init()

#grid veci
GRID_SIZE = 32
GRID_COLOR = (22, 64, 201)

#window attributy
#32 je tile_size, prve cislo je pocet tiles
WIDTH = GRID_SIZE * 25
HEIGHT = GRID_SIZE * 25
# == tile_ammount(X) x GRID_SIZE(32)
MENU_WIDTH, MENU_HEIGHT = 800,800

#game settings
FPS = 60
BOTTOM_BORDER = HEIGHT

#debug variables a cheaty :D
EDITOR_MODE = not True
# map types: "img" "load" "random"
MAP_TYPE = "random"

#farby
BLACK = (0,0,0)

#bullets
bullets = []
shooting = False
SHOT_COOLDOWN = 20
shot_cooldown = SHOT_COOLDOWN
BULLET_SPEED = 20

#variables
TILE_TYPES_ALL = 2 #(all tile types - 1)
FPS = 60
TILES = []
times_placed = 0
MAX_TILES = 99999
tile_type = 1
left_key_pressed = False
right_key_pressed = False
ALL_TILES_AMMOUNT = 2 # 3 ale -1 lebo zaciname pocitat od 0
home_pressed = False

#PLAYER VARS
PLAYER_FRICTION = 0.92
PLAYER_SPEED = 0.75
player_spawned = False
PLAYER_DAMAGE = 33.4
UPGRADES = ["SPEED","DAMAGE","HEALTH","FIRE_RATE","MAGAZINE_SIZE","RECOIL REDUCTION"]


#ENEMY VARS
ENEMY_SPEED = 1
ENEMY_ANIM_SPEED = 0.1
#images
bg_img = pg.transform.scale(pg.image.load("assets/bg.png"),(WIDTH,HEIGHT))
sand_tile = pg.image.load("assets/sand_tile.png")
dirt_tile = pg.image.load("assets/dirt_tile.png")
grass_tile = pg.image.load("assets/grass_tile.png")
# barrier_tile = pg.image.load("assets/collision_box.png")
pointer_img = pg.image.load("assets/pointer.png")
menu_bg  = pg.image.load("assets/menu_bg.png")
ai_bg = pg.transform.scale(pg.image.load("assets/ai_bg.png"),(WIDTH,HEIGHT))
icon_img = pg.image.load("assets/my_dev_icon.png")
death_screen = pg.transform.scale(pg.image.load("assets/game_over_screen.png"),(800,800))

#sfx and music
pshot_sfx = pg.mixer.Sound("assets/sfx/9mm-pistol-shot-6349.wav")
pshot_sfx.set_volume(0.10)
reload_sfx = pg.mixer.Sound("assets/sfx/pistol-cock-6014.wav")
p_take_hit_sfx = pg.mixer.Sound("assets/sfx/player_took_dmg.wav")

#player skins
skin_bundles = []
p_health_img = pg.transform.scale(pg.image.load("assets/p_heart.png"),(32,32))
player_img = pg.image.load("assets/player.png") # default
default_gun = pg.transform.scale(pg.image.load("assets/gun.png"),(32,32)) #default gun
default_proj = pg.image.load("assets/bullet.png") #default projectile
skin_bundles.append([player_img,default_gun,default_proj,pshot_sfx])

player_skin1 = pg.image.load("assets/player_king.png") #king skin
king_gun = pg.transform.scale(pg.image.load("assets/king_gun.png"), (40,40)) #king's sceptre
king_proj = pg.image.load("assets/king_proj.png") #king's projectile
king_sfx = pg.mixer.Sound("assets/sfx/pacman_sfx2.wav")
skin_bundles.append([player_skin1,king_gun,king_proj,king_sfx])

player_skin2 = pg.image.load("assets/player_soldier.png") #vojak skin
soldier_gun = pg.transform.scale(pg.image.load("assets/soldier_gun.png"),(55,55)) #soldier's gun
# soldier_sfx = pg.mixer.Sound("assets/sfx/soldier_sfx.wav")
skin_bundles.append([player_skin2, soldier_gun,default_proj,pshot_sfx]) #soldier's projectile

player_skin3 = pg.image.load("assets/player_cowboy.png") #kovboj skin
cowboy_gun = pg.transform.scale(pg.image.load("assets/cowboy_gun.png"),(40,40)) #kovboj gun
cowboy_sfx = pg.mixer.Sound("assets/sfx/cowboy_sfx.wav")
skin_bundles.append([player_skin3, cowboy_gun,default_proj,cowboy_sfx]) #kovboj projectile

player_skin4 = pg.image.load("assets/player_pacman.png") # pacman ghost skin
pacman_gun = pg.transform.scale(pg.image.load("assets/pacman_gun.png"),(32,32)) #pacman gun (pacman)
pacman_proj = pg.image.load("assets/pacman_proj.png") #pacman cherry projectile
pacman_sfx = pg.mixer.Sound("assets/sfx/pacman_sfx2.wav")
skin_bundles.append([player_skin4,pacman_gun, pacman_proj,pacman_sfx])

player_skin5 = pg.image.load("assets/player_ninja.png")
ninja_gun = pg.transform.scale(pg.image.load("assets/ninja_gun.png"),(80,80))
ninja_proj = pg.transform.scale(pg.image.load("assets/ninja_proj.png"),(64,64))
ninja_sfx = pg.mixer.Sound("assets/sfx/ninja_sfx.wav")
skin_bundles.append([player_skin5,ninja_gun,ninja_proj,ninja_sfx])

#enemy imgs
enemy_list = [pg.image.load("assets/enemy_idle.png"),pg.image.load("assets/enemy0.png")
    ,pg.image.load("assets/enemy1.png"),pg.image.load("assets/enemy2.png")]
e_take_hit_sfx = pg.mixer.Sound("assets/sfx/slime_took_dmg.wav")
white_enemy_img = pg.image.load("assets/white_enemy.png")
