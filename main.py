import pygame as pg
import sys
import math
import json
import random
import time


# custom imports from my own game files
from settings import *
from button import *
# pg.init()
# WIDTH, HEIGHT = pg.display.Info().current_w,pg.display.Info().current_h







class Enemy:
    def __init__(self, x, y, health, type="default"):
        self.type = type
        if self.type == "default":
            self.img_list = enemy_list

        self.current_img = 0
        self.img = self.img_list[self.current_img]
        self.rect = self.img.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.target = game.p
        self.speed = ENEMY_SPEED
        self.health = health
        self.dir = pg.math.Vector2()
        self.vel = pg.math.Vector2()
        self.pos = pg.math.Vector2(self.rect.x,self.rect.y)
        self.dmg = 1
        self.white_enemy_img = white_enemy_img
        self.flashing = False
        self.flash_duration = 0.1  # Duration of the flashing effect in seconds
        self.flash_timer = 0
        self.original_img = self.img
        self.take_hit_sfx = e_take_hit_sfx

    def draw(self):
        self.current_img += ENEMY_ANIM_SPEED
        if self.current_img >= len(self.img_list):
            self.current_img = 0

        self.img = self.img_list[int(self.current_img)]
        game.screen.blit(self.img, self.rect)

    def take_hit(self,dmg):
        if self.health > dmg:
            self.take_hit_sfx.play()
            self.health -= dmg
            self.flash_timer = self.flash_duration
            self.flashing = True
        else:
            game.enemies.remove(self)
            game.score += 1


    #nefunguje rn :D
    def white_flash_img(self):
        if self.flashing:
            # print("Flashing...")
            if self.flash_timer <= 0:
                self.flashing = False
                self.img = self.original_img
            else:
                if self.img == self.original_img:
                    self.img = self.white_enemy_img
                else:
                    self.img = self.original_img
                # Decrement flash_timer by a constant value
                self.flash_timer -= 0.1  # Adjust this value as needed

    def get_vector_distance(self, vector1,vector2):
        return (vector1-vector2).magnitude()
    def follow_player(self):
        self.target = game.p
        player_vec = pg.math.Vector2(self.target.rect.center)
        self.vec = pg.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vec,self.vec)

        if distance > 0:
            self.dir = (player_vec - self.vec).normalize()
        else:
            self.dir = pg.math.Vector2()

        self.vel = self.dir * self.speed

        self.pos += self.vel


        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y

    def update(self):
        self.follow_player()

        self.draw()
        self.white_flash_img()


class Tile:
    def __init__(self, x, y, size, tile_type):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pg.Rect(self.x, self.y, self.size, self.size)
        self.tile_type = tile_type

        # Use a dictionary to map tile types to images
        self.tile_images = {
            0: sand_tile,
            1: dirt_tile,
            2: grass_tile
        }

        self.img = self.tile_images.get(tile_type, sand_tile)  # Default to sand_tile if tile_type is not found

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def update(self, win):
        self.draw(win)


class Bullet:
    def __init__(self, player):
        self.proj = skin_bundles[player.skin_index][2]
        self.img = pg.transform.rotozoom(self.proj, -player.angle, 1.5)
        self.rect = self.img.get_rect()
        self.rect.x, self.rect.y = player.rect.x, player.rect.centery
        self.target_x, self.target_y = player.pointerx + (random.randint(-game.p.spread,game.p.spread)), player.pointery + (random.randint(-game.p.spread,game.p.spread))
        self.speed = BULLET_SPEED
        self.angle = math.atan2(self.target_y - self.rect.centery, self.target_x - self.rect.centerx)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.x = self.rect.x
        self.y = self.rect.y

    def update(self, win):
        self.x += self.dx
        self.y += self.dy

        self.rect.topleft = (self.x, self.y)
        win.blit(self.img, self.rect.topleft)


