from kivy.config import Config

SCREEN_W = 764
SCREEN_H = 640
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

SCREEN_CX = SCREEN_W / 2
SCREEN_CY = SCREEN_H / 2

"""
def collides(rect1, rect2):
    r1x = rect1[0][0]
    r1y = rect1[0][1]
    r2x = rect2[0][0]
    r2y = rect2[0][1]
    r1w = rect1[1][0]
    r1h = rect1[1][1]
    r2w = rect2[1][0]
    r2h = rect2[1][1]

    if (r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y):
        return True
    else:
        return False
"""


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
        print(self)

    def start_game(self, instance):
        self.manager.current = "game"


class GameScreen(Screen):
    pass


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.STATE_INIT = 1
        self.STATE_RESTART = 2
        self.STATE_PLAY = 3
        self.STATE_GAMEOVER = 4

        self.state = self.STATE_INIT

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)

        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self.pressed_keys = set()
        Clock.schedule_interval(self.update, 1 / 30)

        with self.canvas:
            self.bg = Rectangle(
                source="./images/racing_bg_3.png", pos=(0, 0), size=Window.size
            )
            self.car = Rectangle(
                pos=(SCREEN_CX, 0), size=(200, 200), source=("./images/car.png")
            )

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        # print("down", text)
        self.pressed_keys.add(text)

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        # print("up", text)

        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

    def update(self, dt):
        cur_x = self.car.pos[0]
        cur_y = self.car.pos[1]

        step = (
            200 * dt
        )  # add step to add velocity #diff with 3.3 because this code can move in all rounder (3d move)

        if (
            "a" in self.pressed_keys and cur_x > 250
        ):  # can't move x in range (250,650) ==> street
            cur_x -= step
        if "d" in self.pressed_keys and cur_x < 650:
            cur_x += step

        self.car.pos = (cur_x, cur_y)

        """
        if "a" in self.pressed_keys:
            cur_x -= step
        if "d" in self.pressed_keys:
            cur_x += step

        #print(self.car.pos)

        # background animation moving
        self.bg.pos = (self.bg.pos[0] - 1, self.bg.pos[1])
        if self.bg.pos[0] <= -self.height:
            self.bg.pos = (0, self.bg.pos[1])
        if collides((self.car.pos, self.car.size),(self.enemy.pos, self.enemy.size)):
            print('game over!')
        else:
            print('not over')
        """

    def switch_state(self):
        if self.state == self.STATE_INIT:
            self.manager.current = "start"
        elif self.state == self.STATE_RESTART:
            self.manager.current = "game"
        elif self.state == self.STATE_PLAY:
            self.manager.current = "restart"
        elif self.state == self.STATE_GAMEOVER:
            self.manager.current = "over"


class Chocobo_Racing(App):
    def build(self):
        screen_manager = ScreenManager()

        start_screen = StartScreen(name="start")
        screen_manager.add_widget(start_screen)

        game_screen = GameScreen(name="game")
        screen_manager.add_widget(game_screen)

        game_widget = GameWidget()
        game_screen.add_widget(game_widget)

        return screen_manager


if __name__ == "__main__":
    app = Chocobo_Racing()
    app.run()
