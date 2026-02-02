import arcade
import random
from itertools import cycle
import math

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Овощебанда"
SPEED = 5
WATER_HEIGHT = SCREEN_HEIGHT // 3
BULLET_SPEED = 40
EX_BULLET_SPEED = 30  # Скорость для супер-пуль
DRAGON_FIRE_SPEED = 8  # Скорость снаряда дракона


class DragonFire(arcade.Sprite):
    # Кеширование текстур для оптимизации
    _texture_cache_normal = None
    _texture_cache_pink = None

    @classmethod
    def _load_textures(cls, is_pink=False):
        """Загружаем текстуры один раз и кешируем их"""
        if is_pink:
            if cls._texture_cache_pink is not None:
                return cls._texture_cache_pink

            text = "Pink/lv3-2_baby_dragon_fireball_pink_"
        else:
            if cls._texture_cache_normal is not None:
                return cls._texture_cache_normal

            text = "Normal/lv3-2_baby_dragon_fireball_"

        textures_list = []
        for i in range(1, 21):
            texture = arcade.load_texture(
                f"images/Baby Dragon/{text}{'0' * (4 - len(str(i)))}{i}.png"
            )
            textures_list.append(texture)

        # Кешируем загруженные текстуры
        if is_pink:
            cls._texture_cache_pink = textures_list
        else:
            cls._texture_cache_normal = textures_list

        return textures_list

    def __init__(self, x, y, target_x, target_y, is_pink=False):
        scale = 1
        # Загружаем текстуры из кеша
        self.textures_list = DragonFire._load_textures(is_pink)

        # Используем первую текстуру для создания спрайта
        super().__init__(self.textures_list[0], scale=scale)
        self.center_x = x
        self.center_y = y
        self.lifetime = 480

        # Вычисляем направление к цели (игроку)
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)

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
        self.can_be_parried = is_pink  # Только розовые снаряды можно парировать
        self.current_frame = 0
        self.counter = 0
        self.knockable = True  # По умолчанию пули отскакивают

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

        # Только отскакивающие пули меняют направление
        if self.knockable:
            if self.top >= SCREEN_HEIGHT or self.bottom <= 0:
                self.change_y *= -1
            if self.right >= SCREEN_WIDTH or self.left <= 0:
                self.change_x *= -1

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

        # Удаляем если вылетел за экран
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
        """Загружаем текстуры один раз и кешируем их"""
        if cls._texture_cache is not None:
            return

        cls._texture_cache = {
            "down": {"idle": [], "fly_up": [], "attack": []},
            "left": {"idle": [], "fly_up": [], "attack": []},
            "right": {"idle": [], "fly_up": [], "attack": []},
        }

        # Загрузка текстур для DOWN
        for i in range(1, 20):
            path = f"images/Baby Dragon/Down/Idle/lv3-2_baby_dragon_idle_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["down"]["idle"].append(texture)

        for i in range(1, 6):
            path = f"images/Baby Dragon/Down/Fly up/lv3-2_baby_dragon_fly_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["down"]["fly_up"].append(texture)

        for i in range(1, 28):
            path = f"images/Baby Dragon/Down/Attack/lv3-2_baby_dragon_attack_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["down"]["attack"].append(texture)

        # Загрузка текстур для LEFT
        for i in range(1, 11):
            path = f"images/Baby Dragon/Left - Right/Idle/lv3-2_baby_dragon_3Q_idle_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["left"]["idle"].append(texture)

        for i in range(1, 6):
            path = f"images/Baby Dragon/Left - Right/Fly up/lv3-2_baby_dragon_3Q_fly_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["left"]["fly_up"].append(texture)

        for i in range(1, 23):
            path = f"images/Baby Dragon/Left - Right/Attack/lv3-2_baby_dragon_3Q_attack_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            cls._texture_cache["left"]["attack"].append(texture)

        # Загрузка текстур для RIGHT
        for i in range(1, 11):
            path = f"images/Baby Dragon/Left - Right/Idle/lv3-2_baby_dragon_3Q_idle_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            texture = texture.flip_left_right()
            cls._texture_cache["right"]["idle"].append(texture)

        for i in range(1, 6):
            path = f"images/Baby Dragon/Left - Right/Fly up/lv3-2_baby_dragon_3Q_fly_up_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            texture = texture.flip_left_right()
            cls._texture_cache["right"]["fly_up"].append(texture)

        for i in range(1, 23):
            path = f"images/Baby Dragon/Left - Right/Attack/lv3-2_baby_dragon_3Q_attack_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            texture = texture.flip_left_right()
            cls._texture_cache["right"]["attack"].append(texture)

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

        # Для управления анимацией стрельбы
        self.is_shooting = False
        self.shoot_counter = 0  # Сколько выстрелов осталось сделать
        self.current_shoot_frame = 0
        self.shoot_animation_delay = 0
        self.shoot_animation_forward = True

        # Для хранения игрока для выстрела
        self.target_player = None
        # Для хранения созданных снарядов
        self.fireballs_to_add = []

        # Таймер для стрельбы
        self.shoot_timer = 0
        self.shoot_cooldown = 60
        self.can_shoot = False

        # Количество выстрелов за одну атаку
        self.max_shots = 3 if dragon_type == 2 else 1

        # Для тройного выстрела
        self.shoot_pattern = cycle((True, False))

    def shoot_at_player(self, player):
        """Стреляет в игрока, если можно"""
        if not self.can_shoot or self.shoot_timer < self.shoot_cooldown:
            return []

        # Сохраняем цель для выстрелов
        self.target_player = player

        # Устанавливаем количество выстрелов
        self.shoot_counter = self.max_shots

        # Запускаем анимацию стрельбы
        self.is_shooting = True
        self.current_shoot_frame = 0
        self.shoot_animation_delay = 0
        self.shoot_animation_forward = True
        self.fireballs_to_add.clear()  # Очищаем список снарядов

        # Сбрасываем таймер
        self.shoot_timer = 0

        return []

    def create_shoot_projectile(self):
        """Создает снаряд при выстреле в зависимости от типа дракона"""
        if not self.target_player:
            return []

        fireballs = []

        if self.dragon_type == 0:
            # Обычный дракон
            fireball = DragonFire(
                self.center_x, self.center_y,
                self.target_player.center_x, self.target_player.center_y, False
            )
            fireball.knockable = True
            fireballs.append(fireball)

        elif self.dragon_type == 1:
            # Дракон с розовыми снарядами
            fireball = DragonFire(
                self.center_x, self.center_y,
                self.target_player.center_x, self.target_player.center_y, True
            )
            fireball.knockable = True
            fireballs.append(fireball)

        elif self.dragon_type == 2:
            # Дракон с тремя снарядами
            is_pink = next(self.shoot_pattern)

            for angle_offset in [-15, 0, 15]:
                dx = self.target_player.center_x - self.center_x
                dy = self.target_player.center_y - self.center_y
                distance = math.sqrt(dx ** 2 + dy ** 2)
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

        return fireballs

    def update(self, delta_time):
        """Обновление состояния BabyDragon"""
        if self.is_dead or self.disappear:
            return

        super().update()

        # Если идет анимация стрельбы, обрабатываем ее отдельно
        if self.is_shooting:
            self.update_shoot_animation()
            # Возвращаемся чтобы не обновлять обычную анимацию
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
        """Обновление анимации стрельбы - вперед и назад"""
        self.shoot_animation_delay += 1

        # Задержка между кадрами анимации стрельбы
        if self.shoot_animation_delay >= 3:
            self.shoot_animation_delay = 0

            # Получаем текстуры атаки
            attack_textures = self._get_current_textures("attack")
            total_frames = len(attack_textures)

            # Логика для анимации DOWN дракона (фреймы 1-27)
            if self.position_type == "down":
                # Если счетчик выстрелов > 0
                if self.shoot_counter > 0:
                    # Движемся вперед
                    if self.shoot_animation_forward:
                        self.current_shoot_frame += 1

                        # Проверяем, достигли ли 24 кадра (индекс 23, т.к. с 0)
                        if self.current_shoot_frame == 23:
                            # Производим выстрел, если счетчик > 0
                            if self.shoot_counter > 0:
                                fireballs = self.create_shoot_projectile()
                                if fireballs:
                                    self.fireballs_to_add.extend(fireballs)
                                self.shoot_counter -= 1

                            # Если счетчик равен 0, продолжаем до конца
                            if self.shoot_counter <= 0:
                                # Продолжаем до 27 кадра (индекс 26)
                                if self.current_shoot_frame < 26:
                                    # Обновляем текстуру
                                    if 0 <= self.current_shoot_frame < total_frames:
                                        self.texture = attack_textures[self.current_shoot_frame]
                                    return
                                # Если уже на 26 кадре, завершаем анимацию
                                else:
                                    self.complete_shoot_animation()
                                    return
                            else:
                                # Меняем направление на обратное
                                self.shoot_animation_forward = False

                        # Проверяем достижение 17 кадра (индекс 16) для первого выстрела
                        elif self.current_shoot_frame == 16 and self.shoot_counter == self.max_shots:
                            # Производим выстрел
                            fireballs = self.create_shoot_projectile()
                            if fireballs:
                                self.fireballs_to_add.extend(fireballs)
                            self.shoot_counter -= 1

                    # Движемся назад
                    else:
                        self.current_shoot_frame -= 1

                        # Проверяем, достигли ли 17 кадра (индекс 16) для выстрела
                        if self.current_shoot_frame == 16:
                            # Производим выстрел, если счетчик > 0
                            if self.shoot_counter > 0:
                                fireballs = self.create_shoot_projectile()
                                if fireballs:
                                    self.fireballs_to_add.extend(fireballs)
                                self.shoot_counter -= 1

                            # Если счетчик равен 0, меняем направление на вперед
                            if self.shoot_counter <= 0:
                                self.shoot_animation_forward = True

                        # Если дошли до 16 кадра (индекс 15), снова меняем направление
                        elif self.current_shoot_frame <= 15:
                            self.current_shoot_frame = 15
                            self.shoot_animation_forward = True

                # Если счетчик выстрелов <= 0
                else:
                    # Просто продолжаем до конца анимации
                    if self.current_shoot_frame < 26:
                        self.current_shoot_frame += 1
                    else:
                        # Завершаем анимацию
                        self.complete_shoot_animation()
                        return

            # Логика для анимации LEFT/RIGHT дракона (фреймы 1-22)
            else:
                if self.shoot_counter > 0:
                    if self.shoot_animation_forward:
                        self.current_shoot_frame += 1

                        # Выстрел на 15 кадре (индекс 14)
                        if self.current_shoot_frame == 14 and self.shoot_counter > 0:
                            fireballs = self.create_shoot_projectile()
                            if fireballs:
                                self.fireballs_to_add.extend(fireballs)
                            self.shoot_counter -= 1

                        # Если дошли до 19 кадра (индекс 18)
                        elif self.current_shoot_frame == 18:
                            if self.shoot_counter <= 0:
                                # Продолжаем до конца
                                if self.current_shoot_frame < 21:
                                    # Обновляем текстуру
                                    if 0 <= self.current_shoot_frame < total_frames:
                                        self.texture = attack_textures[self.current_shoot_frame]
                                    return
                                else:
                                    self.complete_shoot_animation()
                                    return
                            else:
                                # Меняем направление
                                self.shoot_animation_forward = False

                    else:
                        self.current_shoot_frame -= 1

                        # Если дошли до 10 кадра (индекс 9)
                        if self.current_shoot_frame == 9:
                            if self.shoot_counter <= 0:
                                self.shoot_animation_forward = True
                else:
                    # Завершаем анимацию
                    if self.current_shoot_frame < 21:
                        self.current_shoot_frame += 1
                    else:
                        self.complete_shoot_animation()
                        return

            # Проверяем границы кадров
            if self.current_shoot_frame < 0:
                self.current_shoot_frame = 0
            elif self.current_shoot_frame >= total_frames:
                self.current_shoot_frame = total_frames - 1

            # Обновляем текстуру
            if 0 <= self.current_shoot_frame < total_frames:
                self.texture = attack_textures[self.current_shoot_frame]

    def complete_shoot_animation(self):
        """Завершение анимации стрельбы"""
        self.is_shooting = False
        self.state = "fly_up"
        self.attack_done = False
        self.current_frame = 0
        self.shoot_counter = 0
        self.target_player = None
        self.animation_speed_counter = 0

    def _get_current_textures(self, state):
        """Получить текущий список текстур в зависимости от состояния и позиции"""
        return BabyDragon._texture_cache[self.position_type][state]

    def update_animation(self):
        """Обновление анимации"""
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
        """Обновление текущей текстуры спрайта"""
        textures = self._get_current_textures(self.state)
        if textures and 0 <= self.current_frame < len(textures):
            self.texture = textures[self.current_frame]

    def take_damage(self, damage):
        """Принять урон"""
        if not self.invincible and not self.is_dead and not self.disappear:
            self.hp -= damage
            if self.hp <= 0:
                self.is_dead = True
                self.can_damage = False
                self.can_shoot = False
                self.remove_from_sprite_lists()