class Player:
    def __init__(self, x, y):
        # self.skin_index = random.randint(0, len(skin_bundles) - 1)
        self.skin_index = 0
        try:
            self.img = skin_bundles[self.skin_index][0]
            self.gun_img = skin_bundles[self.skin_index][1]
            self.shot_sfx = skin_bundles[self.skin_index][3]
        except IndexError:
            self.img = skin_bundles[0][0]
            self.gun_img = skin_bundles[0][1]
            self.shot_sfx = skin_bundles[0][3]

        self.reload_sfx = reload_sfx
        self.health_img = p_health_img
        self.rect = self.img.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.gun_rect = self.gun_img.get_rect()
        self.pointerx, self.pointery = 0, 0
        self.dmg = PLAYER_DAMAGE
        self.dx = 0
        self.dy = 0
        self.speed = PLAYER_SPEED
        self.friction = PLAYER_FRICTION
        self.shooting = False
        self.max_health = 5
        self.health = self.max_health
        self.invincible = False
        self.invincible_start_time = 0
        self.invincibility_duration = 1  # duration in seconds
        self.dead = False
        self.max_ammo_ammount = 15
        self.ammo_ammount = self.max_ammo_ammount
        self.reloading = False
        self.reload_start_time = 0
        self.reload_duration = 2
        self.recoil_amount = 15
        self.recoil_offset = 0
        self.recoil_recovery_speed = 1
        self.spread = 35
        self.take_hit_sfx = p_take_hit_sfx


    def can_upgrade(self):
        if game.score % 10 == 0:
            game.upgrade_screen()

    def draw(self, win):
        rotated_gun_img = pg.transform.rotate(self.gun_img, -self.angle)
        if pg.mouse.get_pos()[0] < self.rect.x:
            rotated_gun_img = pg.transform.flip(pg.transform.rotate(self.gun_img, self.angle), False, True)

        new_rect = rotated_gun_img.get_rect(center=self.gun_rect.center)
        if pg.mouse.get_pos()[0] < self.rect.x:
            new_rect.left += self.recoil_offset
        else:
            new_rect.left -= self.recoil_offset


        win.blit(self.img, self.rect)
        win.blit(rotated_gun_img, (new_rect.left, new_rect.top + 10))

    def custom_pointer(self, win, pointer_img):
        self.pointerx, self.pointery = pg.mouse.get_pos()
        win.blit(pointer_img, (self.pointerx - 16, self.pointery - 16))

    def reload(self):
        self.reloading = True
        self.reload_start_time = time.time()
        self.reload_sfx.play()

    def finish_reload(self):
        self.ammo_ammount = self.max_ammo_ammount
        self.reloading = False

    def take_hit(self, dmg):
        if not self.invincible:
            self.take_hit_sfx.play()
            self.health -= dmg
            if self.health <= 0:
                self.dead = True
            else:
                self.invincible = True
                self.invincible_start_time = time.time()

    def draw_health(self):
        for i in range(self.health):
            game.screen.blit(self.health_img,((WIDTH - 50) - (i*32),20))

    def apply_friction(self):
        if abs(self.dx) < 0.1:
            self.dx = 0
        else:
            self.dx *= self.friction

        if abs(self.dy) < 0.1:
            self.dy = 0
        else:
            self.dy *= self.friction

    def movement(self, tiles):
        keys = pg.key.get_pressed()

        if keys[pg.K_w] and self.rect.top > 0:
            self.dy -= self.speed
        if keys[pg.K_s] and self.rect.bottom < HEIGHT:
            self.dy += self.speed
        if keys[pg.K_a] and self.rect.left > 0:
            self.dx -= self.speed
        if keys[pg.K_d] and self.rect.right < WIDTH:
            self.dx += self.speed

        # Apply friction
        self.apply_friction()

        # Update player coordinates
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Ensure the player stays within the window boundaries
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

        self.angle = math.degrees(math.atan2(self.pointery - self.rect.centery, self.pointerx - self.rect.centerx))
        self.gun_rect.centerx = self.rect.centerx
        self.gun_rect.centery = self.rect.centery

    def apply_recoil(self):
        # Gradually reduce the recoil offset
        if self.recoil_offset > 0:
            self.recoil_offset -= self.recoil_recovery_speed
            if self.recoil_offset < 0:
                self.recoil_offset = 0

    def update(self, win, pointer_img):
        if self.invincible and time.time() - self.invincible_start_time > self.invincibility_duration:
            self.invincible = False
        if self.reloading:
            if time.time() - self.reload_start_time >= self.reload_duration:
                self.finish_reload()
        if self.ammo_ammount <= 0 and not self.reloading:
            self.reload()
        self.apply_recoil()
        self.movement(game.tiles)
        self.draw(win)
        self.custom_pointer(win, pointer_img)
        self.draw_health()

