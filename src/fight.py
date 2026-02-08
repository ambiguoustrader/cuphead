import arcade
import random
from itertools import cycle
import math

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Лев"
SPEED = 5
WATER_HEIGHT = SCREEN_HEIGHT // 3
BULLET_SPEED = 40
EX_BULLET_SPEED = 30
DRAGON_FIRE_SPEED = 8

ENEMY_HIT_FLASH_DURATION = 6

_bullet_texture_cache = {}


def get_bullet_texture(path):
    if path not in _bullet_texture_cache:
        _bullet_texture_cache[path] = arcade.load_texture(path)
    return _bullet_texture_cache[path]


def preload_all_textures():
    print("Загрузка текстур...")
    RockLion._load_textures()
    Mudman._load_textures()
    Satyr._load_textures()
    BabyDragon._load_textures()
    DragonFire._load_textures(is_pink=False)
    DragonFire._load_textures(is_pink=True)
    get_bullet_texture("assets/images/cuphead/shoots/peashooter.png")
    get_bullet_texture("assets/images/cuphead/Supers/Mega_Blast.png")
    print("Все текстуры загружены!")


class RockLion(arcade.Sprite):
    _texture_cache = None

    @classmethod
    def _load_textures(cls):
        if cls._texture_cache is not None:
            return

        cls._texture_cache = {
            "intro": {"right": [], "left": []},
            "attack": {"right": [], "left": []},
            "splash": {"right": [], "left": []},
        }

        base = "assets/images/enemies/Rock Lion"

        for i in range(1, 9):
            path = f"{base}/Roar/Intro/lv3-2_rock_lion_intro_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["intro"]["left"].append(texture)
            if i == 8:
                for _ in range(5):
                    cls._texture_cache["intro"]["left"].append(texture)
        for i in range(7, 0, -1):
            path = f"{base}/Roar/Intro/lv3-2_rock_lion_intro_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["intro"]["left"].append(texture)

        for texture in cls._texture_cache["intro"]["left"]:
            cls._texture_cache["intro"]["right"].append(texture.flip_left_right())

        for i in range(1, 9):
            path = f"{base}/Roar/Intro/lv3-2_rock_lion_intro_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["attack"]["left"].append(texture)
            if i == 8:
                for _ in range(5):
                    cls._texture_cache["attack"]["left"].append(texture)
        for i in range(7, 0, -1):
            path = f"{base}/Roar/Intro/lv3-2_rock_lion_intro_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["attack"]["left"].append(texture)

        for texture in cls._texture_cache["attack"]["left"]:
            cls._texture_cache["attack"]["right"].append(texture.flip_left_right())

        for i in range(1, 22):
            path = f"{base}/Death/lv3-2_rock_lion_death_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["splash"]["left"].append(texture)

        for texture in cls._texture_cache["splash"]["left"]:
            cls._texture_cache["splash"]["right"].append(texture.flip_left_right())

    def __init__(self, x, y, direction_x, shoot=None):
        RockLion._load_textures()
        texture = RockLion._texture_cache["intro"]["left"][0]
        super().__init__(texture)

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0

        self.direction = "right" if direction_x > 0 else "left"
        self.start = True
        self.on_ground = False
        self.state = "intro"
        self.current_frame = 0
        self.animation_speed_counter = 0
        self.start_intro_complete = False
        self.hp = 1000
        self.invincible = False
        self.invincible_timer = 0
        self.can_damage = False
        self.is_dead = False
        self.is_attacking = False
        self.death_animation_complete = False

        self.hit_flash_timer = 0

        self.rest_timer = 0
        self.rest_duration = 420

        self.attack_order = ["satyr", "mudman", "dragon"]
        self.current_attack_index = 0

        self.spawn_request = None
        self.has_spawned_this_attack = False

        self.animation_speeds = {
            "intro": 12,
            "attack": 12,
            "splash": 4,
            "rest": 4,
        }

        self.update_texture()

    def get_anim_speed(self):
        return self.animation_speeds.get(self.state, 4)

    def get_current_attack_type(self):
        return self.attack_order[self.current_attack_index]

    def next_attack(self):
        self.current_attack_index = (self.current_attack_index + 1) % len(self.attack_order)

    def update(self, delta_time):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            # Чередование: белая вспышка / нормальный вид
            if self.hit_flash_timer % 2 == 1:
                self.color = (200, 200, 255)  # холодная белая вспышка
            else:
                self.color = (255, 255, 255)
            if self.hit_flash_timer <= 0:
                self.color = (255, 255, 255)
                self.alpha = 255

        if self.is_dead:
            self.animation_speed_counter += 1
            if self.animation_speed_counter >= self.get_anim_speed():
                self.animation_speed_counter = 0
                self.update_animation()
                self.update_texture()
            return

        if self.hp <= 0 and not self.is_dead:
            self.is_dead = True
            self.state = "splash"
            self.current_frame = 0
            self.animation_speed_counter = 0
            self.can_damage = False
            return

        if self.invincible:
            self.invincible_timer -= 1
            self.alpha = 0
            if self.invincible_timer <= 0:
                self.invincible = False
                self.alpha = 255

        super().update()

        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.get_anim_speed():
            self.animation_speed_counter = 0
            self.update_animation()
            self.update_texture()

        if self.state == "intro" and not self.start_intro_complete:
            if self.current_frame >= len(RockLion._texture_cache["intro"][self.direction]) - 1:
                self.start_intro_complete = True
                self.start = False
                self.can_damage = True
                self.state = "rest"
                self.rest_timer = 0

        elif self.state == "rest":
            self.rest_timer += 1
            if self.rest_timer >= self.rest_duration:
                self.state = "attack"
                self.current_frame = 0
                self.animation_speed_counter = 0
                self.is_attacking = True
                self.has_spawned_this_attack = False

    def update_animation(self):
        if self.state == "intro":
            textures_list = RockLion._texture_cache["intro"][self.direction]
            if self.current_frame < len(textures_list) - 1:
                self.current_frame += 1

        elif self.state == "rest":
            pass

        elif self.state == "attack":
            textures_list = RockLion._texture_cache["attack"][self.direction]

            if self.current_frame == 8 and not self.has_spawned_this_attack:
                self.spawn_request = self.get_current_attack_type()
                self.has_spawned_this_attack = True

            if self.current_frame < len(textures_list) - 1:
                self.current_frame += 1
            else:
                self.is_attacking = False
                self.next_attack()
                self.state = "rest"
                self.rest_timer = 0
                self.current_frame = 0

        elif self.state == "splash":
            textures_list = RockLion._texture_cache["splash"][self.direction]
            if self.current_frame < len(textures_list) - 1:
                self.current_frame += 1
            else:
                self.death_animation_complete = True
                self.remove_from_sprite_lists()

    def update_texture(self):
        if self.state == "rest":
            textures_list = RockLion._texture_cache["intro"][self.direction]
            if textures_list:
                self.texture = textures_list[0]
        else:
            textures_list = RockLion._texture_cache[self.state][self.direction]
            if textures_list and 0 <= self.current_frame < len(textures_list):
                self.texture = textures_list[self.current_frame]

    def take_damage(self, damage):
        if not self.invincible and not self.is_dead:
            self.hp -= damage
            self.hit_flash_timer = ENEMY_HIT_FLASH_DURATION
            if self.hp <= 0:
                self.is_dead = True
                self.state = "splash"
                self.current_frame = 0
                self.animation_speed_counter = 0
                self.can_damage = False


class DragonFire(arcade.Sprite):
    _texture_cache_normal = None
    _texture_cache_pink = None

    @classmethod
    def _load_textures(cls, is_pink=False):
        if is_pink:
            if cls._texture_cache_pink is not None:
                return cls._texture_cache_pink
            text = "Pink/lv3-2_baby_dragon_fireball_pink_"
        else:
            if cls._texture_cache_normal is not None:
                return cls._texture_cache_normal
            text = "Normal/lv3-2_baby_dragon_fireball_"

        base = "assets/images/enemies/Baby Dragon"
        textures_list = []
        for i in range(1, 21):
            texture = arcade.load_texture(
                f"{base}/{text}{'0' * (4 - len(str(i)))}{i}.png"
            )
            textures_list.append(texture)

        if is_pink:
            cls._texture_cache_pink = textures_list
        else:
            cls._texture_cache_normal = textures_list

        return textures_list

    def __init__(self, x, y, target_x, target_y, is_pink=False):
        scale = 1
        self.textures_list = DragonFire._load_textures(is_pink)
        super().__init__(self.textures_list[0], scale=scale)
        self.center_x = x
        self.center_y = y
        self.lifetime = 480

        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            self.change_x = (dx / distance) * DRAGON_FIRE_SPEED
            self.change_y = (dy / distance) * DRAGON_FIRE_SPEED
            self.angle = math.degrees(math.atan2(dy, dx))
            if self.angle < -90 or self.angle > 90:
                self.texture = self.texture.flip_left_right()
        else:
            self.change_x = 0
            self.change_y = 0
            self.angle = 0

        self.damage = 30
        self.is_pink = is_pink
        self.can_be_parried = is_pink
        self.current_frame = 0
        self.counter = 0

    def update(self, delta_time):
        self.counter += 1
        if self.counter >= 3:
            self.current_frame = (self.current_frame + 1) % len(self.textures_list)
            self.counter = 0

        self.texture = self.textures_list[self.current_frame]

        if self.angle < -90 or self.angle > 90:
            self.texture = self.texture.flip_left_right()

        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.top >= SCREEN_HEIGHT or self.bottom <= 0:
            self.change_y *= -1
        if self.right >= SCREEN_WIDTH or self.left <= 0:
            self.change_x *= -1
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

        if (
            self.right < 0
            or self.left > SCREEN_WIDTH
            or self.bottom > SCREEN_HEIGHT
            or self.top < 0
        ):
            self.remove_from_sprite_lists()


