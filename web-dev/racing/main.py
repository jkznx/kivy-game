from kivy.config import Config
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Ellipse, Triangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.properties import NumericProperty
from random import randint

# Fixed screen size
SCREEN_W = 1440
SCREEN_H = 800

# Disable resizing
Config.set("graphics", "resizable", False)

# Set fixed window size
Config.set("graphics", "width", str(SCREEN_W))
Config.set("graphics", "height", str(SCREEN_H))

STATE_INIT = 1
STATE_RESTART = 2
STATE_PLAY = 3
STATE_GAMEOVER = 4


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


class Car(Image):
    pass


class GameWidget(Widget):
    car_speed = NumericProperty(200)
    is_paused = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw_my_stuff)
        self.bind(size=self.draw_my_stuff)
        self.road_pos_y = self.height / 2 - 300
        self.dash_offset = 0
        self.car = Car()
        self.add_widget(self.car)

        # Pause label
        self.pause_label = Label(
            text="Paused",
            font_size="50sp",
            font_name="./fonts/pixel_font.ttf",
            pos=(self.width / 2, self.height / 2),
            color=(1, 1, 1, 1),  # White color
            opacity=0,  # Initially hidden
        )
        self.add_widget(self.pause_label)

        # Car speed progress bar
        self.speed_bar = ProgressBar(
            max=400,  # Maximum speed
            value=self.car_speed,  # Initial speed
            size_hint=(None, None),
            width=300,
            height=20,
            pos=(self.width - 350, 20),  # Position on bottom right
        )
        self.add_widget(self.speed_bar)

        Clock.schedule_interval(self.move_car, 1 / 30)

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self.pressed_keys = set()

    def move_car(self, dt):
        step = self.car_speed * dt

        # Calculate the new car position based on the keys pressed
        max_left = self.width / 2.0 - 500
        max_right = self.width / 2.0 + 500

        # Move the car to the left
        if "a" in self.pressed_keys and self.car.x > max_left:
            self.car.x -= step

        # Move the car to the right
        if "d" in self.pressed_keys and self.car.x < max_right:
            self.car.x += step

        # Ensure the car stays within bounds
        self.car.x = max(max_left, min(self.car.x, max_right))

    def draw_my_stuff(self, *args):
        pass

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if text == "p":
            self.toggle_pause()
        else:
            self.pressed_keys.add(text)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_label.opacity = 1
        else:
            self.pause_label.opacity = 0

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]

        if text in self.pressed_keys:
            self.pressed_keys.remove(text)


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
