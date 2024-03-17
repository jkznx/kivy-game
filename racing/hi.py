from kivy.config import Config
# Fixed screen size
SCREEN_W = 1440
SCREEN_H = 800

# Disable resizing
Config.set("graphics", "resizable", False)

# Set fixed window size
Config.set("graphics", "width", str(SCREEN_W))
Config.set("graphics", "height", str(SCREEN_H))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color, Ellipse, Triangle, Line
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock
from random import randint



STATE_INIT = 1
STATE_RESTART = 2
STATE_PLAY = 3
STATE_GAMEOVER = 4

blue_sky = (115, 215, 255)
sunset_color = (255, 165, 0)
green_grass = (86, 125, 70)
black = (0, 0, 0)
white = (255, 255, 255)

cloud_group_positions = [(300, 800), (1200, 850), (600, 750)]


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
            font_size=int(60 * min(SCREEN_W / 1440, SCREEN_H / 800)),
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Add buttons for difficulty selection
        button_size = (
            150 * min(SCREEN_W / 1440, SCREEN_H / 800),
            50 * min(SCREEN_W / 1440, SCREEN_H / 800),
        )
        easy_button = Button(
            text="Easy",
            size_hint=(None, None),
            size=button_size,
            pos_hint={"center_x": 0.25, "center_y": 0.5},
            on_press=lambda x: self.set_difficulty("easy"),
        )
        normal_button = Button(
            text="Normal",
            size_hint=(None, None),
            size=button_size,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            on_press=lambda x: self.set_difficulty("normal"),
        )
        hard_button = Button(
            text="Hard",
            size_hint=(None, None),
            size=button_size,
            pos_hint={"center_x": 0.75, "center_y": 0.5},
            on_press=lambda x: self.set_difficulty("hard"),
        )


        layout.add_widget(easy_button)
        layout.add_widget(normal_button)
        layout.add_widget(hard_button)

        self.add_widget(layout)

        self.game_widget = GameWidget()  # Initialize without specifying difficulty
        self.add_widget(self.game_widget)

    def set_difficulty(self, difficulty):
        # Set the game difficulty
        self.game_widget.difficulty = difficulty


class Car(Image):
    def __init__(self, x=SCREEN_W / 2 - 150 * min(SCREEN_W / 1440, SCREEN_H / 800), y=0):
        super().__init__()
        self.source = "./images/car.png"
        self.size_hint = (None, None)
        self.size = (
            500 * min(SCREEN_W / 1440, SCREEN_H / 800),
            500 * min(SCREEN_W / 1440, SCREEN_H / 800),
        )  # Adjusted size
        self.pos = (x, y)


