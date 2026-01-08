from __future__ import annotations

from pathlib import Path

import arcade

from src.game.systems.controls import ControlsStorage


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        # управление
        self.controls_storage = ControlsStorage(Path("user_data/controls.json"))
        self.controls = self.controls_storage.load()
        self.pressed_keys: set[int] = set()

        # игрок (пример)
        self.player = arcade.SpriteSolidColor(40, 40, arcade.color.YELLOW)
        self.player.center_x = 200
        self.player.center_y = 200
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.speed = 260

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        # если управление меняли в меню — можно перечитать
        self.controls = self.controls_storage.load()

    def on_draw(self):
        self.clear()
        self.player_list.draw()

        arcade.draw_text(
            "WASD/стрелки (если настроите) | Esc - выход",
            10, 10, arcade.color.WHITE, 14
        )

    def on_key_press(self, symbol: int, modifiers: int):
        self.pressed_keys.add(symbol)

        if symbol in self.controls.bindings.get("pause", []):
            # Пока просто закрываем игру
            arcade.close_window()

    def on_key_release(self, symbol: int, modifiers: int):
        self.pressed_keys.discard(symbol)

    def on_update(self, delta_time: float):
        dx = 0
        dy = 0

        if self.controls.is_action_down("move_left", self.pressed_keys):
            dx -= self.speed
        if self.controls.is_action_down("move_right", self.pressed_keys):
            dx += self.speed
        if self.controls.is_action_down("move_up", self.pressed_keys):
            dy += self.speed
        if self.controls.is_action_down("move_down", self.pressed_keys):
            dy -= self.speed

        self.player.center_x += dx * delta_time
        self.player.center_y += dy * delta_time

        if self.controls.is_action_down("shoot", self.pressed_keys):
            pass