class Game:
    def __init__(self):
        self.running = True
        self.screen = None
        self.clock = None
        self.size = self.width, self.height = WIDTH, HEIGHT
        self.bg_color = (0, 0, 0)
        self.tiles = TILES
        self.tile_type = tile_type
        self.left_key_pressed = False
        self.right_key_pressed = False
        self.editor_mode = EDITOR_MODE
        self.times_placed = 0
        self.max_tiles = MAX_TILES
        self.home_pressed = False
        self.map_type = MAP_TYPE
        self.GRID_SIZE = GRID_SIZE
        self.ALL_TILES_AMOUNT = TILE_TYPES_ALL
        self.shooting = shooting
        self.shot_cooldown = shot_cooldown
        self.bullets = bullets
        self.sound_mult = 100
        # print(self.sound_mult)
        self.pointer_img = pg.image.load("assets/pointer.png")
        self.bg_img = pg.transform.scale(pg.image.load("assets/bg.png"),(WIDTH,HEIGHT))
        if self.map_type != "img":
            self.p = Player(self.width//2, self.height//2)
        else:
            self.p = Player(self.width // 2, self.height // 2)
        self.e = None
        self.enemies = []
        self.score = 0
        self.bullets_to_remove = set()
        self.wave_mult = 1
        self.high_score = 0
        self.last_shot_time = 0
        self.shot_cooldown = 0.25

    def populate_tiles(self):
        def get_random_empty_position(existing_positions):
            while True:
                # Randomly choose a position within the grid boundaries
                x = random.randint(0, (WIDTH // self.GRID_SIZE) - 1) * self.GRID_SIZE
                y = random.randint(0, (HEIGHT // self.GRID_SIZE) - 1) * self.GRID_SIZE

                # Return the position if it is empty
                if (x, y) not in existing_positions:
                    return x, y

        # Create a set of all existing positions
        existing_positions = {(tile.x, tile.y) for tile in self.tiles}

        while len(existing_positions) < (WIDTH // self.GRID_SIZE) * (HEIGHT // self.GRID_SIZE):
            # Choose a random tile type
            tile_type = random.randint(0, 2)

            # Get a random starting position
            x, y = get_random_empty_position(existing_positions)

            for _ in range(20,50):  # Random steps between 10 and 20
                # Add a new tile at the current position
                new_tile = Tile(x, y, self.GRID_SIZE, tile_type)
                self.tiles.append(new_tile)
                existing_positions.add((x, y))

                # Randomly choose a direction to move (up, down, left, right)
                direction = random.choice(['up', 'down', 'left', 'right'])

                if direction == 'up':
                    y -= self.GRID_SIZE
                elif direction == 'down':
                    y += self.GRID_SIZE
                elif direction == 'left':
                    x -= self.GRID_SIZE
                elif direction == 'right':
                    x += self.GRID_SIZE

                # Ensure the position stays within the grid boundaries
                x = max(0, min(x, WIDTH - self.GRID_SIZE))
                y = max(0, min(y, HEIGHT - self.GRID_SIZE))

                if (x, y) in existing_positions:
                    break

        # Remove duplicate tiles (if any)
        unique_tiles = set((tile.x, tile.y, tile.tile_type) for tile in self.tiles)
        self.tiles = [Tile(x, y, self.GRID_SIZE, tile_type) for x, y, tile_type in unique_tiles]

    def initialize(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.enemies = []
        self.screen = screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption('My Game')
        self.clock = pg.time.Clock()

        if self.map_type == "load":
            self.tiles = self.load_game()
        elif self.map_type == "random":
            self.populate_tiles()
        elif self.map_type == "img":
            pass

        # Clean up duplicate tiles
        unique_tiles = set((tile.x, tile.y, tile.tile_type) for tile in self.tiles)
        self.tiles = [Tile(x, y, self.GRID_SIZE, tile_type) for x, y, tile_type in unique_tiles]

        # Initialize the player

        # Save the game only if map_type is not "random"
        if self.map_type != "random":
            self.save_game()

        self.pshot_sfx = skin_bundles[self.p.skin_index][3]
        self.pshot_sfx.set_volume(self.sound_mult / 100)


        for i in range(5):
            self.enemies.append(Enemy((random.randint(0,25) * 32),(random.randint(0,25) * 32),100))

    def save_game(self):
        print(self.sound_mult)
        game_data = {
            "sound_mult": self.sound_mult,
            "high_score": self.score,
            "tiles": []
        }

        positions_set = set()
        for tile in self.tiles:
            if (tile.x, tile.y) not in positions_set:
                tile_data = {
                    "x": tile.x,
                    "y": tile.y,
                    "tile_type": tile.tile_type
                }
                game_data["tiles"].append(tile_data)
                positions_set.add((tile.x, tile.y))

        with open("gamefile.json", "w") as f:
            json.dump(game_data, f, indent=4)

    def load_game(self):
        try:
            with open("gamefile.json", "r") as f:
                game_data = json.load(f)
                self.sound_mult = game_data.get("sound_mult", 100)  # Load sound_mult with a default value of 100
                print(self.sound_mult)
                self.high_score = game_data.get("high_score", 0)
                tiles_data = game_data.get("tiles", [])

                self.tiles = []
                for tile_info in tiles_data:
                    x = tile_info["x"]
                    y = tile_info["y"]
                    tile_type = tile_info["tile_type"]
                    new_tile = Tile(x, y, self.GRID_SIZE, tile_type)
                    self.tiles.append(new_tile)

        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet (e.g., first run)
            self.sound_mult = 100
            self.tiles = []
        print(self.high_score)
        return self.tiles

    def change_tile_type(self):
        if self.editor_mode:
            keys = pg.key.get_pressed()

            if keys[pg.K_LEFT] and self.tile_type > 0 and not self.left_key_pressed:
                self.tile_type -= 1
                print(self.tile_type)
                self.left_key_pressed = True

            if keys[pg.K_RIGHT] and self.tile_type < self.ALL_TILES_AMOUNT and not self.right_key_pressed:
                self.tile_type += 1
                print(self.tile_type)
                self.right_key_pressed = True

            if not keys[pg.K_LEFT]:
                self.left_key_pressed = False

            if not keys[pg.K_RIGHT]:
                self.right_key_pressed = False
        else:
            print("Enable editor mode before editing tiles.")

    def place_tile(self):
        if self.editor_mode:
            if self.times_placed < self.max_tiles:
                mouse_x, mouse_y = pg.mouse.get_pos()
                x = (mouse_x // self.GRID_SIZE) * self.GRID_SIZE
                y = (mouse_y // self.GRID_SIZE) * self.GRID_SIZE

                tile_already_placed = any(tile.x == x and tile.y == y for tile in self.tiles)

                if tile_already_placed:
                    print("Tile already placed here")
                else:
                    new_tile = Tile(x, y, self.GRID_SIZE, self.tile_type)
                    self.tiles.append(new_tile)
                    self.times_placed += 1
                    print(self.times_placed)
            else:
                print(f"You have already placed {self.max_tiles} tiles. Try again")
        else:
            print("Enable editor mode before placing tiles.")

    def delete_tile(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        x = (mouse_x // self.GRID_SIZE) * self.GRID_SIZE
        y = (mouse_y // self.GRID_SIZE) * self.GRID_SIZE

        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                self.tiles.remove(tile)
                self.times_placed -= 1

                return
        print("No tile to delete at this position")

    def handle_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_HOME]:
            self.editor_mode = True
        elif keys[pg.K_END]:
            self.editor_mode = False
        elif keys[pg.K_ESCAPE]:
            self.save_game()
            self.main_menu()

    def spawn_enemies(self):
        self.wave_mult += 1
        self.enemy_ammount = int((self.wave_mult * 1.2) + 3)
        self.enemy_health = (self.wave_mult * 20) + 80

        for i in range(self.enemy_ammount):
            self.enemies.append(Enemy((random.randint(0,25) * 32),(random.randint(0,25) * 32),self.enemy_health))

    def spawn_bullet(self):
        now = time.time()
        if now - self.last_shot_time > self.shot_cooldown and not self.p.reloading and self.p.ammo_ammount > 0:
            bullet = Bullet(self.p)
            self.bullets.append(bullet)
            self.p.ammo_ammount -= 1
            self.p.recoil_offset = self.p.recoil_amount  # Apply recoil
            self.last_shot_time = now
            self.pshot_sfx.play()


    def gameloop(self):
        self.initialize()
        pg.display.set_caption("Game")
        pg.display.set_icon(icon_img)

        self.font_s = pg.font.Font(None, 30)

        self.fps_text = self.font_l.render(f"{round(self.clock.get_fps(), 0)}", True, "black")
        self.fps_text_rect = self.fps_text.get_rect(center=(40, 25))

        self.score_text = self.font_s.render(f"{self.score}", True, "black")
        self.score_text_rect = self.score_text.get_rect(center=(WIDTH // 2, 25))
        self.p.dead = False
        self.p.health = self.p.max_health

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.editor_mode:
                        if event.button == 1:
                            self.place_tile()
                        elif event.button == 3:
                            self.delete_tile()

                if event.type == pg.MOUSEBUTTONDOWN and not self.editor_mode and not self.shooting and not self.p.reloading:
                    self.spawn_bullet()

            if self.shooting:
                if self.shot_cooldown != 0:
                    self.shot_cooldown -= 1
                else:
                    self.shot_cooldown = SHOT_COOLDOWN
                    self.shooting = False

            self.handle_keys()
            # self.screen.fill((30, 100, 200))
            if self.map_type == "img":
                self.screen.blit(ai_bg, (0, 0))
            if self.map_type != "img":
                for tile in self.tiles:
                    tile.draw(self.screen)

            self.p.update(self.screen, self.pointer_img)

            if len(self.enemies) == 0:
                self.spawn_enemies()

            for enemy in self.enemies:
                enemy.update()

            for enemy in self.enemies:
                for bullet in self.bullets:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.take_hit(game.p.dmg)
                        self.bullets_to_remove.add(bullet)
            for enemy in self.enemies:
                if enemy.rect.colliderect(self.p.rect):
                    self.p.take_hit(enemy.dmg)

            bullets_set = set(self.bullets)
            bullets_set -= self.bullets_to_remove
            self.bullets = list(bullets_set)
            if self.editor_mode:
                self.change_tile_type()

            for bullet in self.bullets:
                bullet.update(self.screen)

            # renderovanie textu
            self.fps_text = self.font_s.render(f"{round(self.clock.get_fps(), 0)}", True, "black")
            self.screen.blit(self.fps_text, self.fps_text_rect)

            # pg.draw.rect(self.screen,(255,255,255),(WIDTH//2-30,0,75,75))
            self.score_text = self.font_l.render(f"{self.score}", True, "black")
            self.screen.blit(self.score_text, self.score_text_rect)
            # koniec renderovania textu

            if self.p.dead:
                self.game_over()

            pg.display.update()
            self.clock.tick(FPS)

        if self.editor_mode:
            self.save_game()

        pg.quit()
        sys.exit()

    def upgrade_screen():
        win = pg.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
        pg.display.set_icon(icon_img)
        pg.mouse.set_visible(True)

    def game_over(self):
        win = pg.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
        self.save_game()
        for i in range(1000):
            for event in pg.event.get():
                if event.type ==pg.QUIT:
                    self.save_game()
                    pg.quit()
                    sys.exit()

            win.fill((0,0,0))
            win.blit(death_screen, (0, 0))
            pg.display.update()
        self.main_menu()

    def change_sound(self):
        self.p.shot_sfx.set_volume(self.sound_mult / 100)
        self.p.reload_sfx.set_volume(self.sound_mult / 100)
        self.p.take_hit_sfx.set_volume(self.sound_mult / 100)
        for enemy in self.enemies:
            enemy.take_hit_sfx.set_volume(self.sound_mult / 100)

    def options(self):
        pg.display.set_icon(icon_img)
        pg.mouse.set_visible(True)
        pg.init()

        win = pg.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
        pg.display.set_caption("Options")
        self.font = pg.font.Font(None, 20)
        self.font_m = pg.font.Font(None, 50)
        self.back_button = Button(image=pg.image.load("assets/small_button.png"), pos=(50, 25), text_input="BACK",
                                  font=self.font, base_color="black", hovering_color="red")
        self.sound_text = self.font_m.render("Volume", True, "white")
        self.sound_text_rect = self.sound_text.get_rect(center=(80, 100))
        self.decrease_vol = Button(image=pg.image.load("assets/small_button.png"), pos=(200, 100), text_input="-",
                                   font=self.font, base_color="black", hovering_color="red")
        self.increase_vol = Button(image=pg.image.load("assets/small_button.png"), pos=(430, 100), text_input="+",
                                   font=self.font, base_color="black", hovering_color="red")
        self.volume_text = self.font_l.render(f"{self.sound_mult}", True, "white")
        self.volume_text_rect = self.volume_text.get_rect(center=(300, 100))

        self.editor_text = self.font_m.render(f"Editor mode: {self.editor_mode}", True, "white")
        self.editor_text_rect = self.editor_text.get_rect(center=(180, 180))
        self.editor_on = Button(image=pg.image.load("assets/small_button.png"), pos=(430, 180), text_input="On",
                                   font=self.font, base_color="black", hovering_color="red")
        self.editor_off = Button(image=pg.image.load("assets/small_button.png"), pos=(530, 180), text_input="Off",
                                 font=self.font, base_color="black", hovering_color="red")

        while True:
            win.blit(menu_bg, (0,0))

            self.mouse_pos = pg.mouse.get_pos()
            # print(self.mouse_pos)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.save_game()
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.back_button.checkForInput(self.mouse_pos):
                        self.save_game()
                        self.main_menu()
                    if self.increase_vol.checkForInput(self.mouse_pos) and self.sound_mult < 100:
                        self.sound_mult += 5
                        self.volume_text = self.font_l.render(f"{self.sound_mult}", True, "white")
                        self.change_sound()
                        self.save_game()
                    if self.decrease_vol.checkForInput(self.mouse_pos) and self.sound_mult > 0:
                        self.sound_mult -= 5
                        self.volume_text = self.font_l.render(f"{self.sound_mult}", True, "white")
                        self.change_sound()
                        self.save_game()
                    if self.editor_on.checkForInput(self.mouse_pos):
                        self.editor_mode = True
                        self.editor_text = self.font_m.render(f"Editor mode: {self.editor_mode}", True, "white")

                    if self.editor_off.checkForInput(self.mouse_pos):
                        self.editor_mode = False
                        self.editor_text = self.font_m.render(f"Editor mode: {self.editor_mode}", True, "white")





            for button in [self.back_button, self.decrease_vol, self.increase_vol,self.editor_on,self.editor_off]:
                button.changeColor(self.mouse_pos)
                button.update(win)

            win.blit(self.volume_text, self.volume_text_rect)
            win.blit(self.sound_text, self.sound_text_rect)
            win.blit(self.editor_text, self.editor_text_rect)
            pg.display.update()

    def main_menu(self):
        pg.display.set_icon(icon_img)
        pg.mouse.set_visible(True)
        pg.init()
        win = pg.display.set_mode((MENU_WIDTH,MENU_HEIGHT))
        if self.map_type == "load":
            self.tiles = self.load_game()
        pg.display.set_caption("Main Menu")
        while True:
            win.blit(menu_bg,(0,0))

            self.menu_mouse_pos = pg.mouse.get_pos()
            self.font = pg.font.Font(None,40)
            self.font_l = pg.font.Font(None, 80)
            self.menu_text = self.font_l.render("MAIN MENU", True, (255,255,255))
            self.menu_rect = self.menu_text.get_rect(center=(WIDTH//2,50))
            self.play_button = Button(image=pg.image.load("assets/button.png"),pos=(280,150),text_input="PLAY",font=self.font,base_color="black",hovering_color="red")
            self.options_button = Button(image=pg.image.load("assets/button.png"),pos=(520,150),text_input="OPTIONS",font=self.font,base_color="black",hovering_color="red")
            self.quit_button = Button(image=pg.image.load("assets/button.png"),pos=(MENU_WIDTH//2,280),text_input="QUIT",font=self.font,base_color="black",hovering_color="red")

            for button in [self.play_button,self.options_button,self.quit_button]:
                button.changeColor(self.menu_mouse_pos)
                button.update(win)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.save_game()
                    pg.quit()
                    sys.exit()


                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.play_button.checkForInput(self.menu_mouse_pos):
                        self.gameloop()
                    if self.options_button.checkForInput(self.menu_mouse_pos):
                        self.options()
                    if self.quit_button.checkForInput(self.menu_mouse_pos):
                        print(self.sound_mult)
                        self.save_game()
                        pg.quit()
                        sys.exit()

            win.blit(self.menu_text,self.menu_rect)

            pg.display.update()

if __name__ == "__main__":
    game = Game()
    game.main_menu()