class BabyDragon(arcade.Sprite):
    _texture_cache = None

    @classmethod
    def _load_textures(cls):
        if cls._texture_cache is not None:
            return

        cls._texture_cache = {
            "down": {"idle": [], "fly_up": [], "attack": []},
            "left": {"idle": [], "fly_up": [], "attack": []},
            "right": {"idle": [], "fly_up": [], "attack": []},
        }

        base = "assets/images/enemies/Baby Dragon/Down"

        for i in range(1, 20):
            path = f"{base}/Idle/lv3-2_baby_dragon_idle_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["down"]["idle"].append(texture)

        for i in range(1, 6):
            path = f"{base}/Fly up/lv3-2_baby_dragon_fly_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["down"]["fly_up"].append(texture)

        for i in range(1, 28):
            path = f"{base}/Attack/lv3-2_baby_dragon_attack_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["down"]["attack"].append(texture)

    def __init__(self, x, y, direction_x, dragon_type=0, position_type="down"):
        BabyDragon._load_textures()
        super().__init__(BabyDragon._texture_cache[position_type]["idle"][0])

        self.dragon_type = dragon_type
        self.position_type = position_type

        if position_type == "left":
            self.center_x = 100
            self.direction = "right"
        elif position_type == "right":
            self.center_x = SCREEN_WIDTH - 100
            self.direction = "left"
        else:
            self.center_x = x

        self.center_y = SCREEN_HEIGHT + 100
        self.change_x = 0
        self.change_y = -3

        self.state = "idle"
        self.current_frame = 0
        self.animation_speed_counter = 0
        self.animation_speed = 4
        self.hp = 30
        self.invincible = False
        self.invincible_timer = 0
        self.can_damage = False
        self.is_dead = False
        self.target_y = 600 if position_type == "down" else 400
        self.attack_done = False
        self.disappear = False

        self.hit_flash_timer = 0

        self.is_shooting = False
        self.shoot_animation_loops = 0
        self.shoot_loops_needed = 0
        self.current_shoot_frame = 0
        self.shoot_animation_delay = 0
        self.shoot_pattern = cycle([False, True])

        self.shoot_timer = 0
        self.shoot_cooldown = 60
        self.can_shoot = False

        self.shoot_counter = 0
        self.max_shots = 3 if dragon_type == 2 else float("inf")
        self.has_shot_triple = False
        self.triple_shot_used = False

    def shoot_at_player(self, player):
        if not self.can_shoot or self.shoot_timer < self.shoot_cooldown:
            return None

        if self.dragon_type == 2 and self.triple_shot_used:
            return None

        fireballs = []

        if self.dragon_type == 0:
            fireball = DragonFire(
                self.center_x, self.center_y, player.center_x, player.center_y, False
            )
            fireball.knockable = True
            fireballs.append(fireball)
            self.shoot_loops_needed = 1

        elif self.dragon_type == 1:
            fireball = DragonFire(
                self.center_x, self.center_y, player.center_x, player.center_y, True
            )
            fireball.knockable = True
            fireballs.append(fireball)
            self.shoot_loops_needed = 1

        elif self.dragon_type == 2:
            if self.has_shot_triple:
                return None

            is_pink = next(self.shoot_pattern)

            for angle_offset in [-15, 0, 15]:
                dx = player.center_x - self.center_x
                dy = player.center_y - self.center_y
                distance = math.sqrt(dx**2 + dy**2)
                base_angle = math.atan2(dy, dx)

                angle = base_angle + math.radians(angle_offset)
                target_x = self.center_x + distance * math.cos(angle)
                target_y = self.center_y + distance * math.sin(angle)

                fireball = DragonFire(
                    self.center_x,
                    self.center_y,
                    target_x,
                    target_y,
                    is_pink if angle_offset == 0 else False,
                )
                fireball.knockable = False
                fireballs.append(fireball)

            self.has_shot_triple = True
            self.triple_shot_used = True
            self.shoot_loops_needed = 2

        self.is_shooting = True
        self.shoot_animation_loops = 0
        self.current_shoot_frame = 0
        self.shoot_animation_delay = 0
        self.shoot_timer = 0

        return fireballs

    def update(self, delta_time):
        if self.is_dead or self.disappear:
            return

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            # Чередование: белая вспышка / нормальный вид
            if self.hit_flash_timer % 2 == 1:
                self.color = (200, 200, 255)  # холодная белая вспышка
            else:
                self.color = (255, 255, 255)
            if self.hit_flash_timer <= 0:
                self.color = (255, 255, 255)
                self.alpha = 255

        super().update()

        if self.is_shooting:
            self.update_shoot_animation()
            return

        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.animation_speed:
            self.animation_speed_counter = 0
            self.update_animation()
            self.update_texture()

        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.state == "idle":
            if self.center_y <= self.target_y:
                self.state = "attack"
                self.change_y = 0
                self.current_frame = 0
                self.animation_speed_counter = 0
                self.can_damage = True
                self.can_shoot = True

        elif self.state == "attack":
            if not self.attack_done:
                if self.current_frame >= len(self._get_current_textures("attack")) - 1:
                    self.attack_done = True
                    self.state = "fly_up"
                    self.current_frame = 0
                    self.animation_speed_counter = 0
                    self.change_y = 5
                    self.can_damage = False
                    self.can_shoot = False

        elif self.state == "fly_up":
            if self.center_y > SCREEN_HEIGHT + 100:
                self.disappear = True
                self.remove_from_sprite_lists()

        if self.can_shoot:
            self.shoot_timer += 1

    def update_shoot_animation(self):
        self.shoot_animation_delay += 1

        if self.shoot_animation_delay >= 3:
            self.shoot_animation_delay = 0
            self.current_shoot_frame += 1

            attack_textures = self._get_current_textures("attack")

            if self.current_shoot_frame >= len(attack_textures):
                self.shoot_animation_loops += 1
                self.current_shoot_frame = 0

                if self.shoot_animation_loops >= self.shoot_loops_needed:
                    self.is_shooting = False
                    self.state = "attack"
                    self.attack_done = False
                    self.current_frame = 0
                    return

            self.texture = attack_textures[self.current_shoot_frame]

    def _get_current_textures(self, state):
        return BabyDragon._texture_cache[self.position_type][state]

    def update_animation(self):
        if self.state == "idle":
            textures = self._get_current_textures("idle")
            if textures:
                self.current_frame = (self.current_frame + 1) % len(textures)

        elif self.state == "attack":
            if not self.attack_done:
                textures = self._get_current_textures("attack")
                if textures and self.current_frame < len(textures) - 1:
                    self.current_frame += 1

        elif self.state == "fly_up":
            textures = self._get_current_textures("fly_up")
            if textures:
                self.current_frame = (self.current_frame + 1) % len(textures)

    def update_texture(self):
        textures = self._get_current_textures(self.state)
        if textures and 0 <= self.current_frame < len(textures):
            self.texture = textures[self.current_frame]

    def take_damage(self, damage):
        if not self.invincible and not self.is_dead and not self.disappear:
            self.hp -= damage
            self.hit_flash_timer = ENEMY_HIT_FLASH_DURATION
            if self.hp <= 0:
                self.is_dead = True
                self.can_damage = False
                self.can_shoot = False
                self.remove_from_sprite_lists()


