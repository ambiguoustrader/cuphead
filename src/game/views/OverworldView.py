from __future__ import annotations

from pathlib import Path

import arcade


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Cuphead Overworld"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = PROJECT_ROOT / "assets" / "maps" / "overworld.tmx"

PLAYER_SPEED = 250


class OverworldView(arcade.View):
    def __init__(self):
        super().__init__()

        self.pressed_keys: set[int] = set()

        self.tile_map = arcade.load_tilemap(
            MAP_PATH,
            scaling=1.0,
            use_spatial_hash=True,
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.player = arcade.SpriteSolidColor(32, 32, arcade.color.YELLOW)
        self.player.center_x = 100
        self.player.center_y = 100
        self.scene.add_sprite("Player", self.player)

        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.walls = self.get_walls()
        self.physics_engine = self.create_physics_engine()

    def get_walls(self):
        if "Walls" not in self.scene.name_mapping:
            return None
        return self.scene.get_sprite_list("Walls")

    def create_physics_engine(self):
        if self.walls is None:
            return None
        return arcade.PhysicsEngineSimple(self.player, self.walls)

    def on_key_press(self, key, modifiers):
        self.pressed_keys.add(key)

    def on_key_release(self, key, modifiers):
        self.pressed_keys.discard(key)

    def on_update(self, delta_time):
        dx, dy = self.calc_move_vector()

        self.player.change_x = dx * delta_time
        self.player.change_y = dy * delta_time

        if self.physics_engine:
            self.physics_engine.update()
        else:
            self.player.center_x += self.player.change_x
            self.player.center_y += self.player.change_y

        self.update_camera()

    def calc_move_vector(self):
        dx = 0
        dy = 0

        if arcade.key.LEFT in self.pressed_keys:
            dx -= PLAYER_SPEED
        if arcade.key.RIGHT in self.pressed_keys:
            dx += PLAYER_SPEED
        if arcade.key.UP in self.pressed_keys:
            dy += PLAYER_SPEED
        if arcade.key.DOWN in self.pressed_keys:
            dy -= PLAYER_SPEED

        return dx, dy

    def update_camera(self):
        target = (
            self.player.center_x - SCREEN_WIDTH // 2,
            self.player.center_y - SCREEN_HEIGHT // 2,
        )
        self.camera.move_to(target)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(OverworldView())
    arcade.run()


if __name__ == "__main__":
    main()