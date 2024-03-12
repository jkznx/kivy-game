from kivy.config import Config

SCREEN_W = 1440
SCREEN_H = 800
RESIZE_ENABLE = False
Config.set("graphics", "resizable", RESIZE_ENABLE)
Config.set("graphics", "width", str(SCREEN_W))
Config.set("graphics", "height", str(SCREEN_H))

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from random import choice

SCREEN_CX = SCREEN_W / 2
SCREEN_CY = SCREEN_H / 2

STATE_INIT = 1
STATE_RESTART = 2
STATE_PLAY = 3
STATE_GAMEOVER = 4

state = STATE_INIT


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Start Background image
        with self.canvas:
            self.bg = Rectangle(
                source="./images/game_start.png", pos=(0, 0), size=Window.size
            )
        # Game Title
        game_title = Label(
            text="Chocobo Racing",
            font_size="60sp",
            font_name="./fonts/pixel_font.ttf",
            pos_hint={"center_x": 0.5, "top": 1.35},
        )

        # Add start button
        start_button = Button(
            text="Start Game",
            font_name="./fonts/pixel_font.ttf",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.4, "y": 0.1},  # start_Btn pos
            background_color=(0, 0, 0, 1),  # black button
        )
        start_button.bind(on_press=self.start_game)
        layout.add_widget(game_title)
        layout.add_widget(start_button)
        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.current = "game"


class GameScreen(Screen):
    pass


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)

        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self.pressed_keys = set()
        Clock.schedule_interval(self.move_step, 0)

        # Initialize the enemy car
        self.enemy = Rectangle(
            pos=(choice([700, 1000]), 0), size=(300, 300), source="./images/car_2.png"
        )

        with self.canvas:
            self.bg = Rectangle(
                source="./images/racing_bg_3.png", pos=(0, 0), size=Window.size
            )
            self.hero = Rectangle(
                pos=(600, 0), size=(300, 300), source=("./images/car.png")
            )

    def spawn_enemy(self, dt):
        enemy = Rectangle(
            pos=(choice([700, 1000]), 0), size=(300, 300), source="./images/car_2.png"
        )
        self.enemies.append(enemy)
        self.add_widget(enemy)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.pressed_keys.add(text)

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]

        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

    def move_step(self, dt):
        cur_x = self.hero.pos[0]
        cur_y = self.hero.pos[1]

        step = 200 * dt

        if "a" in self.pressed_keys and cur_x > 540:
            cur_x -= step
        if "d" in self.pressed_keys and cur_x < 1100:
            cur_x += step

        self.hero.pos = (cur_x, cur_y)

        for enemy in self.enemies:
            enemy_cur_y = enemy.pos[1]
            enemy_step = 300 * dt
            enemy.pos = (enemy.pos[0], enemy_cur_y + enemy_step)

            if enemy_cur_y > SCREEN_H:
                self.remove_widget(enemy)
                self.enemies.remove(enemy)


class Chocobo_Racing(App):
    def build(self):
        screen_manager = ScreenManager()
        start_screen = StartScreen(name="start")
        game_screen = GameScreen(name="game")
        game_widget = GameWidget()

        screen_manager.add_widget(start_screen)
        screen_manager.add_widget(game_screen)
        game_screen.add_widget(game_widget)

        return screen_manager


if __name__ == "__main__":
    app = Chocobo_Racing()
    app.run()