class Mudman(arcade.Sprite):
    _texture_cache = None

    @classmethod
    def _load_textures(cls):
        if cls._texture_cache is not None:
            return

        cls._texture_cache = {
            "intro": {"right": [], "left": []},
            "splash": {"right": [], "left": []},
        }

        base = "assets/images/enemies/Mudman"

        for i in range(1, 22):
            path = f"{base}/Intro/lv3-2_mudman_small_intro_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["intro"]["left"].append(texture)

        for texture in cls._texture_cache["intro"]["left"]:
            cls._texture_cache["intro"]["right"].append(texture.flip_left_right())

        for i in range(1, 11):
            path = f"{base}/Splash/Small/One/lv3-2_mudman_small_splash_one_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["splash"]["left"].append(texture)

        for texture in cls._texture_cache["splash"]["left"]:
            cls._texture_cache["splash"]["right"].append(texture.flip_left_right())

    def __init__(self, x, y, direction_x, shoot=None):
        Mudman._load_textures()
        texture = Mudman._texture_cache["intro"]["left"][0]
        super().__init__(texture)

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0

        self.direction = "right" if direction_x > 0 else "left"
        self.start = True
        self.on_ground = False
        self.state = "intro"
        self.current_frame = 0
        self.animation_speed_counter = 0
        self.animation_speed = 4
        self.start_intro_complete = False
        self.hp = 30
        self.invincible = False
        self.invincible_timer = 0
        self.can_damage = False
        self.is_dead = False

        self.hit_flash_timer = 0

        self.update_texture()

    def update(self, delta_time):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            # Чередование: белая вспышка / нормальный вид
            if self.hit_flash_timer % 2 == 1:
                self.color = (200, 200, 255)  # холодная белая вспышка
            else:
                self.color = (255, 255, 255)
            if self.hit_flash_timer <= 0:
                self.color = (255, 255, 255)
                self.alpha = 255

        if self.is_dead:
            self.animation_speed_counter += 1
            if self.animation_speed_counter >= self.animation_speed:
                self.animation_speed_counter = 0
                self.update_animation()
                self.update_texture()
            return

        if self.hp <= 0 and not self.is_dead:
            self.is_dead = True
            self.state = "splash"
            self.current_frame = 0
            self.animation_speed_counter = 0
            self.can_damage = False
            return

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        super().update()

        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.animation_speed:
            self.animation_speed_counter = 0
            self.update_animation()
            self.update_texture()

        if self.start and not self.start_intro_complete:
            if (
                self.current_frame
                >= len(Mudman._texture_cache["intro"][self.direction]) - 1
            ):
                self.start_intro_complete = True
                self.start = False
                self.state = "intro"
                self.can_damage = True
        elif not self.start and self.start_intro_complete:
            self.can_damage = True

    def update_animation(self):
        if self.state == "intro":
            textures_list = Mudman._texture_cache["intro"][self.direction]
            if textures_list:
                if not self.start_intro_complete:
                    if self.current_frame < len(textures_list) - 1:
                        self.current_frame += 1
        elif self.state == "splash":
            textures_list = Mudman._texture_cache["splash"][self.direction]
            if textures_list:
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    self.remove_from_sprite_lists()

    def update_texture(self):
        textures_list = Mudman._texture_cache[self.state][self.direction]
        if textures_list and 0 <= self.current_frame < len(textures_list):
            self.texture = textures_list[self.current_frame]

    def take_damage(self, damage):
        if not self.invincible and not self.is_dead:
            self.hp -= damage
            self.hit_flash_timer = ENEMY_HIT_FLASH_DURATION
            if self.hp <= 0:
                self.is_dead = True
                self.state = "splash"
                self.current_frame = 0
                self.animation_speed_counter = 0
                self.can_damage = False


