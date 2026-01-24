import arcade
import random
from itertools import cycle
import math

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Овощебанда"
SPEED = 5
WATER_HEIGHT = SCREEN_HEIGHT // 3
BULLET_SPEED = 40


class Bullet(arcade.Sprite):
    def __init__(self, x, y, direction_x, direction_y, shoot, angle=0):
        super().__init__(shoot, scale=0.7)
        self.center_x = x
        self.center_y = y
        self.change_x = direction_x * BULLET_SPEED
        self.change_y = direction_y * BULLET_SPEED
        self.lifetime = 120
        self.angle = angle  # Угол поворота для диагональных выстрелов
        if angle != 0:
            self.angle = angle  # Устанавливаем угол поворота спрайта

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()


class CupHead(arcade.Sprite):
    def __init__(self, filename, scale, speed):
        super().__init__(filename, scale)

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
            "shoot_diagonal_down": {"right": [], "left": []},
            "shoot_diagonal_up": {"right": [], "left": []},
            "shoot_straight_running": {"right": [], "left": []},
            "shoot_diagonal_up_running": {"right": [], "left": []},
            "shoot_diagonal_up_running_left": {
                "right": [],
                "left": [],
            },
            'duck_shoot': {"right": [], "left": []},
        }

        for i in range(1, 6):
            path = f'images/Idle/cuphead_idle_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["idle"]["right"].append(texture)

        for texture in self.textures_dict["idle"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["idle"]["left"].append(flipped_texture)

        self.texture = self.textures_dict["idle"]["right"][0]

        for i in range(1, 17):
            path = f'images/Run/Normal/cuphead_run_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["run"]["right"].append(texture)

        for texture in self.textures_dict["run"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["run"]["left"].append(flipped_texture)

        for i in range(1, 9):
            path = f"images/Jump/Cuphead/cuphead_jump_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["jump"]["right"].append(texture)

        for texture in self.textures_dict["jump"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["jump"]["left"].append(flipped_texture)

        for i in range(1, 9):
            if i == 3:
                continue
            path = f"images/Duck/idle/cuphead_duck_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["duck"]["right"].append(texture)

        for texture in self.textures_dict["duck"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["duck"]["left"].append(flipped_texture)

        for i in range(1, 6):
            path = f"images/Duck/idle/cuphead_duck_idle_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["duck_idle"]["right"].append(texture)

        for texture in self.textures_dict["duck_idle"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["duck_idle"]["left"].append(flipped_texture)

        for i in range(-1, 6):
            path = f'images/Dash/Ground/cuphead_dash_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["dash"]["right"].append(texture)

        for texture in self.textures_dict["dash"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["dash"]["left"].append(flipped_texture)

        for i in range(4, -2, -1):
            path = f'images/Dash/Ground/cuphead_dash_{"0" * (4 - len(str(i)))}{i}.png'
            texture = arcade.load_texture(path)
            self.textures_dict["dash_back"]["right"].append(texture)

        for texture in self.textures_dict["dash_back"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["dash_back"]["left"].append(flipped_texture)

        for i in range(1, 44):
            path = (
                f'images/Intros/Flex/cuphead_intro_b_{"0" * (4 - len(str(i)))}{i}.png'
            )
            texture = arcade.load_texture(path)
            self.textures_dict["flex"]["right"].append(texture)

        for i in range(1, 4):
            path = f"images/Shoot/Straight/cuphead_shoot_straight_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_straight"]["right"].append(texture)

        for texture in self.textures_dict["shoot_straight"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["shoot_straight"]["left"].append(flipped_texture)

        for i in range(1, 4):
            path = f"images/Shoot/Up/cuphead_shoot_up_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_up"]["right"].append(texture)

        for texture in self.textures_dict["shoot_up"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["shoot_up"]["left"].append(flipped_texture)

        for i in range(1, 4):
            path = f"images/Shoot/Down/cuphead_shoot_down_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_down"]["right"].append(texture)

        for texture in self.textures_dict["shoot_down"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["shoot_down"]["left"].append(flipped_texture)

        for i in range(1, 4):
            path = f"images/Shoot/Diagonal Up/cuphead_shoot_diagonal_up_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_diagonal_up"]["right"].append(texture)

        for texture in self.textures_dict["shoot_diagonal_up"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["shoot_diagonal_up"]["left"].append(flipped_texture)

        for i in range(1, 17):
            path = f"images/Run/Shooting/Straight/cuphead_run_shoot_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_straight_running"]["right"].append(texture)

        for texture in self.textures_dict["shoot_straight_running"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["shoot_straight_running"]["left"].append(flipped_texture)

        for i in range(1, 17):
            path = f"images/Run/Shooting/Diagonal Up/cuphead_run_shoot_diagonal_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_diagonal_up_running"]["right"].append(texture)

        for texture in self.textures_dict["shoot_diagonal_up_running"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["shoot_diagonal_up_running"]["left"].append(
                flipped_texture
            )

        for i in range(1, 17):
            path = f"images/Run/Shooting/Diagonal Up/cuphead_run_shoot_diagonal_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["shoot_diagonal_up_running_left"]["left"].append(texture)

        for texture in self.textures_dict["shoot_diagonal_up_running_left"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["shoot_diagonal_up_running_left"]["right"].append(
                flipped_texture
            )

        for i in range(1, 4):
            path = f"images/Duck/Shoot/cuphead_duck_shoot_000{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["duck_shoot"]["right"].append(texture)

        for texture in self.textures_dict["duck_shoot"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["duck_shoot"]["left"].append(flipped_texture)

        self.state = "idle"
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
        self.flexing = False
        self.can_move = True
        self.dashing_back = False

        # Переменные для дэша
        self.dash_start_moving = False
        self.dash_start_direction = "right"
        self.key = False
        self.count_dash = 1

        self.keys_pressed = {"left": False, "right": False, "up": False, "down": False}

        # стрельба
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
        self.shoot_diagonal_up_running_left = (
            False
        )
        self.duck_shooting = False

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
        }

    def update(self, delta_time):
        super().update()

        if self.key:
            self.center_x = self.center_x + (50 * (-1, 1)[self.direction == "right"])
            self.key = False

        if self.flexing:
            new_state = "flex"

        elif self.dashing_back:
            new_state = "dash_back"

        elif not self.on_ground and not self.dashing:
            # В прыжке оставляем обычную анимацию прыжка
            new_state = "jump"

        elif self.dashing:
            new_state = "dash"

        # Проверяем стрельбу в приседе
        elif self.shooting and self.duck:
            new_state = "duck_shoot"
            self.duck_shooting = True

        # Проверяем стрельбу во время бега
        elif self.shooting and self.moving:
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

        # Проверяем стрельбу стоя на месте
        elif self.shooting and not self.moving and not self.duck and self.on_ground:
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
                if (
                        self.current_frame
                        >= len(self.textures_dict["duck"][self.direction]) - 1
                ):
                    new_state = "duck_idle"
                    self.current_frame = 0
                    self.duck_idle = True
                else:
                    new_state = "duck"
            elif self.state == "duck" and self.duck_direction == -1:
                new_state = "duck"
                self.duck_direction = 1
                self.current_frame = (
                        len(self.textures_dict["duck"][self.direction])
                        - 1
                        - self.current_frame
                )
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
                self.current_frame = (
                        len(self.textures_dict["duck"][self.direction])
                        - 1
                        - self.current_frame
                )
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

        elif self.moving and self.change_x != 0 and not self.duck:
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
                self.update_animation_frame()
                self.update_texture()

    def update_animation_frame(self):
        if self.state == "flex":
            textures_list = self.textures_dict["flex"]["right"]
            if textures_list:
                self.can_move = False
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    self.can_move = True
                    self.current_frame = len(textures_list) - 1
                    self.flexing = False
                    # ВОССТАНАВЛИВАЕМ ГРАВИТАЦИЮ ПОСЛЕ FLEX
                    self.change_y = 0  # Сбрасываем вертикальную скорость
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
            textures_list = self.textures_dict["shoot_diagonal_up_running"][
                self.direction
            ]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

        if self.state == "shoot_diagonal_up_running_left":
            textures_list = self.textures_dict["shoot_diagonal_up_running_left"][
                self.direction
            ]
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
                    self.dash_direction_multiplier = (
                        1 if self.direction == "right" else -1
                    )
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
                        self.dash_direction_multiplier = (
                            1 if self.direction == "right" else -1
                        )
                        self.change_x = 7 * self.dash_direction_multiplier
                    self.current_frame += 1
                else:
                    self.dashing_back = False

                    if self.duck:
                        self.change_x = 0
                        self.moving = False
                    else:
                        any_key_pressed = (
                                self.keys_pressed["left"] or self.keys_pressed["right"]
                        )

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
        """Начинаем дэш, если это возможно"""
        if not self.dashing and not self.dashing_back:
            self.dashing = True
            self.current_frame = 0
            self.animation_speed_counter = 0


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background = arcade.load_texture("images/backgrounds/background.jpg")

    def setup(self):
        self.all_sprites = arcade.SpriteList()
        self.floes = arcade.SpriteList()
        self.cuphead = CupHead("images/Idle/cuphead_idle_0001.png", 0.8, 2)
        self.cuphead.center_x = 50
        self.cuphead.center_y = 100
        self.cuphead.change_x = 0
        self.cuphead.change_y = 0
        self.pull = cycle((15, 0, -15))

        self.victory = False
        self.loose = False

        self.all_sprites.append(self.cuphead)

    def on_draw(self):
        arcade.draw_texture_rect(
            self.background,
            arcade.XYWH(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT
            ),
        )

        self.all_sprites.draw()
        if self.victory:
            self.pp.draw()

    def on_update(self, delta_time):
        if self.loose or self.victory:
            return
        self.all_sprites.update(delta_time)

        self.cuphead.update(delta_time)

        # Применяем гравитацию только если не в дэше
        if (
                not self.cuphead.dashing
                and self.cuphead.can_move
                and not self.cuphead.dashing_back
                and not self.cuphead.flexing  # Не применяем гравитацию во время flex
        ):
            self.cuphead.change_y -= 0.5

        self.cuphead.center_y += self.cuphead.change_y
        self.cuphead.center_x += self.cuphead.change_x

        # Ограничения по краям экрана
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

        # Проверка земли
        ground_level = 50
        if self.cuphead.bottom <= ground_level:
            self.cuphead.bottom = ground_level
            self.cuphead.on_ground = True
            self.cuphead.change_y = 0
            self.cuphead.count_dash = 1
        else:
            self.cuphead.on_ground = False

        if self.cuphead.shooting and self.cuphead.shoot_cooldown <= 0:
            # Определяем направление стрельбы
            direction_x = 0
            direction_y = 0
            bullet_angle = 0
            flag = self.cuphead.direction == "right"
            pull_move = self.cuphead.center_x + 50 * (-1, 1)[flag]
            pull_up = self.cuphead.center_y + next(self.pull)

            # Определяем тип стрельбы и корректируем параметры
            if self.cuphead.duck_shooting:
                # Стрельба в приседе
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0
                pull_move += 50 * (-1, 1)[flag]
            elif not self.cuphead.on_ground and self.cuphead.keys_pressed["up"]:
                # Стрельба вверх в прыжке (диагональная)
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0.707  # 45 градусов
                pull_up += 50
                bullet_angle = 45 if self.cuphead.direction == "right" else -45
            elif (
                    self.cuphead.shoot_diagonal_up_running
                    or self.cuphead.shoot_diagonal_up_running_left
            ):
                # Диагональный выстрел при беге
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0.707
                pull_up += 50
                # Угол для пули: 45 градусов вверх
                bullet_angle = 45 if self.cuphead.direction == "right" else -45
            elif self.cuphead.shooting_up and self.cuphead.on_ground:
                # Стрельба вверх стоя на земле
                direction_x = 0
                direction_y = 1
                pull_move -= 30 * (-1, 1)[flag]
                pull_up += 100
                bullet_angle = 90  # Поворот на 90 градусов для стрельбы вверх
            elif self.cuphead.shooting_down:
                # Стрельба вниз стоя
                direction_x = 0
                direction_y = -1
                pull_up -= 50
                bullet_angle = -90  # Поворот на -90 градусов для стрельбы вниз
            elif self.cuphead.shooting_straight:
                # Стрельба прямо стоя
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0
            elif self.cuphead.shoot_straight_running:
                # Стрельба прямо при беге
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0
            elif not self.cuphead.on_ground:
                # Стрельба в прыжке (обычная, горизонтальная)
                direction_x = 1 if self.cuphead.direction == "right" else -1
                direction_y = 0
                bullet_angle = 0

            # Создать пулю
            shoot = arcade.load_texture("images/shoots/peashooter.png")

            # Поворачиваем текстуру в зависимости от угла
            if bullet_angle == 90:  # Вверх
                shoot = shoot.rotate_180()
            elif bullet_angle == -90:  # Вниз
                shoot = shoot
            elif bullet_angle == 45:  # Диагональ вправо-вверх
                shoot = shoot.rotate_90(3)
            elif bullet_angle == -45:  # Диагональ влево-вверх
                shoot = shoot.rotate_90(3)

            # Для стрельбы влево - зеркалим
            if not flag and bullet_angle == 0:
                shoot = shoot.flip_left_right()

            bullet = Bullet(
                pull_move, pull_up, direction_x, direction_y, shoot, bullet_angle
            )
            self.all_sprites.append(bullet)

            # кулдаун
            self.cuphead.shoot_cooldown = 6

        if self.cuphead.shoot_cooldown > 0:
            self.cuphead.shoot_cooldown -= 1

        # Сбрасываем состояния стрельбы при беге, если не стреляем или не двигаемся
        if not self.cuphead.shooting or not self.cuphead.moving:
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False

    def on_key_press(self, key, modifiers):
        if self.loose or self.victory or self.cuphead.flexing:
            return

        if key == arcade.key.LEFT:
            self.cuphead.keys_pressed["left"] = True
            self.cuphead.change_direction("left")

            if (
                    not self.cuphead.dashing
                    and not self.cuphead.dashing_back
                    and not self.cuphead.duck
                    and not self.cuphead.flexing
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
            ):
                self.cuphead.change_x = SPEED
                self.cuphead.moving = True
            elif self.cuphead.duck:
                self.cuphead.moving = False
                self.cuphead.change_x = 0

        elif key == arcade.key.UP:
            self.cuphead.keys_pressed["up"] = True
            # При нажатии UP меняем состояние стрельбы если уже стреляем и на земле
            if self.cuphead.shooting and not self.cuphead.moving and not self.cuphead.duck and self.cuphead.on_ground:
                self.cuphead.shooting_up = True
                self.cuphead.shooting_straight = False

        elif key == arcade.key.DOWN:
            self.cuphead.keys_pressed["down"] = True
            self.cuphead.duck = True
            self.cuphead.change_x = 0
            self.cuphead.moving = False
            # При приседе сбрасываем состояния стрельбы вверх/вниз
            if self.cuphead.shooting:
                self.cuphead.shooting_up = False
                self.cuphead.shooting_down = False

        elif (
                key == arcade.key.SPACE
                and self.cuphead.on_ground
                and not self.cuphead.flexing
        ):
            self.cuphead.change_y = 10
            self.cuphead.on_ground = False

        # ДЭШ
        if (
                key == arcade.key.X
                and not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.flexing
        ):
            if self.cuphead.count_dash:
                self.cuphead.start_dash()
                if not self.cuphead.on_ground:
                    self.cuphead.count_dash -= 1

        # FLEX
        elif key == arcade.key.F and not self.cuphead.flexing:
            self.cuphead.flexing = True
            self.cuphead.change_x = 0
            self.cuphead.change_y = 0  # Сбрасываем вертикальную скорость
            self.cuphead.moving = False
            self.cuphead.can_move = False
            # Останавливаем стрельбу при начале flex
            self.cuphead.shooting = False
            self.cuphead.shooting_straight = False
            self.cuphead.shooting_up = False
            self.cuphead.shooting_down = False
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False
            self.cuphead.duck_shooting = False
            self.cuphead.shooting_diagonal_up = False

        if key == arcade.key.Z and not self.cuphead.flexing:
            self.cuphead.shooting = True
            # При начале стрельбы устанавливаем состояние по умолчанию
            if not self.cuphead.moving and not self.cuphead.duck and self.cuphead.on_ground:
                self.cuphead.shooting_straight = True

    def on_key_release(self, key, modifiers):
        if self.loose or self.victory:
            return

        if key == arcade.key.LEFT:
            self.cuphead.keys_pressed["left"] = False

        elif key == arcade.key.RIGHT:
            self.cuphead.keys_pressed["right"] = False

        elif key == arcade.key.UP:
            self.cuphead.keys_pressed["up"] = False
            # При отпускании UP меняем состояние стрельбы только если на земле
            if self.cuphead.shooting and not self.cuphead.moving and not self.cuphead.duck and self.cuphead.on_ground:
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
            ):
                any_key_pressed = (
                        self.cuphead.keys_pressed["left"]
                        or self.cuphead.keys_pressed["right"]
                )
                if any_key_pressed:
                    if self.cuphead.keys_pressed["left"]:
                        self.cuphead.change_x = -SPEED
                        self.cuphead.moving = True
                        self.cuphead.change_direction("left")
                    elif self.cuphead.keys_pressed["right"]:
                        self.cuphead.change_x = SPEED
                        self.cuphead.moving = True
                        self.cuphead.change_direction("right")

        if (
                not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.duck
                and not self.cuphead.flexing
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
            self.cuphead.shooting = False
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False
            self.cuphead.shooting_straight = False
            self.cuphead.shooting_up = False
            self.cuphead.shooting_down = False
            self.cuphead.duck_shooting = False
            self.cuphead.shooting_diagonal_up = False


def setup_game(width=1500, height=870, title="CUPHEAD"):
    game = GameWindow(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()