class Mudman(arcade.Sprite):
    def __init__(self, x, y, direction_x, shoot=None):
        texture = arcade.load_texture(
            "images/Mudman/Intro/lv3-2_mudman_small_intro_0001.png"
        )
        super().__init__(texture)

        self.center_x = x
        self.center_y = y
        self.change_x = 0  # Mudman не двигается
        self.change_y = 0

        self.direction = "right" if direction_x > 0 else "left"
        self.start = True  # Флаг начальной анимации (intro)
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
        self.is_dead = False  # Флаг смерти

        # Загрузка текстур
        self.textures_dict = {
            "intro": {"right": [], "left": []},
            "splash": {"right": [], "left": []},
        }

        for i in range(1, 22):
            path = f"images/Mudman/Intro/lv3-2_mudman_small_intro_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["intro"]["left"].append(texture)

        for texture in self.textures_dict["intro"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["intro"]["right"].append(flipped_texture)

        for i in range(1, 11):
            path = f"images/Mudman/Splash/Small/One/lv3-2_mudman_small_splash_one_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["splash"]["left"].append(texture)

        for texture in self.textures_dict["splash"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["splash"]["right"].append(flipped_texture)

        # Устанавливаем начальную текстуру
        self.update_texture()

    def update(self, delta_time):
        """Обновление состояния Mudman"""
        # Если Mudman мертв и проигрывает анимацию splash, продолжаем обновление
        if self.is_dead:
            # Обновляем анимацию смерти
            self.animation_speed_counter += 1
            if self.animation_speed_counter >= self.animation_speed:
                self.animation_speed_counter = 0
                self.update_animation()
                self.update_texture()
            return

        # Если у Mudman не осталось HP, начинаем анимацию смерти
        if self.hp <= 0 and not self.is_dead:
            self.is_dead = True
            self.state = "splash"
            self.current_frame = 0
            self.animation_speed_counter = 0
            self.can_damage = False  # Больше не может наносить урон
            return

        # Обновление таймера неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        super().update()

        # Обновление анимации
        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.animation_speed:
            self.animation_speed_counter = 0
            self.update_animation()
            self.update_texture()

        # После завершения анимации появления, Mudman может наносить урон
        if self.start and not self.start_intro_complete:
            # Проигрываем анимацию intro
            if (
                    self.current_frame
                    >= len(self.textures_dict["intro"][self.direction]) - 1
            ):
                self.start_intro_complete = True
                self.start = False
                self.state = (
                    "intro"  # Остаемся в состоянии intro, но уже завершили анимацию
                )
                self.can_damage = True  # Теперь может наносить урон
        elif not self.start and self.start_intro_complete:
            self.can_damage = True

    def update_animation(self):
        """Обновление анимации"""
        if self.state == "intro":
            textures_list = self.textures_dict["intro"][self.direction]
            if textures_list:
                if not self.start_intro_complete:
                    # Проигрываем анимацию появления до конца
                    if self.current_frame < len(textures_list) - 1:
                        self.current_frame += 1
        elif self.state == "splash":
            textures_list = self.textures_dict["splash"][self.direction]
            if textures_list:
                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    # Анимация смерти завершена - удаляем спрайт
                    self.remove_from_sprite_lists()

    def update_texture(self):
        """Обновление текущей текстуры спрайта"""
        textures_list = self.textures_dict[self.state][self.direction]
        if textures_list and 0 <= self.current_frame < len(textures_list):
            self.texture = textures_list[self.current_frame]

    def take_damage(self, damage):
        """Принять урон"""
        if (
                not self.invincible and not self.is_dead
        ):  # Получаем урон только если не неуязвимы и не мертвы
            self.hp -= damage
            if self.hp <= 0:
                # Не удаляем сразу, начинаем анимацию смерти
                self.is_dead = True
                self.state = "splash"
                self.current_frame = 0
                self.animation_speed_counter = 0
                self.can_damage = False


class Satyr(arcade.Sprite):
    def __init__(self, x, y, direction_x, shoot=None):
        texture = arcade.load_texture("images/Satyr/Jump/lv3-2_satyr_jump_0001.png")
        super().__init__(texture)

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

        # Загрузка текстур
        self.textures_dict = {
            "jump": {"right": [], "left": []},
            "run": {"right": [], "left": []},
            "turn": {"right": [], "left": []},
        }

        # Загрузка анимации прыжка
        for i in range(1, 20):
            path = (
                f"images/Satyr/Jump/lv3-2_satyr_jump_{'0' * (4 - len(str(i)))}{i}.png"
            )
            texture = arcade.load_texture(path)
            self.textures_dict["jump"]["left"].append(texture)

        for texture in self.textures_dict["jump"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["jump"]["right"].append(flipped_texture)

        # Загрузка анимации бега/пропуска
        for i in range(1, 25):
            path = (
                f"images/Satyr/Skip/lv3-2_satyr_skip_{'0' * (4 - len(str(i)))}{i}.png"
            )
            texture = arcade.load_texture(path)
            self.textures_dict["run"]["left"].append(texture)

        for texture in self.textures_dict["run"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["run"]["right"].append(flipped_texture)

        # Загрузка анимации поворота
        for i in range(1, 5):
            path = (
                f"images/Satyr/Turn/lv3-2_satyr_turn_{'0' * (4 - len(str(i)))}{i}.png"
            )
            texture = arcade.load_texture(path)
            self.textures_dict["turn"]["left"].append(texture)

        for texture in self.textures_dict["turn"]["left"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["turn"]["right"].append(flipped_texture)

        # Устанавливаем начальную текстуру
        self.update_texture()

    def update(self, delta_time):
        """Обновление состояния сатира"""
        # Если у сатира не осталось HP, не обновляем его
        if self.hp <= 0:
            return

        # Обновление таймера неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

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
            if (
                    self.jump_frames <= 20
            ):  # Первые 20 обновлений (примерно 5 кадров анимации)
                # Поднимаемся
                self.change_y = 10
            elif self.jump_frames <= 40:  # Следующие 20 обновлений (кадры 5-10)
                # Падаем
                self.change_y = -8
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
                    self.can_damage = True
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
        if not self.invincible:  # Получаем урон только если не неуязвимы
            self.hp -= damage
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
        self.angle = angle  # Угол поворота для диагональных выстрелов
        if angle != 0:
            self.angle = angle  # Устанавливаем угол поворота спрайта
        self.is_ex = is_ex  # Флаг супер-пули
        self.damage = 30 if is_ex else 5  # Урон от пули

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
            "shoot_diagonal_up": {"right": [], "left": []},
            "shoot_diagonal_down": {"right": [], "left": []},
            "shoot_straight_running": {"right": [], "left": []},
            "shoot_diagonal_up_running": {"right": [], "left": []},
            "shoot_diagonal_up_running_left": {
                "right": [],
                "left": [],
            },
            "duck_shoot": {"right": [], "left": []},
            "ex_straight": {"right": [], "left": []},
            "hit": {"right": [], "left": []},
            "death": {"right": [], "left": []},
            "ghost": {"right": [], "left": []},
            "parry": {"right": [], "left": []},
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

        for i in range(1, 16):
            path = f"images/Special Attck/Straight/Ground/cuphead_ex_straight_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["ex_straight"]["right"].append(texture)

        for texture in self.textures_dict["ex_straight"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["ex_straight"]["left"].append(flipped_texture)

        for i in range(1, 7):
            path = f"images/Hit/Ground/cuphead_hit_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["hit"]["right"].append(texture)

        for texture in self.textures_dict["hit"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["hit"]["left"].append(flipped_texture)

        for i in range(1, 17):
            path = f"images/Death/cuphead_death_body_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["death"]["right"].append(texture)

        for texture in self.textures_dict["death"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["death"]["left"].append(flipped_texture)

        for i in range(1, 25):
            path = f"images/Ghost/cuphead_ghost_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["ghost"]["right"].append(texture)

        for texture in self.textures_dict["ghost"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["ghost"]["left"].append(flipped_texture)

        for i in range(1, 9):
            path = f"images/Parry/Hand/cuphead_parry_{'0' * (4 - len(str(i)))}{i}.png"
            texture = arcade.load_texture(path)
            self.textures_dict["parry"]["right"].append(texture)

        for texture in self.textures_dict["parry"]["right"]:
            flipped_texture = texture.flip_left_right()
            self.textures_dict["parry"]["left"].append(flipped_texture)

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
        self.death = False
        self.hp = 3
        self.invincible = False  # Флаг неуязвимости
        self.invincible_timer = 0  # Таймер неуязвимости
        self.just_took_damage = False  # Флаг только что получил урон
        self.disable_input = False  # Флаг отключения ввода

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

        self.hit = False
        self.hit_check = False

        self.ghost = False

        # Паррирование
        self.parry = False
        self.parry_timer = 0
        self.parry_cooldown = 0
        self.can_parry = True
        self.parry_success = False
        self.parry_success_timer = 0
        self.ex_meter = 0  # Шкала супер-атаки
        self.max_ex_meter = 5  # 5 паррирований = полная шкала
        self.can_air_parry = False  # Можно ли парировать в воздухе
        self.air_parry_window = 0  # Окно для паррирования в воздухе
        self.in_air_parry_window = False  # В окне для воздушного паррирования
        self.has_jumped = False  # Совершил ли прыжок

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

        # Если уже призрак, обрабатываем отдельно
        if self.ghost:
            self.process_ghost_state()
            return

        # Если умер, останавливаем движение и выходим
        if self.death:
            self.change_x = 0
            self.change_y = 0
            self.moving = False
            self.can_move = False
            self.disable_input = True
            # Пропускаем обычную логику и переходим сразу к смерти
            self.update_death_animation()
            return

        # Обновление таймера неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.alpha = 255  # Восстанавливаем полную видимость
            else:
                # Мерцание при неуязвимости
                if self.invincible_timer % 4 < 2:
                    self.alpha = 128
                else:
                    self.alpha = 255

        # Обновление паррирования
        if self.parry:
            self.parry_timer -= 1
            if self.parry_timer <= 0:
                self.parry = False
                self.can_parry = True

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
                self.update_animation()
                self.update_texture()

    def process_ghost_state(self):
        """Обработка состояния призрака"""
        if not self.ghost:
            return

        # Устанавливаем состояние ghost если еще не установлено
        if self.state != "ghost":
            self.state = "ghost"
            self.current_frame = 0
            self.animation_speed_counter = 0

        # Обновляем анимацию призрака
        self.animation_speed_counter += 1
        if self.animation_speed_counter >= self.animation_speeds["ghost"]:
            self.animation_speed_counter = 0
            self.update_ghost_animation()

        # Двигаем призрака вверх
        self.change_y = 3

        # Проверяем, улетел ли призрак за пределы экрана
        if self.bottom > SCREEN_HEIGHT:
            self.remove_from_sprite_lists()

    def update_ghost_animation(self):
        """Обновление анимации призрака"""
        textures_list = self.textures_dict["ghost"]["right"]
        if textures_list:
            self.current_frame = (self.current_frame + 1) % len(textures_list)
            self.texture = textures_list[self.current_frame]

    def update_death_animation(self):
        """Отдельный метод для анимации смерти"""
        textures_list = self.textures_dict["death"]["right"]
        if textures_list:
            if self.current_frame < len(textures_list) - 1:
                self.animation_speed_counter += 1
                if self.animation_speed_counter >= self.animation_speeds["death"]:
                    self.animation_speed_counter = 0
                    self.current_frame += 1
                    self.texture = textures_list[self.current_frame]
            else:
                # Анимация смерти завершена - переходим в состояние призрака
                self.ghost = True
                self.state = "ghost"
                self.current_frame = 0
                self.animation_speed_counter = 0
                self.change_y = 5  # Начинаем подниматься

    def update_animation(self):
        """Обновление анимации"""
        if self.state == "death":
            return  # Обрабатывается отдельно в update_death_animation()

        if self.state == "hit":
            self.hit_check = True
            textures_list = self.textures_dict["hit"][self.direction]
            if textures_list:
                # НЕ останавливаем движение при получении урона
                self.can_move = True  # Можно двигаться во время анимации урона

                if self.current_frame < len(textures_list) - 1:
                    self.current_frame += 1
                else:
                    # Активируем временную неуязвимость после получения урона
                    self.invincible = True
                    self.invincible_timer = 90  # 1.5 секунды при 60 FPS
                    self.hit = False
                    self.hit_check = False
                    self.just_took_damage = False
                return

        if self.state == "ex_straight":
            self.hit_check = False
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
        elif self.state == "parry":
            textures_list = self.textures_dict["parry"][self.direction]
            if textures_list:
                self.current_frame = (self.current_frame + 1) % len(textures_list)
                if self.current_frame >= len(textures_list) - 1:
                    if not self.on_ground:
                        self.state = "jump"
                    else:
                        self.state = "idle"
                    self.current_frame = 0

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
        print('s')

        # Позиция выстрела
        flag = self.direction == "right"
        pull_move = self.center_x + 60 * (-1, 1)[flag]
        pull_up = self.center_y

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

    def process_parry(self, is_air_parry=False):
        """Активация паррирования"""
        if self.can_parry and self.parry_cooldown <= 0 and not self.hit:
            # Проверяем условия для воздушного паррирования
            if is_air_parry:
                # Только если в воздухе и в окне паррирования
                if (
                        not self.on_ground
                        and self.has_jumped
                        and self.air_parry_window <= 30
                ):
                    self.parry = True
                    self.parry_timer = 15
                    self.parry_cooldown = 30
                    self.can_parry = False
                    self.can_move = True
                    self.state = "parry"
                    self.current_frame = 0
                    self.animation_speed_counter = 0
                    return True
                return False

        return False

    def parry_successful(self):
        """Успешное паррирование"""
        self.parry_success = True
        self.parry_success_timer = 30  # Показываем эффект 1 секунду
        self.ex_meter += 1
        if self.ex_meter >= self.max_ex_meter:
            self.ex_meter = self.max_ex_meter
            # Можно добавить визуальный эффект полной шкалы

        self.change_y = 6  # Отскок вверх после паррирования

    def take_damage(self):
        """Получить урон"""
        if not self.invincible and not self.just_took_damage and not self.parry:
            self.hp -= 1
            self.hit = True
            self.just_took_damage = True
            self.invincible = True
            self.invincible_timer = 90  # 1.5 секунды неуязвимости

            # НЕ останавливаем стрельбу полностью, только сбрасываем флаги стрельбы
            self.shooting_straight = False
            self.shooting_up = False
            self.shooting_down = False
            self.shoot_straight_running = False
            self.shoot_diagonal_up_running = False
            self.shoot_diagonal_up_running_left = False
            self.duck_shooting = False
            self.shooting_diagonal_up = False

            # НЕ останавливаем движение
            # Можно продолжать стрельбу после получения урона
            # если кнопка все еще зажата
            if self.shooting:
                self.shooting = True  # Сохраняем флаг стрельбы


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background = arcade.load_texture("images/backgrounds/background.jpg")

    def setup(self):
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.dragon_fireballs = arcade.SpriteList()  # Новый список для снарядов дракона

        self.cuphead = CupHead("images/Idle/cuphead_idle_0001.png", 1, 2)
        self.cuphead.center_x = 50
        self.cuphead.center_y = 100
        self.cuphead.change_x = 0
        self.cuphead.change_y = 0
        self.cuphead.alpha = 255  # Инициализируем альфа-канал
        self.pull = cycle((15, 0, -15))

        self.victory = False
        self.loose = False
        self.hits = 0
        self.timer_cpawn_satyr = 0
        self.shoot = 0

        self.all_sprites.append(self.cuphead)

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
        self.dragon_fireballs.draw()  # Рисуем снаряды дракона

        # Отображаем HP
        arcade.draw_text(
            f"HP: {self.cuphead.hp}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.RED,
            24,
            bold=True,
        )

        # Отображаем шкалу супер-атаки

        # Отображаем эффект паррирования
        if self.cuphead.parry_success:
            arcade.draw_text(
                "PARRY!",
                self.cuphead.center_x - 40,
                self.cuphead.center_y + 80,
                arcade.color.YELLOW,
                32,
                bold=True,
            )

        if self.victory:
            self.pp.draw()

    def on_update(self, delta_time):
        if self.loose or self.victory:
            return

        self.timer_cpawn_satyr += 1
        if self.timer_cpawn_satyr > 100:
            choose = random.choice((BabyDragon,))
            if choose == BabyDragon:
                dragon_type = random.randint(0, 2)
                position_type = random.choice(["down", "left", "right"])

                # Определяем координаты в зависимости от позиции
                if position_type == "down":
                    x = random.randint(300, SCREEN_WIDTH - 300)  # Центр экрана
                elif position_type == "left":
                    x = 150  # Левая часть
                else:  # "right"
                    x = SCREEN_WIDTH - 150  # Правая часть

                enemy = BabyDragon(
                    x, 100, random.choice((-1, 1)), dragon_type, position_type
                )
            else:
                enemy = choose(
                    random.randint(50, 1200), 100, random.choice((-1, 1)), shoot=None
                )

            self.enemies.append(enemy)
            self.timer_cpawn_satyr = 0

        # Сначала обновляем спрайты
        self.all_sprites.update(delta_time)
        self.bullets.update(delta_time)
        self.enemies.update(delta_time)
        self.dragon_fireballs.update(delta_time)  # Обновляем снаряды дракона
        self.cuphead.update(delta_time)

        # Если капхед умер, не обновляем остальную логику
        if self.cuphead.death:
            return

        # Добавляем пули из списка cuphead (супер-атака)
        for bullet in self.cuphead.bullets_to_add:
            self.bullets.append(bullet)
        self.cuphead.bullets_to_add.clear()  # Очищаем список после добавления

        # Обрабатываем стрельбу драконов
        for dragon in self.enemies:
            if isinstance(dragon, BabyDragon):
                fireballs = dragon.shoot_at_player(self.cuphead)
                if fireballs:
                    for fireball in fireballs:
                        self.dragon_fireballs.append(fireball)

        # Проверка столкновений с врагами
        check_enemies = arcade.check_for_collision_with_list(self.cuphead, self.enemies)
        for c in check_enemies:
            if c.can_damage:
                self.cuphead.take_damage()

        # Проверка столкновений со снарядами дракона
        check_fireballs = arcade.check_for_collision_with_list(
            self.cuphead, self.dragon_fireballs
        )
        for fireball in check_fireballs:
            if self.cuphead.parry and fireball.can_be_parried:
                # Успешное паррирование розового снаряда
                self.cuphead.parry_successful()
                fireball.remove_from_sprite_lists()
            elif not self.cuphead.invincible and not self.cuphead.parry:
                self.cuphead.take_damage()
                fireball.remove_from_sprite_lists()

        # Применяем гравитацию ТОЛЬКО если не в состоянии урона и не в дэше
        if (
                not self.cuphead.dashing
                and self.cuphead.can_move
                and not self.cuphead.dashing_back
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and not self.cuphead.hit  # Исключаем гравитацию во время урона
                and not self.cuphead.parry
                and not self.cuphead.on_ground  # Гравитация только в воздухе
        ):
            self.cuphead.change_y -= 0.5

        # ОБНОВЛЕНИЕ ОКНА ВОЗДУШНОГО ПАРРИРОВАНИЯ - ИСПРАВЛЕННЫЙ КОД
        if self.cuphead.has_jumped and not self.cuphead.on_ground:
            self.cuphead.air_parry_window += 1
            if self.cuphead.air_parry_window <= 30:  # 30 кадров (0.5 секунды) окно
                self.cuphead.in_air_parry_window = True
            else:
                self.cuphead.in_air_parry_window = False
        else:
            # Сброс при приземлении
            self.cuphead.has_jumped = False
            self.cuphead.in_air_parry_window = False
            self.cuphead.air_parry_window = 0

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

        # Проверка столкновений пуль с врагами
        for enemy in self.enemies:
            hit_list = arcade.check_for_collision_with_list(enemy, self.bullets)
            for bullet in hit_list:
                if (
                        enemy in self.enemies and enemy.can_damage
                ):  # Проверяем, что враг еще существует
                    enemy.take_damage(bullet.damage)  # Наносим урон через метод
                    if bullet in self.bullets:  # Проверяем, что пуля еще существует
                        bullet.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        # Если капхед умер или отключен ввод, игнорируем нажатия
        if self.cuphead.death or self.cuphead.disable_input:
            return

        if (
                self.loose
                or self.victory
                or self.cuphead.flexing
                or self.cuphead.ex_straight
                or self.cuphead.hit  # Не обрабатываем ввод во время получения урона
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
                    and not self.cuphead.parry  # Можно двигаться во время паррирования
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
                    and not self.cuphead.parry  # Можно двигаться во время паррирования
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
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and not self.cuphead.hit
        ):
            # Первое нажатие - обычный прыжок
            if self.cuphead.on_ground:
                self.cuphead.change_y = 10
                self.cuphead.on_ground = False
                self.cuphead.has_jumped = True
                self.cuphead.air_parry_window = 0  # Сбрасываем окно
            # Второе нажатие в окне - воздушное паррирование
            elif not self.cuphead.on_ground and self.cuphead.has_jumped:
                # Активируем воздушное паррирование
                self.cuphead.process_parry(is_air_parry=True)

                # ДЭШ
        if (
                key == arcade.key.X
                and not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and not self.cuphead.parry  # Нельзя делать дэш во время паррирования
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
                and not self.cuphead.parry  # Нельзя flex во время паррирования
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
                and not self.cuphead.parry  # Нельзя использовать супер во время паррирования
        ):
            self.cuphead.ex_straight = True
            self.cuphead.ex_meter = 0  # Сбрасываем шкалу
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
                and not self.cuphead.parry  # Можно стрелять во время паррирования
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
        # Если капхед умер или отключен ввод, игнорируем отпускания клавиш
        if self.cuphead.death or self.cuphead.disable_input:
            return

        if (
                self.loose
                or self.victory
                or self.cuphead.flexing
                or self.cuphead.ex_straight
                or self.cuphead.hit  # Не обрабатываем ввод во время получения урона
        ):
            return

        if key == arcade.key.LEFT:
            self.cuphead.keys_pressed["left"] = False
            # Если отпустили LEFT и не нажата правая кнопка, останавливаем движение
            if (
                    not self.cuphead.keys_pressed["right"]
                    and not self.cuphead.dashing
                    and not self.cuphead.dashing_back
                    and not self.cuphead.parry  # Учитываем паррирование
            ):
                self.cuphead.change_x = 0
                self.cuphead.moving = False

        elif key == arcade.key.RIGHT:
            self.cuphead.keys_pressed["right"] = False
            # Если отпустили RIGHT и не нажата левая кнопка, останавливаем движение
            if (
                    not self.cuphead.keys_pressed["left"]
                    and not self.cuphead.dashing
                    and not self.cuphead.dashing_back
                    and not self.cuphead.parry  # Учитываем паррирование
            ):
                self.cuphead.change_x = 0
                self.cuphead.moving = False

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
                    and not self.cuphead.parry  # Учитываем паррирование
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
                else:
                    self.cuphead.change_x = 0
                    self.cuphead.moving = False

        if (
                not self.cuphead.dashing
                and not self.cuphead.dashing_back
                and not self.cuphead.duck
                and not self.cuphead.flexing
                and not self.cuphead.ex_straight
                and not self.cuphead.parry  # Учитываем паррирование
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