class Satyr(arcade.Sprite):
    _texture_cache = None

    @classmethod
    def _load_textures(cls):
        if cls._texture_cache is not None:
            return

        cls._texture_cache = {
            "jump": {"right": [], "left": []},
            "run": {"right": [], "left": []},
            "turn": {"right": [], "left": []},
        }

        base = "assets/images/enemies/Satyr"

        for i in range(1, 20):
            path = f"{base}/Jump/lv3-2_satyr_jump_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["jump"]["left"].append(texture)

        for texture in cls._texture_cache["jump"]["left"]:
            cls._texture_cache["jump"]["right"].append(texture.flip_left_right())

        for i in range(1, 25):
            path = f"{base}/Skip/lv3-2_satyr_skip_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["run"]["left"].append(texture)

        for texture in cls._texture_cache["run"]["left"]:
            cls._texture_cache["run"]["right"].append(texture.flip_left_right())

        for i in range(1, 5):
            path = f"{base}/Turn/lv3-2_satyr_turn_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["turn"]["left"].append(texture)

        for texture in cls._texture_cache["turn"]["left"]:
            cls._texture_cache["turn"]["right"].append(texture.flip_left_right())

    def __init__(self, x, y, direction_x, shoot=None):
        Satyr._load_textures()
        super().__init__(Satyr._texture_cache["jump"]["left"][0])

        self.center_x = x
        self.center_y = y
        self.change_x = direction_x * 2
        self.change_y = 0

        self.direction = "right" if direction_x > 0 else "left"
        self.start = True
        self.on_ground = False
        self.state = "jump"
        self.current_frame = 0
        self.animation_speed_counter = 0
        self.animation_speed = 4
        self.start_jump_complete = False
        self.jump_phase = "up"
        self.jump_frames = 0
        self.hp = 30
        self.invincible = False
        self.invincible_timer = 0
        self.can_damage = False

        self.hit_flash_timer = 0

        self.update_texture()

    def update(self, delta_time):
        if self.hp <= 0:
            return

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            # Чередование: белая вспышка / нормальный вид
            if self.hit_flash_timer % 2 == 1:
                self.color = (200, 200, 255)  # холодная белая вспышка
            else:
                self.color = (255, 255, 255)
            if self.hit_flash_timer <= 0:
                self.color = (255, 255, 255)
                self.alpha = 255

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        super().update()

        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.animation_speed:
            self.animation_speed_counter = 0
            self.update_animation()
            self.update_texture()

        if self.start and not self.start_jump_complete:
            self.jump_frames += 1
            if self.jump_frames <= 20:
                self.change_y = 10
            elif self.jump_frames <= 40:
                self.change_y = -8
            else:
                self.start_jump_complete = True
                self.change_y = 0
        else:
            if not self.on_ground:
                self.change_y -= 0.5

        self.center_y += self.change_y
        self.center_x += self.change_x

        ground_level = 50
        if self.bottom <= ground_level:
            self.bottom = ground_level
            self.on_ground = True
            self.change_y = 0

            if self.start and self.start_jump_complete:
                if self.current_frame >= 15:
                    self.start = False
                    self.state = "run"
                    self.current_frame = 0
                    self.animation_speed_counter = 0
                    self.can_damage = True
        else:
            self.on_ground = False

        if self.left < 0:
            self.left = 0
            self.change_x *= -1
            self.direction = "right" if self.change_x > 0 else "left"
            self.current_frame = 0

        elif self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
            self.change_x *= -1
            self.direction = "right" if self.change_x > 0 else "left"
            self.current_frame = 0

    def update_animation(self):
        if self.start:
            textures_list = Satyr._texture_cache["jump"][self.direction]
            if textures_list:
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
        else:
            textures_list = Satyr._texture_cache["run"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

    def update_texture(self):
        if self.start:
            textures_list = Satyr._texture_cache["jump"][self.direction]
        else:
            textures_list = Satyr._texture_cache["run"][self.direction]

        if textures_list and 0 <= self.current_frame < len(textures_list):
            self.texture = textures_list[self.current_frame]

    def take_damage(self, damage):
        if not self.invincible:
            self.hp -= damage
            self.hit_flash_timer = ENEMY_HIT_FLASH_DURATION
            if self.hp <= 0:
                self.remove_from_sprite_lists()


class Bullet(arcade.Sprite):
    def __init__(self, x, y, direction_x, direction_y, shoot, angle=0, is_ex=False):
        if is_ex:
            scale = 1.2
        else:
            scale = 0.7
        super().__init__(shoot, scale=scale)
        self.center_x = x
        self.center_y = y
        speed = EX_BULLET_SPEED if is_ex else BULLET_SPEED
        self.change_x = direction_x * speed
        self.change_y = direction_y * speed
        self.lifetime = 120
        self.angle = angle
        if angle != 0:
            self.angle = angle
        self.is_ex = is_ex
        self.damage = 30 if is_ex else 5

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()


class CupHead(arcade.Sprite):
    _bullet_variants = None

    @classmethod
    def _prepare_bullet_textures(cls):
        if cls._bullet_variants is not None:
            return

        base = get_bullet_texture("assets/images/cuphead/shoots/peashooter.png")
        ex_base = get_bullet_texture("assets/images/cuphead/Supers/Mega_Blast.png")

        cls._bullet_variants = {
            "peashooter_right": base,
            "peashooter_left": base.flip_left_right(),
            "peashooter_up": base.rotate_180(),
            "peashooter_down": base,
            "peashooter_diag_right": base.rotate_90(3),
            "peashooter_diag_left": base.rotate_90(3),
            "ex_right": ex_base,
            "ex_left": ex_base.flip_left_right(),
        }

    def __init__(self, filename, scale, speed):
        super().__init__(filename, scale)
        CupHead._prepare_bullet_textures()

        self.textures_dict = {
            "idle": {"right": [], "left": []},
            "run": {"right": [], "left": []},
            "jump": {"right": [], "left": []},
            "duck": {"right": [], "left": []},
            "duck_idle": {"right": [], "left": []},
            "dash": {"right": [], "left": []},
            "flex": {"right": [], "left": []},
            "dash_back": {"right": [], "left": []},
            "shoot_straight": {"right": [], "left": []},
            "shoot_up": {"right": [], "left": []},
            "shoot_down": {"right": [], "left": []},
            "shoot_diagonal_up": {"right": [], "left": []},
            "shoot_diagonal_down": {"right": [], "left": []},
            "shoot_straight_running": {"right": [], "left": []},
            "shoot_diagonal_up_running": {"right": [], "left": []},
            "shoot_diagonal_up_running_left": {"right": [], "left": []},
            "duck_shoot": {"right": [], "left": []},
            "ex_straight": {"right": [], "left": []},
            "hit": {"right": [], "left": []},
            "death": {"right": [], "left": []},
            "ghost": {"right": [], "left": []},
            "parry": {"right": [], "left": []},
        }

        base = "assets/images/cuphead"

        for i in range(1, 6):
            path = f'{base}/Idle/cuphead_idle_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["idle"]["right"].append(texture)

        for texture in self.textures_dict["idle"]["right"]:
            self.textures_dict["idle"]["left"].append(texture.flip_left_right())

        self.texture = self.textures_dict["idle"]["right"][0]

        for i in range(1, 17):
            path = f'{base}/Run/Normal/cuphead_run_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["run"]["right"].append(texture)

        for texture in self.textures_dict["run"]["right"]:
            self.textures_dict["run"]["left"].append(texture.flip_left_right())

        for i in range(1, 9):
            path = f"{base}/Jump/Cuphead/cuphead_jump_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["jump"]["right"].append(texture)

        for texture in self.textures_dict["jump"]["right"]:
            self.textures_dict["jump"]["left"].append(texture.flip_left_right())

        for i in range(1, 9):
            if i == 3:
                continue
            path = f"{base}/Duck/idle/cuphead_duck_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["duck"]["right"].append(texture)

        for texture in self.textures_dict["duck"]["right"]:
            self.textures_dict["duck"]["left"].append(texture.flip_left_right())

        for i in range(1, 6):
            path = f"{base}/Duck/idle/cuphead_duck_idle_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["duck_idle"]["right"].append(texture)

        for texture in self.textures_dict["duck_idle"]["right"]:
            self.textures_dict["duck_idle"]["left"].append(texture.flip_left_right())

        for i in range(-1, 6):
            path = f'{base}/Dash/Ground/cuphead_dash_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["dash"]["right"].append(texture)

        for texture in self.textures_dict["dash"]["right"]:
            self.textures_dict["dash"]["left"].append(texture.flip_left_right())

        for i in range(4, -2, -1):
            path = f'{base}/Dash/Ground/cuphead_dash_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["dash_back"]["right"].append(texture)

        for texture in self.textures_dict["dash_back"]["right"]:
            self.textures_dict["dash_back"]["left"].append(texture.flip_left_right())

        for i in range(1, 44):
            path = f'{base}/Intros/Flex/cuphead_intro_b_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["flex"]["right"].append(texture)

        for i in range(1, 4):
            path = f"{base}/Shoot/Straight/cuphead_shoot_straight_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_straight"]["right"].append(texture)

        for texture in self.textures_dict["shoot_straight"]["right"]:
            self.textures_dict["shoot_straight"]["left"].append(texture.flip_left_right())

        for i in range(1, 4):
            path = f"{base}/Shoot/Up/cuphead_shoot_up_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_up"]["right"].append(texture)

        for texture in self.textures_dict["shoot_up"]["right"]:
            self.textures_dict["shoot_up"]["left"].append(texture.flip_left_right())

        for i in range(1, 4):
            path = f"{base}/Shoot/Down/cuphead_shoot_down_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_down"]["right"].append(texture)

        for texture in self.textures_dict["shoot_down"]["right"]:
            self.textures_dict["shoot_down"]["left"].append(texture.flip_left_right())

        for i in range(1, 4):
            path = f"{base}/Shoot/Diagonal Up/cuphead_shoot_diagonal_up_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_diagonal_up"]["right"].append(texture)

        for texture in self.textures_dict["shoot_diagonal_up"]["right"]:
            self.textures_dict["shoot_diagonal_up"]["left"].append(texture.flip_left_right())

        for i in range(1, 17):
            path = f"{base}/Run/Shooting/Straight/cuphead_run_shoot_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_straight_running"]["right"].append(texture)

        for texture in self.textures_dict["shoot_straight_running"]["right"]:
            self.textures_dict["shoot_straight_running"]["left"].append(texture.flip_left_right())

        for i in range(1, 17):
            path = f"{base}/Run/Shooting/Diagonal Up/cuphead_run_shoot_diagonal_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_diagonal_up_running"]["right"].append(texture)

        for texture in self.textures_dict["shoot_diagonal_up_running"]["right"]:
            self.textures_dict["shoot_diagonal_up_running"]["left"].append(texture.flip_left_right())

        for i in range(1, 17):
            path = f"{base}/Run/Shooting/Diagonal Up/cuphead_run_shoot_diagonal_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_diagonal_up_running_left"]["left"].append(texture)

        for texture in self.textures_dict["shoot_diagonal_up_running_left"]["left"]:
            self.textures_dict["shoot_diagonal_up_running_left"]["right"].append(texture.flip_left_right())

        for i in range(1, 4):
            path = f"{base}/Duck/Shoot/cuphead_duck_shoot_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["duck_shoot"]["right"].append(texture)

        for texture in self.textures_dict["duck_shoot"]["right"]:
            self.textures_dict["duck_shoot"]["left"].append(texture.flip_left_right())

        for i in range(1, 16):
            path = f"{base}/Special Attck/Straight/Ground/cuphead_ex_straight_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["ex_straight"]["right"].append(texture)

        for texture in self.textures_dict["ex_straight"]["right"]:
            self.textures_dict["ex_straight"]["left"].append(texture.flip_left_right())

        for i in range(1, 7):
            path = f"{base}/Hit/Ground/cuphead_hit_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["hit"]["right"].append(texture)

        for texture in self.textures_dict["hit"]["right"]:
            self.textures_dict["hit"]["left"].append(texture.flip_left_right())

        for i in range(1, 17):
            path = f"{base}/Death/cuphead_death_body_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["death"]["right"].append(texture)

        for texture in self.textures_dict["death"]["right"]:
            self.textures_dict["death"]["left"].append(texture.flip_left_right())

        for i in range(1, 25):
            path = f"{base}/Ghost/cuphead_ghost_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["ghost"]["right"].append(texture)

        for texture in self.textures_dict["ghost"]["right"]:
            self.textures_dict["ghost"]["left"].append(texture.flip_left_right())

        for i in range(1, 9):
            path = f"{base}/Parry/Hand/cuphead_parry_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["parry"]["right"].append(texture)

        for texture in self.textures_dict["parry"]["right"]:
            self.textures_dict["parry"]["left"].append(texture.flip_left_right())

        self.state = "flex"
        self.direction = "right"
        self.current_frame = 0
        self.animation_speed_counter = 0
        self.moving = False
        self.on_ground = True
        self.duck = False
        self.duck_idle = False
        self.duck_direction = 1
        self.idle_direction = 1
        self.idle_frames_count = 5
        self.dashing = False
        self.need_dash_teleport = False
        self.dash_direction_multiplier = 1
        self.flexing = True
        self.ex_straight = False
        self.can_move = True
        self.dashing_back = False
        self.death = False
        self.ghost_gone = False
        self.hp = 3
        self.invincible = False
        self.invincible_timer = 0
        self.just_took_damage = False
        self.disable_input = False
        self.ex_cards = 0
        self.max_ex_cards = 5
        self.cards_per_parry = 1
        self.cards_per_hit = 0.02

        self.can_shoot = True
        self.can_dash = True
        self.force_stop_movement = False

        self.bullets_to_add = []

        self.dash_start_moving = False
        self.dash_start_direction = "right"
        self.key = False
        self.count_dash = 1

        self.keys_pressed = {"left": False, "right": False, "up": False, "down": False}

        self.shooting_straight = False
        self.shooting_up = False
        self.shooting_down = False
        self.shooting_diagonal_down = False
        self.shooting_diagonal_up = False

        self.shooting = False
        self.shoot_cooldown = 0
        self.shoot_timer = 0

        self.shoot_diagonal_up_running = False
        self.shoot_straight_running = False
        self.shoot_diagonal_up_running_left = False
        self.duck_shooting = False

        self.hit = False
        self.hit_check = False

        self.ghost = False
        self.ghost_timer = 0
        self.ghost_duration = 120

        self.parry = False
        self.parry_timer = 0
        self.parry_cooldown = 0
        self.can_parry = True
        self.parry_success = False
        self.parry_success_timer = 0
        self.ex_meter = 0
        self.max_ex_meter = 5
        self.can_air_parry = False
        self.air_parry_window = 0
        self.in_air_parry_window = False
        self.has_jumped = False

        self.animation_speeds = {
            "idle": 8,
            "run": 4,
            "jump": 6,
            "duck": 6,
            "duck_idle": 10,
            "dash": 4,
            "flex": 8,
            "dash_back": 2,
            "duck_shoot": 8,
            "shoot_down": 2,
            "shoot_up": 8,
            "shoot_straight": 8,
            "shoot_diagonal_down": 1,
            "shoot_diagonal_up": 1,
            "shoot_straight_running": 8,
            "shoot_diagonal_up_running": 8,
            "shoot_diagonal_up_running_left": 8,
            "ex_straight": 6,
            "hit": 5,
            "death": 5,
            "ghost": 5,
            "parry": 6,
        }

    def update(self, delta_time):
        super().update()

        if self.force_stop_movement:
            self.change_x = 0
            self.moving = False

        if self.ghost:
            self.process_ghost_state()
            return

        if self.death:
            self.change_x = 0
            self.change_y = 0
            self.moving = False
            self.can_move = False
            self.disable_input = True
            self.update_death_animation()
            return

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.alpha = 255
            else:
                if self.invincible_timer % 4 < 2:
                    self.alpha = 128
                else:
                    self.alpha = 255

        if self.parry:
            self.parry_timer -= 1
            if self.parry_timer <= 0:
                self.parry = False
                self.can_parry = True
                if self.state == "parry":
                    if not self.on_ground:
                        self.state = "jump"
                    else:
                        self.state = "idle"
                    self.current_frame = 0
                    self.animation_speed_counter = 0

        if self.parry_cooldown > 0:
            self.parry_cooldown -= 1

        if self.parry_success:
            self.parry_success_timer -= 1
            if self.parry_success_timer <= 0:
                self.parry_success = False

        if self.key:
            self.center_x = self.center_x + (50 * (-1, 1)[self.direction == "right"])
            self.key = False

        if self.hp <= 0:
            self.death = True
            new_state = "death"
        elif self.hit:
            new_state = "hit"
        elif self.ex_straight:
            new_state = "ex_straight"
        elif self.flexing:
            new_state = "flex"
        elif self.dashing_back:
            new_state = "dash_back"
        elif self.parry:
            new_state = "parry"
        elif not self.on_ground and not self.dashing:
            new_state = "jump"
        elif self.dashing:
            new_state = "dash"
        elif self.shooting and self.duck and self.can_shoot:
            new_state = "duck_shoot"
            self.duck_shooting = True
        elif self.shooting and self.moving and self.can_shoot:
            if self.keys_pressed["up"]:
                if self.direction == "right":
                    new_state = "shoot_diagonal_up_running"
                    self.shoot_diagonal_up_running = True
                else:
                    new_state = "shoot_diagonal_up_running_left"
                    self.shoot_diagonal_up_running_left = True
                self.shoot_straight_running = False
                self.shooting_straight = False
            else:
                new_state = "shoot_straight_running"
                self.shoot_straight_running = True
                self.shoot_diagonal_up_running = False
                self.shoot_diagonal_up_running_left = False
                self.shooting_straight = False
        elif self.shoot_straight_running:
            new_state = "shoot_straight_running"
        elif self.shoot_diagonal_up_running:
            new_state = "shoot_diagonal_up_running"
        elif self.shoot_diagonal_up_running_left:
            new_state = "shoot_diagonal_up_running_left"
        elif (
            self.shooting
            and not self.moving
            and not self.duck
            and self.on_ground
            and self.can_shoot
        ):
            if self.keys_pressed["up"]:
                new_state = "shoot_up"
                self.shooting_up = True
                self.shooting_straight = False
            elif self.keys_pressed["down"]:
                new_state = "shoot_down"
                self.shooting_down = True
                self.shooting_straight = False
            else:
                new_state = "shoot_straight"
                self.shooting_straight = True
                self.shooting_up = False
                self.shooting_down = False
        elif self.shooting_straight:
            new_state = "shoot_straight"
        elif self.shooting_diagonal_up:
            new_state = "shoot_diagonal_up"
        elif self.shooting_diagonal_down:
            new_state = "shoot_diagonal_down"
        elif self.shooting_up:
            new_state = "shoot_up"
        elif self.shooting_down:
            new_state = "shoot_down"
        elif self.duck:
            if self.state == "duck" and self.duck_direction == 1:
                if self.current_frame >= len(self.textures_dict["duck"][self.direction]) - 1:
                    new_state = "duck_idle"
                    self.current_frame = 0
                    self.duck_idle = True
                else:
                    new_state = "duck"
            elif self.state == "duck" and self.duck_direction == -1:
                new_state = "duck"
                self.duck_direction = 1
                self.current_frame = len(self.textures_dict["duck"][self.direction]) - 1 - self.current_frame
            elif self.state == "duck_idle":
                new_state = "duck_idle"
            else:
                new_state = "duck"
                self.duck_direction = 1
                self.current_frame = 0
                self.duck_idle = False
        elif not self.duck and (self.state in ["duck", "duck_idle", "duck_shoot"]):
            if self.state == "duck_idle":
                new_state = "duck"
                self.duck_direction = -1
                self.current_frame = len(self.textures_dict["duck"][self.direction]) - 1
                self.duck_idle = False
            elif self.state == "duck" and self.duck_direction == 1:
                new_state = "duck"
                self.duck_direction = -1
                self.current_frame = len(self.textures_dict["duck"][self.direction]) - 1 - self.current_frame
                self.duck_idle = False
            elif self.state == "duck" and self.duck_direction == -1:
                new_state = "duck"
                if self.current_frame <= 0:
                    new_state = "idle"
                    self.current_frame = 0
            elif self.state == "duck_shoot":
                new_state = "duck"
                self.duck_direction = -1
                self.current_frame = len(self.textures_dict["duck"][self.direction]) - 1
                self.duck_idle = False
        elif self.moving and self.change_x != 0 and not self.duck and not self.force_stop_movement:
            new_state = "run"
        else:
            new_state = "idle"

        if new_state != self.state:
            self.state = new_state
            self.current_frame = 0
            self.animation_speed_counter = 0
            self.idle_direction = 1
            self.update_texture()
        else:
            self.animation_speed_counter += 1
            animation_speed = self.animation_speeds[self.state]

            if animation_speed > 0 and self.animation_speed_counter >= animation_speed:
                self.animation_speed_counter = 0
                self.update_animation()
                self.update_texture()

    def process_ghost_state(self):
        if not self.ghost:
            return

        if self.state != "ghost":
            self.state = "ghost"
            self.current_frame = 0
            self.animation_speed_counter = 0

        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.animation_speeds["ghost"]:
            self.animation_speed_counter = 0
            self.update_ghost_animation()

        self.change_y = 3

        self.ghost_timer += 1
        if self.ghost_timer >= self.ghost_duration:
            self.ghost_gone = True

    def update_ghost_animation(self):
        textures_list = self.textures_dict["ghost"]["right"]
        if textures_list:
            self.current_frame = (self.current_frame + 1) % len(textures_list)
            self.texture = textures_list[self.current_frame]

    def update_death_animation(self):
        textures_list = self.textures_dict["death"]["right"]
        if textures_list:
            if self.current_frame < len(textures_list) - 1:
                self.animation_speed_counter += 1
                if self.animation_speed_counter >= self.animation_speeds["death"]:
                    self.animation_speed_counter = 0
                    self.current_frame += 1
                    self.texture = textures_list[self.current_frame]
            else:
                self.ghost = True
                self.ghost_timer = 0
                self.state = "ghost"
                self.current_frame = 0
                self.animation_speed_counter = 0
                self.change_y = 5

    def update_animation(self):
        if self.state == "death":
            return

        if self.state == "hit":
            self.hit_check = True
            textures_list = self.textures_dict["hit"][self.direction]
            if textures_list:
                self.can_move = False
                self.force_stop_movement = True

                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    self.invincible = True
                    self.invincible_timer = 90
                    self.hit = False
                    self.hit_check = False
                    self.just_took_damage = False
                    self.can_shoot = True
                    self.can_dash = True
                    self.can_move = True
                    self.force_stop_movement = False
                return

        if self.state == "ex_straight":
            self.hit_check = False
            textures_list = self.textures_dict["ex_straight"][self.direction]
            if textures_list:
                self.can_move = False
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                    if self.current_frame == 8:
                        self.create_ex_bullet()
                else:
                    self.can_move = True
                    self.current_frame = len(textures_list) - 1
                    self.ex_straight = False
                    self.change_y = 0
                return

        elif self.state == "flex":
            textures_list = self.textures_dict["flex"]["right"]
            if textures_list:
                self.can_move = False
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    self.can_move = True
                    self.current_frame = len(textures_list) - 1
                    self.flexing = False
                    self.change_y = 0
                return

        if self.state == "shoot_straight":
            textures_list = self.textures_dict["shoot_straight"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "shoot_up":
            textures_list = self.textures_dict["shoot_up"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "shoot_down":
            textures_list = self.textures_dict["shoot_down"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "shoot_diagonal_up":
            textures_list = self.textures_dict["shoot_diagonal_up"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "duck_shoot":
            textures_list = self.textures_dict["duck_shoot"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "shoot_straight_running":
            textures_list = self.textures_dict["shoot_straight_running"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "shoot_diagonal_up_running":
            textures_list = self.textures_dict["shoot_diagonal_up_running"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "shoot_diagonal_up_running_left":
            textures_list = self.textures_dict["shoot_diagonal_up_running_left"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "idle":
            self.count_dash = 1
            self.current_frame += self.idle_direction
            if self.current_frame >= self.idle_frames_count - 1:
                self.current_frame = self.idle_frames_count - 1
                self.idle_direction = -1
            elif self.current_frame <= 0:
                self.current_frame = 0
                self.idle_direction = 1

        elif self.state == "run":
            self.count_dash = 1
            textures_list = self.textures_dict["run"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        elif self.state == "parry":
            textures_list = self.textures_dict["parry"][self.direction]
            if textures_list:
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    self.parry = False
                    self.can_parry = True
                    self.parry_timer = 0
                    if not self.on_ground:
                        self.state = "jump"
                    else:
                        self.state = "idle"
                    self.current_frame = 0
                    self.animation_speed_counter = 0

        elif self.state == "jump":
            textures_list = self.textures_dict["jump"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        elif self.state == "duck":
            textures_list = self.textures_dict["duck"][self.direction]
            if textures_list:
                self.current_frame += self.duck_direction
                if self.current_frame < 0:
                    self.current_frame = 0
                elif self.current_frame >= len(textures_list):
                    self.current_frame = len(textures_list) - 1

        elif self.state == "duck_idle":
            textures_list = self.textures_dict["duck_idle"][self.direction]
            if textures_list:
                self.current_frame += self.idle_direction
                if self.current_frame >= len(textures_list) - 1:
                    self.current_frame = len(textures_list) - 1
                    self.idle_direction = -1
                elif self.current_frame <= 0:
                    self.current_frame = 0
                    self.idle_direction = 1

        elif self.state == "dash":
            self.change_y = 0
            textures_list = self.textures_dict["dash"][self.direction]
            if textures_list:
                if self.current_frame == 0:
                    self.dash_start_moving = self.moving
                    self.dash_start_direction = self.direction
                    self.dash_direction_multiplier = 1 if self.direction == "right" else -1
                    self.change_x = 7 * self.dash_direction_multiplier

                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    self.current_frame = len(textures_list) - 1
                    self.dashing = False
                    self.dashing_back = True

        elif self.state == "dash_back":
            textures_list = self.textures_dict["dash_back"][self.direction]
            if textures_list:
                if self.current_frame < len(textures_list) - 1:
                    if self.current_frame == 0:
                        self.dash_direction_multiplier = 1 if self.direction == "right" else -1
                        self.change_x = 7 * self.dash_direction_multiplier
                    self.current_frame += 1
                else:
                    self.dashing_back = False
                    if self.duck:
                        self.change_x = 0
                        self.moving = False
                    else:
                        any_key_pressed = self.keys_pressed["left"] or self.keys_pressed["right"]
                        if any_key_pressed:
                            if self.keys_pressed["left"]:
                                self.change_x = -SPEED
                                self.moving = True
                                self.direction = "left"
                            elif self.keys_pressed["right"]:
                                self.change_x = SPEED
                                self.moving = True
                                self.direction = "right"
                        else:
                            self.change_x = 0
                            self.moving = False

    def update_texture(self):
        textures_list = self.textures_dict[self.state][self.direction]
        if textures_list and 0 <= self.current_frame < len(textures_list):
            self.texture = textures_list[self.current_frame]

    def change_direction(self, new_direction):
        if new_direction != self.direction:
            self.direction = new_direction
            self.update_texture()

    def start_dash(self):
        if not self.dashing and not self.dashing_back and self.can_dash:
            self.dashing = True
            self.current_frame = 0
            self.animation_speed_counter = 0

    def create_ex_bullet(self):
        direction_x = 1 if self.direction == "right" else -1
        direction_y = 0
        bullet_angle = 0

        flag = self.direction == "right"
        pull_move = self.center_x + 60 * (-1, 1)[flag]
        pull_up = self.center_y

        if flag:
            shoot = CupHead._bullet_variants["ex_right"]
        else:
            shoot = CupHead._bullet_variants["ex_left"]

        bullet = Bullet(pull_move, pull_up, direction_x, direction_y, shoot, bullet_angle, is_ex=True)
        self.bullets_to_add.append(bullet)

    def process_parry(self, is_air_parry=False):
        if self.can_parry and self.parry_cooldown <= 0 and not self.hit:
            if is_air_parry and not self.on_ground and self.has_jumped:
                self.parry = True
                self.parry_timer = 60
                self.parry_cooldown = 30
                self.can_parry = False
                self.can_move = True
                self.state = "parry"
                self.current_frame = 0
                self.animation_speed_counter = 0
                return True
        return False

    def parry_successful(self):
        self.parry_success = True
        self.parry_success_timer = 30
        self.ex_cards = min(self.ex_cards + self.cards_per_parry, self.max_ex_cards)
        self.change_y = 6

    def gain_card_on_hit(self):
        self.ex_cards = min(self.ex_cards + self.cards_per_hit, self.max_ex_cards)

    def take_damage(self):
        if not self.invincible and not self.just_took_damage and not self.parry:
            self.hp -= 1
            self.hit = True
            self.just_took_damage = True
            self.invincible = True
            self.invincible_timer = 90

            self.can_shoot = False
            self.can_dash = False

            self.shooting = False
            self.shooting_straight = False
            self.shooting_up = False
            self.shooting_down = False
            self.shoot_straight_running = False
            self.shoot_diagonal_up_running = False
            self.shoot_diagonal_up_running_left = False
            self.duck_shooting = False
            self.shooting_diagonal_up = False

            self.dashing = False
            self.dashing_back = False

            self.force_stop_movement = True
            self.change_x = 0
            self.moving = False

            self.duck = False
            self.duck_shooting = False


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background = arcade.load_texture("assets/images/backgrounds/background.jpg")

    def setup(self):
        preload_all_textures()

        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.dragon_fireballs = arcade.SpriteList()

        self.cuphead = CupHead("assets/images/cuphead/Idle/cuphead_idle_0001.png", 1, 2)
        self.cuphead.center_x = 50
        self.cuphead.center_y = 100
        self.cuphead.change_x = 0
        self.cuphead.change_y = 0
        self.cuphead.alpha = 255
        self.pull = cycle((15, 0, -15))

        self.rock_lion = RockLion(1300, 200, -1)

        self.victory = False
        self.loose = False
        self.game_over_timer = 0
        self.game_over_delay = 120

        self.all_sprites.append(self.cuphead)
        self.enemies.append(self.rock_lion)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        self.all_sprites.draw()
        self.enemies.draw()
        self.bullets.draw()
        self.dragon_fireballs.draw()

        hp_text = arcade.Text(
            f"HP: {self.cuphead.hp}",
            10, SCREEN_HEIGHT - 30,
            arcade.color.RED, 24, bold=True,
        )
        hp_text.draw()

        cards_full = int(self.cuphead.ex_cards)
        cards_partial = self.cuphead.ex_cards - cards_full

        for i in range(self.cuphead.max_ex_cards):
            x = 10 + i * 45
            y = SCREEN_HEIGHT - 70

            rect = arcade.rect.XYWH(x + 20, y, 35, 40)
            arcade.draw_rect_outline(rect, arcade.color.GRAY, border_width=2)

            if i < cards_full:
                rect_filled = arcade.rect.XYWH(x + 20, y, 33, 38)
                arcade.draw_rect_filled(rect_filled, arcade.color.GOLD)
            elif i == cards_full and cards_partial > 0:
                fill_height = int(38 * cards_partial)
                rect_partial = arcade.rect.XYWH(
                    x + 20, y - 19 + fill_height // 2, 33, fill_height
                )
                arcade.draw_rect_filled(rect_partial, arcade.color.DARK_GOLDENROD)

        cards_text = arcade.Text(
            f"EX: {cards_full}/{self.cuphead.max_ex_cards}",
            10 + self.cuphead.max_ex_cards * 45 + 10, SCREEN_HEIGHT - 78,
            arcade.color.GOLD, 18, bold=True,
        )
        cards_text.draw()

        if self.victory:
            self._draw_victory_screen()

        if self.loose:
            self._draw_defeat_screen()

    def _draw_victory_screen(self):
        overlay = arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        arcade.draw_rect_filled(overlay, (0, 0, 0, 150))

        knockout_text = arcade.Text(
            "A KNOCKOUT!",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
            arcade.color.GOLD, 72, bold=True,
            anchor_x="center", anchor_y="center",
        )
        knockout_text.draw()

        subtitle = arcade.Text(
            "Defeat",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
            arcade.color.WHITE, 32,
            anchor_x="center", anchor_y="center",
        )
        subtitle.draw()

        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH // 2
        bar_y = SCREEN_HEIGHT // 2 - 60

        bar_bg = arcade.rect.XYWH(bar_x, bar_y, bar_width, bar_height)
        arcade.draw_rect_filled(bar_bg, arcade.color.DARK_RED)

        bar_fill = arcade.rect.XYWH(bar_x, bar_y, bar_width - 4, bar_height - 4)
        arcade.draw_rect_filled(bar_fill, arcade.color.RED)

        bar_label = arcade.Text(
            "BOSS HP: 0%",
            SCREEN_WIDTH // 2, bar_y,
            arcade.color.WHITE, 16, bold=True,
            anchor_x="center", anchor_y="center",
        )
        bar_label.draw()

        exit_text = arcade.Text(
            "Нажмите ESC чтобы выйти",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140,
            arcade.color.LIGHT_GRAY, 24,
            anchor_x="center", anchor_y="center",
        )
        exit_text.draw()

    def _draw_defeat_screen(self):
        overlay = arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        arcade.draw_rect_filled(overlay, (0, 0, 0, 180))

        died_text = arcade.Text(
            "YOU DIED!",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120,
            arcade.color.RED, 72, bold=True,
            anchor_x="center", anchor_y="center",
        )
        died_text.draw()

        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH // 2
        bar_y = SCREEN_HEIGHT // 2 - 40

        boss_hp_percent = max(0, self.rock_lion.hp / 1000)

        bar_bg = arcade.rect.XYWH(bar_x, bar_y, bar_width, bar_height)
        arcade.draw_rect_filled(bar_bg, arcade.color.DARK_RED)

        if boss_hp_percent > 0:
            fill_w = int((bar_width - 4) * boss_hp_percent)
            if fill_w > 0:
                bar_fill = arcade.rect.XYWH(
                    bar_x - (bar_width - 4) // 2 + fill_w // 2,
                    bar_y, fill_w, bar_height - 4
                )
                arcade.draw_rect_filled(bar_fill, arcade.color.RED)

        player_pos = 1.0 - boss_hp_percent
        marker_x = bar_x - bar_width // 2 + int(bar_width * player_pos)
        marker_text = arcade.Text(
            "☠", marker_x, bar_y + 25,
            arcade.color.WHITE, 20,
            anchor_x="center", anchor_y="center",
        )
        marker_text.draw()

        percent_text = arcade.Text(
            f"Boss HP: {int(boss_hp_percent * 100)}%",
            SCREEN_WIDTH // 2, bar_y,
            arcade.color.WHITE, 14, bold=True,
            anchor_x="center", anchor_y="center",
        )
        percent_text.draw()

        buttons_text = arcade.Text(
            "Нажмите R, чтобы начать заново  |  Нажмите ESC чтобы выйти",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120,
            arcade.color.LIGHT_GRAY, 24,
            anchor_x="center", anchor_y="center",
        )
        buttons_text.draw()

    def on_update(self, delta_time):
        if self.rock_lion.is_dead and self.rock_lion.death_animation_complete and not self.victory:
            self.game_over_timer += 1
            if self.game_over_timer >= self.game_over_delay:
                self.victory = True

        if self.cuphead.ghost_gone and not self.loose:
            self.loose = True

        if self.loose or self.victory:
            return

        if self.cuphead.hit and self.cuphead.just_took_damage:
            self.cuphead.keys_pressed = {
                "left": False, "right": False, "up": False, "down": False,
            }
            self.cuphead.change_x = 0
            self.cuphead.change_y = 0
            self.cuphead.moving = False
            self.cuphead.shooting = False

        if self.rock_lion.spawn_request is not None:
            spawn_type = self.rock_lion.spawn_request
            self.rock_lion.spawn_request = None

            if spawn_type == "satyr":
                for _ in range(3):
                    enemy = Satyr(random.randint(50, 1200), 100, random.choice((-1, 1)), shoot=None)
                    self.enemies.append(enemy)

            elif spawn_type == "mudman":
                for _ in range(3):
                    enemy = Mudman(random.randint(50, 1000), 100, random.choice((-1, 1)), shoot=None)
                    self.enemies.append(enemy)

            elif spawn_type == "dragon":
                for i in range(2):
                    dragon_type = random.randint(0, 2)
                    enemy = BabyDragon(random.randint(50, 1200), 100, random.choice((-1, 1)), dragon_type)
                    self.enemies.append(enemy)

        self.all_sprites.update(delta_time)
        self.bullets.update(delta_time)
        self.enemies.update(delta_time)
        self.dragon_fireballs.update(delta_time)
        self.cuphead.update(delta_time)
        self.rock_lion.update(delta_time)

        if self.cuphead.death:
            return

        for bullet in self.cuphead.bullets_to_add:
            self.bullets.append(bullet)
        self.cuphead.bullets_to_add.clear()

        for dragon in self.enemies:
            if isinstance(dragon, BabyDragon):
                fireballs = dragon.shoot_at_player(self.cuphead)
                if fireballs:
                    for fireball in fireballs:
                        self.dragon_fireballs.append(fireball)

        check_enemies = arcade.check_for_collision_with_list(self.cuphead, self.enemies)
        for c in check_enemies:
            if c.can_damage:
                self.cuphead.take_damage()

        check_fireballs = arcade.check_for_collision_with_list(self.cuphead, self.dragon_fireballs)
        for fireball in check_fireballs:
            if self.cuphead.parry and fireball.can_be_parried:
                self.cuphead.parry_successful()
                fireball.remove_from_sprite_lists()
            elif not self.cuphead.invincible and not self.cuphead.parry:
                self.cuphead.take_damage()
                fireball.remove_from_sprite_lists()

        if (
            not self.cuphead.dashing
            and self.cuphead.can_move
            and not self.cuphead.dashing_back
            and not self.cuphead.flexing
            and not self.cuphead.ex_straight
            and not self.cuphead.hit
            and not self.cuphead.parry
            and not self.cuphead.on_ground
            and not self.cuphead.force_stop_movement
        ):
            self.cuphead.change_y -= 0.5

        if self.cuphead.has_jumped and not self.cuphead.on_ground:
            self.cuphead.air_parry_window += 1
            if self.cuphead.air_parry_window <= 30:
                self.cuphead.in_air_parry_window = True
            else:
                self.cuphead.in_air_parry_window = False
        else:
            self.cuphead.has_jumped = False
            self.cuphead.in_air_parry_window = False
            self.cuphead.air_parry_window = 0

        self.cuphead.center_y += self.cuphead.change_y
        self.cuphead.center_x += self.cuphead.change_x

        if self.cuphead.left < 0:
            self.cuphead.left = 0
            if self.cuphead.dashing or self.cuphead.dashing_back:
                self.cuphead.dashing = False
                self.cuphead.dashing_back = False
                self.cuphead.change_x = 0
        if self.cuphead.right > SCREEN_WIDTH:
            self.cuphead.right = SCREEN_WIDTH
            if self.cuphead.dashing or self.cuphead.dashing_back:
                self.cuphead.dashing = False
                self.cuphead.dashing_back = False
                self.cuphead.change_x = 0

        ground_level = 50
        if self.cuphead.bottom <= ground_level:
            self.cuphead.bottom = ground_level
            self.cuphead.on_ground = True
            self.cuphead.change_y = 0
            self.cuphead.count_dash = 1
        else:
            self.cuphead.on_ground = False

        if not self.cuphead.can_shoot:
            self.cuphead.shooting = False
            return

        if self.cuphead.dashing or self.cuphead.dashing_back:
            self.cuphead.shooting = False
            return

        if self.cuphead.shooting and self.cuphead.shoot_cooldown <= 0:
            direction_x = 0
            direction_y = 0
            bullet_angle = 0
            flag = self.cuphead.direction == "right"
            pull_move = self.cuphead.center_x + 50 * (-1, 1)[flag]
            pull_up = self.cuphead.center_y + next(self.pull)

            if self.cuphead.duck_shooting:
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0
                pull_move += 50 * (-1, 1)[flag]
            elif not self.cuphead.on_ground and self.cuphead.keys_pressed["up"]:
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0.707
                pull_up += 50
                bullet_angle = 45 if self.cuphead.direction == "right" else -45
            elif self.cuphead.shoot_diagonal_up_running or self.cuphead.shoot_diagonal_up_running_left:
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0.707
                pull_up += 50
                bullet_angle = 45 if self.cuphead.direction == "right" else -45
            elif self.cuphead.shooting_up and self.cuphead.on_ground:
                direction_x = 0
                direction_y = 1
                pull_move -= 30 * (-1, 1)[flag]
                pull_up += 100
                bullet_angle = 90
            elif self.cuphead.shooting_down:
                direction_x = 0
                direction_y = -1
                pull_up -= 50
                bullet_angle = -90
            elif self.cuphead.shooting_straight:
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0
            elif self.cuphead.shoot_straight_running:
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0
            elif not self.cuphead.on_ground:
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0

            bv = CupHead._bullet_variants
            if bullet_angle == 90:
                shoot = bv["peashooter_up"]
            elif bullet_angle == -90:
                shoot = bv["peashooter_down"]
            elif bullet_angle == 45:
                shoot = bv["peashooter_diag_right"]
            elif bullet_angle == -45:
                shoot = bv["peashooter_diag_left"]
            elif not flag:
                shoot = bv["peashooter_left"]
            else:
                shoot = bv["peashooter_right"]

            bullet = Bullet(pull_move, pull_up, direction_x, direction_y, shoot, bullet_angle)
            self.bullets.append(bullet)

            self.cuphead.shoot_cooldown = 6

        if self.cuphead.shoot_cooldown > 0:
            self.cuphead.shoot_cooldown -= 1

        if not self.cuphead.shooting or not self.cuphead.moving:
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False

        for enemy in self.enemies:
            hit_list = arcade.check_for_collision_with_list(enemy, self.bullets)
            for bullet in hit_list:
                if enemy in self.enemies and enemy.can_damage:
                    enemy.take_damage(bullet.damage)
                    self.cuphead.gain_card_on_hit()
                    if bullet in self.bullets:
                        bullet.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R and (self.victory or self.loose):
            self.setup()
            return

        if self.cuphead.death or self.cuphead.disable_input:
            return

        if self.cuphead.hit and self.cuphead.just_took_damage:
            return

        if (
            self.loose
            or self.victory
            or self.cuphead.flexing
            or self.cuphead.ex_straight
            or self.cuphead.hit
        ):
            return

        if key == arcade.key.LEFT:
            self.cuphead.keys_pressed["left"] = True
            self.cuphead.change_direction("left")

            if (
                not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.duck
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and not self.cuphead.parry
                and not self.cuphead.force_stop_movement
            ):
                self.cuphead.change_x = -SPEED
                self.cuphead.moving = True
            elif self.cuphead.duck:
                self.cuphead.moving = False
                self.cuphead.change_x = 0

        elif key == arcade.key.RIGHT:
            self.cuphead.keys_pressed["right"] = True
            self.cuphead.change_direction("right")

            if (
                not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.duck
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and not self.cuphead.parry
                and not self.cuphead.force_stop_movement
            ):
                self.cuphead.change_x = SPEED
                self.cuphead.moving = True
            elif self.cuphead.duck:
                self.cuphead.moving = False
                self.cuphead.change_x = 0

        elif key == arcade.key.UP:
            self.cuphead.keys_pressed["up"] = True
            if (
                self.cuphead.shooting
                and not self.cuphead.moving
                and not self.cuphead.duck
                and self.cuphead.on_ground
                and self.cuphead.can_shoot
            ):
                self.cuphead.shooting_up = True
                self.cuphead.shooting_straight = False

        elif key == arcade.key.DOWN:
            self.cuphead.keys_pressed["down"] = True
            self.cuphead.duck = True
            self.cuphead.change_x = 0
            self.cuphead.moving = False
            if self.cuphead.shooting:
                self.cuphead.shooting_up = False
                self.cuphead.shooting_down = False

        elif (
            key == arcade.key.SPACE
            and not self.cuphead.flexing
            and not self.cuphead.ex_straight
            and not self.cuphead.hit
        ):
            if self.cuphead.on_ground:
                self.cuphead.change_y = 10
                self.cuphead.on_ground = False
                self.cuphead.has_jumped = True
                self.cuphead.air_parry_window = 0
            elif not self.cuphead.on_ground and self.cuphead.has_jumped:
                self.cuphead.process_parry(is_air_parry=True)

        if (
            key == arcade.key.X
            and not self.cuphead.dashing
            and not self.cuphead.dashing_back
            and not self.cuphead.flexing
            and not self.cuphead.ex_straight
            and not self.cuphead.parry
            and self.cuphead.can_dash
        ):
            if self.cuphead.count_dash:
                self.cuphead.start_dash()
                if not self.cuphead.on_ground:
                    self.cuphead.count_dash -= 1

        elif (
            key == arcade.key.F
            and not self.cuphead.flexing
            and not self.cuphead.ex_straight
            and self.cuphead.on_ground
            and not self.cuphead.parry
        ):
            self.cuphead.flexing = True
            self.cuphead.change_x = 0
            self.cuphead.change_y = 0
            self.cuphead.moving = False
            self.cuphead.can_move = False
            self.cuphead.shooting = False
            self.cuphead.shooting_straight = False
            self.cuphead.shooting_up = False
            self.cuphead.shooting_down = False
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False
            self.cuphead.duck_shooting = False
            self.cuphead.shooting_diagonal_up = False

        elif (
            key == arcade.key.V
            and not self.cuphead.ex_straight
            and not self.cuphead.flexing
            and not self.cuphead.parry
            and self.cuphead.ex_cards >= 1
        ):
            self.cuphead.ex_straight = True
            self.cuphead.ex_cards -= 1
            self.cuphead.change_x = 0
            self.cuphead.change_y = 0
            self.cuphead.moving = False
            self.cuphead.can_move = False
            self.cuphead.shooting = False
            self.cuphead.shooting_straight = False
            self.cuphead.shooting_up = False
            self.cuphead.shooting_down = False
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False
            self.cuphead.duck_shooting = False
            self.cuphead.shooting_diagonal_up = False

        if (
            key == arcade.key.Z
            and not self.cuphead.flexing
            and not self.cuphead.ex_straight
            and not self.cuphead.parry
        ):
            if not self.cuphead.can_shoot:
                return
            if self.cuphead.dashing or self.cuphead.dashing_back:
                return

            self.cuphead.shooting = True
            if (
                not self.cuphead.moving
                and not self.cuphead.duck
                and self.cuphead.on_ground
            ):
                self.cuphead.shooting_straight = True

    def on_key_release(self, key, modifiers):
        if self.cuphead.death or self.cuphead.disable_input:
            return

        if self.cuphead.hit and self.cuphead.just_took_damage:
            return

        if (
            self.loose
            or self.victory
            or self.cuphead.flexing
            or self.cuphead.ex_straight
            or self.cuphead.hit
        ):
            return

        if key == arcade.key.LEFT:
            self.cuphead.keys_pressed["left"] = False
            if (
                not self.cuphead.keys_pressed["right"]
                and not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.parry
                and not self.cuphead.force_stop_movement
            ):
                self.cuphead.change_x = 0
                self.cuphead.moving = False

        elif key == arcade.key.RIGHT:
            self.cuphead.keys_pressed["right"] = False
            if (
                not self.cuphead.keys_pressed["left"]
                and not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.parry
                and not self.cuphead.force_stop_movement
            ):
                self.cuphead.change_x = 0
                self.cuphead.moving = False

        elif key == arcade.key.UP:
            self.cuphead.keys_pressed["up"] = False
            if (
                self.cuphead.shooting
                and not self.cuphead.moving
                and not self.cuphead.duck
                and self.cuphead.on_ground
                and self.cuphead.can_shoot
            ):
                self.cuphead.shooting_up = False
                self.cuphead.shooting_straight = True

        elif key == arcade.key.DOWN:
            self.cuphead.keys_pressed["down"] = False
            self.cuphead.duck = False
            self.cuphead.duck_shooting = False

            if (
                not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and not self.cuphead.parry
                and not self.cuphead.force_stop_movement
            ):
                any_key_pressed = self.cuphead.keys_pressed["left"] or self.cuphead.keys_pressed["right"]
                if any_key_pressed:
                    if self.cuphead.keys_pressed["left"]:
                        self.cuphead.change_x = -SPEED
                        self.cuphead.moving = True
                        self.cuphead.change_direction("left")
                    elif self.cuphead.keys_pressed["right"]:
                        self.cuphead.change_x = SPEED
                        self.cuphead.moving = True
                        self.cuphead.change_direction("right")
                else:
                    self.cuphead.change_x = 0
                    self.cuphead.moving = False

        if (
            not self.cuphead.dashing
            and not self.cuphead.dashing_back
            and not self.cuphead.duck
            and not self.cuphead.flexing
            and not self.cuphead.ex_straight
            and not self.cuphead.parry
            and not self.cuphead.force_stop_movement
        ):
            if key == arcade.key.LEFT and self.cuphead.change_x < 0:
                if self.cuphead.keys_pressed["right"]:
                    self.cuphead.change_x = SPEED
                    self.cuphead.moving = True
                    self.cuphead.change_direction("right")
                else:
                    self.cuphead.change_x = 0
                    self.cuphead.moving = False

            elif key == arcade.key.RIGHT and self.cuphead.change_x > 0:
                if self.cuphead.keys_pressed["left"]:
                    self.cuphead.change_x = -SPEED
                    self.cuphead.moving = True
                    self.cuphead.change_direction("left")
                else:
                    self.cuphead.change_x = 0
                    self.cuphead.moving = False

        if key == arcade.key.Z:
            if not self.cuphead.can_shoot:
                return

            self.cuphead.shooting = False
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False
            self.cuphead.shooting_straight = False
            self.cuphead.shooting_up = False
            self.cuphead.shooting_down = False
            self.cuphead.duck_shooting = False
            self.cuphead.shooting_diagonal_up = False


def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()