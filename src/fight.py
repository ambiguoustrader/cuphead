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
EX_BULLET_SPEED = 30  # Скорость для супер-пуль


class Satyr(arcade.Sprite):
    def __init__(self, x, y, direction_x):
        # Используем базовую текстуру
        texture = arcade.load_texture("images/Satyr/Jump/lv3-2_satyr_jump_0001.png")
        super().__init__(texture)

        self.center_x = x
        self.center_y = y
        self.change_x = direction_x * 2  # Скорость движения
        self.change_y = 0
        self.hp = 100

        # Направление и состояния
        self.direction = "right" if direction_x > 0 else "left"
        self.start = True  # Флаг начальной анимации прыжка
        self.on_ground = False
        self.state = "jump"
        self.current_frame = 0
        self.animation_speed_counter = 0
        self.animation_speed = 4  # Скорость анимации
        self.start_jump_complete = False  # Флаг завершения начального прыжка
        self.jump_phase = "up"  # Фаза прыжка: "up" или "down"
        self.jump_frames = 0  # Счетчик кадров прыжка

        # Загрузка текстур
        self.textures_dict = {
            "jump": {"right": [], "left": []},
            "run": {"right": [], "left": []},
            "turn": {"right": [], "left": []},
        }

        # Загрузка анимации прыжка
        for i in range(1, 20):
            path = f"images/Satyr/Jump/lv3-2_satyr_jump_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["jump"]["left"].append(texture)

        for texture in self.textures_dict["jump"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["jump"]["right"].append(flipped_texture)

        # Загрузка анимации бега/пропуска
        for i in range(1, 25):
            path = f"images/Satyr/Skip/lv3-2_satyr_skip_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["run"]["left"].append(texture)

        for texture in self.textures_dict["run"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["run"]["right"].append(flipped_texture)

        # Загрузка анимации поворота
        for i in range(1, 5):
            path = f"images/Satyr/Turn/lv3-2_satyr_turn_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["turn"]["left"].append(texture)

        for texture in self.textures_dict["turn"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["turn"]["right"].append(flipped_texture)

        # Устанавливаем начальную текстуру
        self.update_texture()

    def update(self, delta_time):
        """Обновление состояния сатира"""
        super().update()

        # Обновление анимации
        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.animation_speed:
            self.animation_speed_counter = 0
            self.update_animation()
            self.update_texture()

        # Если в начале игры и еще не завершил начальный прыжок
        if self.start and not self.start_jump_complete:
            self.jump_frames += 1

            # Кадры 0-9: прыжок
            if self.jump_frames <= 20:  # Первые 20 обновлений (примерно 5 кадров анимации)
                # Поднимаемся
                self.change_y = 8
            elif self.jump_frames <= 40:  # Следующие 20 обновлений (кадры 5-10)
                # Падаем
                self.change_y = -6
            else:
                # Завершаем прыжок, включаем обычную гравитацию
                self.start_jump_complete = True
                self.change_y = 0
        else:
            # После начального прыжка применяем обычную гравитацию
            if not self.on_ground:
                self.change_y -= 0.5

        self.center_y += self.change_y
        self.center_x += self.change_x

        # Проверка земли
        ground_level = 50
        if self.bottom <= ground_level:
            self.bottom = ground_level
            self.on_ground = True
            self.change_y = 0

            # После приземления заканчиваем начальную анимацию
            if self.start and self.start_jump_complete:
                # Ждем несколько кадров после приземления для завершения анимации
                if self.current_frame >= 15:  # Когда достигли последних кадров прыжка
                    self.start = False
                    self.state = "run"
                    self.current_frame = 0
                    self.animation_speed_counter = 0
        else:
            self.on_ground = False

        # Проверка границ экрана
        if self.left < 0:
            self.left = 0
            self.change_x *= -1
            self.direction = "right" if self.change_x > 0 else "left"
            self.current_frame = 0  # Сброс кадра при изменении направления

        elif self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
            self.change_x *= -1
            self.direction = "right" if self.change_x > 0 else "left"
            self.current_frame = 0  # Сброс кадра при изменении направления

    def update_animation(self):
        """Обновление анимации"""
        if self.start:
            # Проигрываем анимацию прыжка
            textures_list = self.textures_dict["jump"][self.direction]
            if textures_list:
                # Плавное проигрывание всей анимации прыжка
                if not self.start_jump_complete:
                    # Во время прыжка проигрываем все кадры
                    if self.current_frame < len(textures_list) - 1:
                        self.current_frame += 1
                else:
                    # После завершения прыжка можем ускорить анимацию приземления
                    if self.current_frame < len(textures_list) - 1:
                        self.current_frame += 1
        else:
            # После завершения начального прыжка переходим к анимации бега
            textures_list = self.textures_dict["run"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)

    def update_texture(self):
        """Обновление текущей текстуры спрайта"""
        if self.start:
            textures_list = self.textures_dict["jump"][self.direction]
        else:
            textures_list = self.textures_dict["run"][self.direction]

        if textures_list and 0 <= self.current_frame < len(textures_list):
            self.texture = textures_list[self.current_frame]

    def take_damage(self, damage):
        """Принять урон"""
        self.hp -= damage
        if self.hp <= 0:
            self.remove_from_sprite_lists()


class Bullet(arcade.Sprite):
    def __init__(self, x, y, direction_x, direction_y, shoot, angle=0, is_ex=False):
        super().__init__(shoot, scale=0.7)
        self.center_x = x
        self.center_y = y
        speed = EX_BULLET_SPEED if is_ex else BULLET_SPEED
        self.change_x = direction_x * speed
        self.change_y = direction_y * speed
        self.lifetime = 120
        self.angle = angle  # Угол поворота для диагональных выстрелов
        if angle != 0:
            self.angle = angle  # Устанавливаем угол поворота спрайта
        self.is_ex = is_ex  # Флаг супер-пули

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
            "duck_shoot": {"right": [], "left": []},
            "ex_straight": {"right": [], "left": []},
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

        # Загрузка анимации супер-атаки
        for i in range(1, 16):
            path = f"images/Special Attck/Straight/Ground/cuphead_ex_straight_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["ex_straight"]["right"].append(texture)

        for texture in self.textures_dict["ex_straight"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["ex_straight"]["left"].append(flipped_texture)

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
        self.ex_straight = False  # Флаг супер-атаки
        self.can_move = True
        self.dashing_back = False

        # Список для хранения созданных пуль
        self.bullets_to_add = []

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
        self.shoot_diagonal_up_running_left = False
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
            "ex_straight": 6,
        }

    def update(self, delta_time):
        super().update()

        if self.key:
            self.center_x = self.center_x + (50 * (-1, 1)[self.direction == "right"])
            self.key = False

        if self.ex_straight:
            new_state = "ex_straight"
        elif self.flexing:
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
        if self.state == "ex_straight":
            textures_list = self.textures_dict["ex_straight"][self.direction]
            if textures_list:
                self.can_move = False
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                    # Создаем пулю на определенных кадрах анимации
                    if self.current_frame == 8:
                        self.create_ex_bullet()
                else:
                    self.can_move = True
                    self.current_frame = len(textures_list) - 1
                    self.ex_straight = False
                    # Восстанавливаем гравитацию после супер-атаки
                    self.change_y = 0  # Сбрасываем вертикальную скорость
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

    def create_ex_bullet(self):
        """Создание супер-пули (вызывается из анимации)"""
        direction_x = 1 if self.direction == "right" else -1
        direction_y = 0
        bullet_angle = 0

        # Позиция выстрела
        flag = self.direction == "right"
        pull_move = self.center_x + 60 * (-1, 1)[flag]
        pull_up = self.center_y - 20

        # Текстура для супер-пули
        shoot = arcade.load_texture("images/Supers/Mega_Blast.png")

        # Для стрельбы влево - зеркалим
        if not flag:
            shoot = shoot.flip_left_right()

        # Создаем супер-пулю
        bullet = Bullet(
            pull_move,
            pull_up,
            direction_x,
            direction_y,
            shoot,
            bullet_angle,
            is_ex=True,
        )

        # Добавляем пулю в список для добавления
        self.bullets_to_add.append(bullet)


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background = arcade.load_texture("images/backgrounds/background.jpg")

    def setup(self):
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.cuphead = CupHead("images/Idle/cuphead_idle_0001.png", 0.8, 2)
        self.cuphead.center_x = 50
        self.cuphead.center_y = 100
        self.cuphead.change_x = 0
        self.cuphead.change_y = 0
        self.satyr = Satyr(random.randint(50, 750), 70, -1)
        self.pull = cycle((15, 0, -15))

        self.victory = False
        self.loose = False
        self.hits = 0

        self.all_sprites.append(self.cuphead)
        self.enemies.append(self.satyr)

    def on_draw(self):
        arcade.draw_texture_rect(
            self.background,
            arcade.XYWH(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT
            ),
        )

        self.all_sprites.draw()
        self.enemies.draw()
        self.bullets.draw()
        if self.victory:
            self.pp.draw()

    def on_update(self, delta_time):
        if self.loose or self.victory:
            return

        self.all_sprites.update(delta_time)
        self.bullets.update(delta_time)
        self.enemies.update(delta_time)  # Теперь вызываем без параметра hits
        self.cuphead.update(delta_time)

        # Добавляем пули из списка cuphead (супер-атака)
        for bullet in self.cuphead.bullets_to_add:
            self.bullets.append(bullet)
        self.cuphead.bullets_to_add.clear()  # Очищаем список после добавления

        # Применяем гравитацию только если не в дэше, не в flex и не в супер-атаке
        if (
                not self.cuphead.dashing
                and self.cuphead.can_move
                and not self.cuphead.dashing_back
                and not self.cuphead.flexing  # Не применяем гравитацию во время flex
                and not self.cuphead.ex_straight  # Не применяем гравитацию во время супер-атаки
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
            self.bullets.append(bullet)

            # кулдаун
            self.cuphead.shoot_cooldown = 6

        if self.cuphead.shoot_cooldown > 0:
            self.cuphead.shoot_cooldown -= 1

        # Сбрасываем состояния стрельбы при беге, если не стреляем или не двигаемся
        if not self.cuphead.shooting or not self.cuphead.moving:
            self.cuphead.shoot_straight_running = False
            self.cuphead.shoot_diagonal_up_running = False
            self.cuphead.shoot_diagonal_up_running_left = False

        # Проверка столкновений пуль с сатиром
        for enemy in self.enemies:
            hit_list = arcade.check_for_collision_with_list(enemy, self.bullets)
            for bullet in hit_list:
                bullet.remove_from_sprite_lists()
                enemy.take_damage(10)  # Наносим урон через метод

    def on_key_press(self, key, modifiers):
        if (
                self.loose
                or self.victory
                or self.cuphead.flexing
                or self.cuphead.ex_straight
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
            ):
                self.cuphead.change_x = SPEED
                self.cuphead.moving = True
            elif self.cuphead.duck:
                self.cuphead.moving = False
                self.cuphead.change_x = 0

        elif key == arcade.key.UP:
            self.cuphead.keys_pressed["up"] = True
            # При нажатии UP меняем состояние стрельбы если уже стреляем и на земле
            if (
                    self.cuphead.shooting
                    and not self.cuphead.moving
                    and not self.cuphead.duck
                    and self.cuphead.on_ground
            ):
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
                and not self.cuphead.ex_straight
        ):
            self.cuphead.change_y = 10
            self.cuphead.on_ground = False

        # ДЭШ
        if (
                key == arcade.key.X
                and not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
        ):
            if self.cuphead.count_dash:
                self.cuphead.start_dash()
                if not self.cuphead.on_ground:
                    self.cuphead.count_dash -= 1

        # FLEX
        elif (
                key == arcade.key.F
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and self.cuphead.on_ground
        ):
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

        # Супер-атака (V)
        elif (
                key == arcade.key.V
                and not self.cuphead.ex_straight
                and not self.cuphead.flexing
        ):
            self.cuphead.ex_straight = True
            self.cuphead.change_x = 0
            self.cuphead.change_y = 0  # Сбрасываем вертикальную скорость
            self.cuphead.moving = False
            self.cuphead.can_move = False
            # Останавливаем стрельбу при начале супер-атаки
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
        ):
            self.cuphead.shooting = True
            # При начале стрельбы устанавливаем состояние по умолчанию
            if (
                    not self.cuphead.moving
                    and not self.cuphead.duck
                    and self.cuphead.on_ground
            ):
                self.cuphead.shooting_straight = True

    def on_key_release(self, key, modifiers):
        if (
                self.loose
                or self.victory
                or self.cuphead.flexing
                or self.cuphead.ex_straight
        ):
            return

        if key == arcade.key.LEFT:
            self.cuphead.keys_pressed["left"] = False

        elif key == arcade.key.RIGHT:
            self.cuphead.keys_pressed["right"] = False

        elif key == arcade.key.UP:
            self.cuphead.keys_pressed["up"] = False
            # При отпускании UP меняем состояние стрельбы только если на земле
            if (
                    self.cuphead.shooting
                    and not self.cuphead.moving
                    and not self.cuphead.duck
                    and self.cuphead.on_ground
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
                and not self.cuphead.ex_straight
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