class GameWidget(Widget):
    car_speed = NumericProperty(200)
    is_paused = False

    def __init__(self, difficulty="easy", **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw_my_stuff)
        self.bind(size=self.draw_my_stuff)
        self.difficulty = difficulty  # Assign the difficulty parameter here
        self.road_pos_y = self.height / 2 - 300 * min(SCREEN_W / 1440, SCREEN_H / 800)
        self.dash_offset = 0
        self.car = Car()
        self.add_widget(self.car)

        self.bird = Image(
            source="./images/bird.gif",
            size=(
                300 * min(SCREEN_W / 1440, SCREEN_H / 800),
                300 * min(SCREEN_W / 1440, SCREEN_H / 800),
            ),
        )
        self.add_widget(self.bird)

        # Add hearts
        self.hearts = []
        heart_y = self.height / 2 + 600 * min(SCREEN_W / 1440, SCREEN_H / 800)  # Set y-coordinate for all hearts
        for i in range(3):
            heart = Image(
                source="./images/pixel_heart.png",
                size=(
                    75 * min(SCREEN_W / 1440, SCREEN_H / 800),
                    75 * min(SCREEN_W / 1440, SCREEN_H / 800),
                ),
            )
            heart.pos = (
                self.width / 2 + 50 - (i) * 25 * min(SCREEN_W / 1440, SCREEN_H / 800),
                heart_y,
            )
            self.add_widget(heart)
            self.hearts.append(heart)

        # Pause label
        self.pause_label = Label(
            text="Paused",
            font_size=int(50 * min(SCREEN_W / 1440, SCREEN_H / 800)),
            font_name="./fonts/pixel_font.ttf",
            pos=(self.width / 2, self.height / 2),
            color=(1, 1, 1, 1),  # White color
            opacity=0,  # Initially hidden
        )
        self.add_widget(self.pause_label)

        self.time_label = Label(
            text="Time: 0",
            font_size=int(50 * min(SCREEN_W / 1440, SCREEN_H / 800)),
            font_name="./fonts/pixel_font.ttf",
            pos=(20, self.height - 40),  # Adjust position as needed
            color=(1, 1, 1, 1),  # White color
        )
        self.add_widget(self.time_label)

        # Score label
        self.score = 0
        self.score_label = Label(
            text="Score: 0",
            font_size=int(50 * min(SCREEN_W / 1440, SCREEN_H / 800)),
            font_name="./fonts/pixel_font.ttf",
            pos=(
                self.width - 120 * min(SCREEN_W / 1440, SCREEN_H / 800),
                self.height - 40,
            ),  # Adjust position as needed
            color=(1, 1, 1, 1),  # White color
        )
        self.add_widget(self.score_label)

        Clock.schedule_interval(self.update_time_and_score, 1)
        Clock.schedule_interval(self.update_road_position, 1 / 30)
        Clock.schedule_interval(self.move_car, 1 / 30)

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self.pressed_keys = set()

        # init enemies
        self.enemies = []

        # draw sky, clouds, sunset, grass, road, and center line
        self.draw_my_stuff()

    def update_time_and_score(self, dt):
        if not self.is_paused:
            self.time_label.text = f"Time: {int(self.time_label.text.split(': ')[-1]) + 1}"  # Update time
            if self.difficulty == "easy":
                self.score += 10  # Increase score by 10 every second
            elif self.difficulty == "normal":
                self.score += 20  # Increase score by 20 every second
            elif self.difficulty == "hard":
                self.score += 30  # Increase score by 30 every second

            if self.score > 9999:
                self.score = 9999  # Limit score to 9999
            self.score_label.text = f"Score: {self.score}"  # Update score

    def update_road_position(self, dt):
        # Update road position
        self.road_pos_y += 30 * min(SCREEN_W / 1440, SCREEN_H / 800)  # Adjust speed here
        if (
            self.road_pos_y
            > self.height * 0.8 - 900 * min(SCREEN_W / 1440, SCREEN_H / 800)
        ):
            self.road_pos_y = self.height / 2.0 - 375 * min(
                SCREEN_W / 1440, SCREEN_H / 800
            )
        self.dash_offset += 10 * min(SCREEN_W / 1440, SCREEN_H / 800)
        if self.dash_offset > 120 * min(SCREEN_W / 1440, SCREEN_H / 800):
            self.dash_offset = 60 * min(SCREEN_W / 1440, SCREEN_H / 800)
        self.draw_my_stuff()

    def move_car(self, dt):
        cur_x = self.car.x
        cur_y = self.car.y

        step = self.car_speed * dt

        max_left = SCREEN_W / 2 - 500 * min(SCREEN_W / 1440, SCREEN_H / 800)
        max_right = SCREEN_W / 2 + 500 * min(SCREEN_W / 1440, SCREEN_H / 800)

        if "a" in self.pressed_keys and cur_x > max_left:
            cur_x -= step
        if "d" in self.pressed_keys and cur_x < max_right:
            cur_x += step

        self.car.pos = (cur_x, cur_y)

    def draw_my_stuff(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Draw sky
            Color(*[component / 255 for component in blue_sky])
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            # Draw clouds
            for cloud_pos_x, cloud_pos_y in cloud_group_positions:
                for _ in range(30):
                    cloud_size = randint(30, 120) * min(SCREEN_W / 1440, SCREEN_H / 800)
                    cloud_color = white

                    Color(*[component / 255 for component in cloud_color])
                    Ellipse(
                        pos=(cloud_pos_x, cloud_pos_y), size=(cloud_size, cloud_size)
                    )
                    cloud_pos_x += randint(-30, 30) * min(SCREEN_W / 1440, SCREEN_H / 800)
                    cloud_pos_y += randint(-10, 10) * min(SCREEN_W / 1440, SCREEN_H / 800)

            # Draw sunset
            Color(*[component / 255 for component in sunset_color])
            Ellipse(
                pos=(self.width / 2 - 125, self.height * 0.7),
                size=(
                    250 * min(SCREEN_W / 1440, SCREEN_H / 800),
                    250 * min(SCREEN_W / 1440, SCREEN_H / 800),
                ),
            )

            # Draw grass
            Color(*[component / 255 for component in green_grass])
            Rectangle(pos=(0, 0), size=(self.width, self.height * 0.8))

            # Draw road triangles
            Color(*[component / 255 for component in black])
            Triangle(
                points=[
                    0,
                    0,
                    self.width / 2,
                    0,
                    self.width / 4
                    + 50 * min(SCREEN_W / 1440, SCREEN_H / 800),
                    self.height * 0.8,
                ]
            )
            Triangle(
                points=[
                    self.width,
                    0,
                    self.width / 2,
                    0,
                    self.width * 3 / 4
                    - 50 * min(SCREEN_W / 1440, SCREEN_H / 800),
                    self.height * 0.8,
                ]
            )

            # Draw road
            road_width = 800 * min(SCREEN_W / 1440, SCREEN_H / 800)
            road_height = min(
                self.height * 0.8,
                self.road_pos_y
                + 900 * min(SCREEN_W / 1440, SCREEN_H / 800),
            )
            road_pos_x = self.width / 2 - road_width / 2  # Center the road
            Color(*[component / 255 for component in black])
            Rectangle(
                pos=(road_pos_x, 0),
                size=(road_width, road_height),
            )

            # Draw center line
            Color(1, 1, 1)
            dash_length = 100 * min(SCREEN_W / 1440, SCREEN_H / 800)
            gap_length = 300 * min(SCREEN_W / 1440, SCREEN_H / 800)
            Line(
                points=[
                    self.width / 2.0,
                    -100,
                    self.width / 2.0,
                    self.height * 0.8,
                ],
                dash_length=dash_length,
                dash_offset=self.dash_offset,
            )

            # Draw bird
            self.bird.pos = (
                self.width / 2 + 450 * min(SCREEN_W / 1440, SCREEN_H / 800),
                self.height * 0.75,
            )
            Rectangle(
                texture=self.bird.texture,
                pos=self.bird.pos,
                size=self.bird.size,
            )

            # Draw hearts
            for heart in self.hearts:
                Rectangle(
                    texture=heart.texture, pos=heart.pos, size=heart.size
                )
        
        self.car = Car(self.car.x, self.car.y)
        self.add_widget(self.car)

        # Draw time label
        self.time_label = Label(
            text=self.time_label.text,
            font_size=int(50 * min(SCREEN_W / 1440, SCREEN_H / 800)),
            font_name="./fonts/pixel_font.ttf",
            pos=(
                75 * min(SCREEN_W / 1440, SCREEN_H / 800),
                self.height / 2 - 40 * min(SCREEN_W / 1440, SCREEN_H / 800),
            ),
            color=(1, 1, 1, 1),  # White color
        )
        self.add_widget(self.time_label)

        # Draw score label
        self.score_label = Label(
            text=self.score_label.text,
            font_size=int(50 * min(SCREEN_W / 1440, SCREEN_H / 800)),
            font_name="./fonts/pixel_font.ttf",
            pos=(
                self.width - 200 * min(SCREEN_W / 1440, SCREEN_H / 800),
                self.height / 2 - 40 * min(SCREEN_W / 1440, SCREEN_H / 800),
            ),
            color=(1, 1, 1, 1),  # White color
        )
        self.add_widget(self.score_label)

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
            Clock.unschedule(self.update_road_position)
            Clock.unschedule(self.move_car)
            self.pause_label.opacity = 1
        else:
            Clock.schedule_interval(
                self.update_road_position, 1 / 30
            )
            Clock.schedule_interval(self.move_car, 1 / 30)
            self.pause_label.opacity = 0

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]

        if text in self.pressed_keys:
            self.pressed_keys.remove(text)

        if text == "r":
            self.reset_game()

    def reset_game(self):
        self.time_label.text = "Time: 0"
        self.score = 0
        self.score_label.text = "Score: 0"
        self.road_pos_y = self.height / 2 - 300 * min(
            SCREEN_W / 1440, SCREEN_H / 800
        )
        self.car.pos = (
            SCREEN_W / 2 - 150 * min(SCREEN_W / 1440, SCREEN_H / 800),
            0,
        )
        self.enemies = []
        self.draw_my_stuff()


class ChocoboRacingApp(App):
    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        start_screen = StartScreen(name="start")
        game_screen = GameScreen(name="game")

        sm.add_widget(start_screen)
        sm.add_widget(game_screen)
        return sm


if __name__ == "__main__":
    ChocoboRacingApp().run()
