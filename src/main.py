import arcade
from src.game.views.game_view import GameView


def main():
    window = arcade.Window(1280, 720, "Cuphead")
    window.show_view(GameView())
    arcade.run()


if __name__ == "__main__":
    main()
