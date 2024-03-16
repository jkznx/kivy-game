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
from kivy.uix.asyncimage import AsyncImage
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

blue_sky = (115, 215, 255)
sunset_color = (255, 165, 0)
green_grass = (86, 125, 70)
black = (0, 0, 0)
white = (255, 255, 255)


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
    def __init__(self, x=350, y=0):
        super().__init__()
        self.source = "./images/car.png"
        self.size_hint = (None, None)
        self.size = (300, 300)  # Adjusted size
        self.pos = (x, y)


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

        self.bird = AsyncImage(source="./images/bird.gif", size=(100, 100))
        self.add_widget(self.bird)

        # Add hearts
        self.hearts = []
        for i in range(3):
            heart = Image(source="./images/pixel_heart.png", size=(50, 50))
            heart.pos = (self.width - (i + 1) * 80, self.height/2 + 600)
            self.add_widget(heart)
            self.hearts.append(heart)
        

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

        self.time_label = Label(
            text="Time: 0",
            font_size="20sp",
            font_name="./fonts/pixel_font.ttf",
            pos=(20, self.height - 40),  # Adjust position as needed
            color=(1, 1, 1, 1),  # White color
        )
        self.add_widget(self.time_label)

        # Score label
        self.score = 0
        self.score_label = Label(
            text="Score: 0",
            font_size="20sp",
            font_name="./fonts/pixel_font.ttf",
            pos=(self.width - 120, self.height - 40),  # Adjust position as needed
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
            self.score += 10  # Increase score by 10 every second
            if self.score > 9999:
                self.score = 9999  # Limit score to 9999
            self.score_label.text = f"Score: {self.score}"  # Update score

    def update_road_position(self, dt):
        # Update road position
        self.road_pos_y += 2  # Adjust speed here
        if self.road_pos_y > self.height * 0.8 - 900:
            self.road_pos_y = self.height / 2.0 - 375  # Reset when it moves out of view
        self.dash_offset += 10  # Adjust speed here for the dash line
        if self.dash_offset > 120:
            self.dash_offset =  60 # Reset dash offset when it reaches the dash length
        self.draw_my_stuff()

    def move_car(self, dt):
        cur_x = self.car.x
        cur_y = self.car.y

        step = self.car_speed * dt

        max_left = 350 - 300
        max_right = 350 + 300

        if "a" in self.pressed_keys and cur_x > max_left:
            cur_x -= step
            print("a")
        if "d" in self.pressed_keys and cur_x < max_right:
            cur_x += step
            print("d")

        self.car.pos = (cur_x, cur_y)

        print(self.car.pos)

    def draw_my_stuff(self, *args):
        self.canvas.clear()
        with self.canvas:
            # draw sky
            Color(*[component / 255 for component in blue_sky])
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            # cloud on sky
            cloud_group_positions = [
                (self.width * 0.2, self.height * 0.85),
                (self.width * 0.5, self.height * 0.88),
                (self.width * 0.8, self.height * 0.9),
            ]

            for cloud_pos_x, cloud_pos_y in cloud_group_positions:
                for _ in range(30):
                    cloud_size = randint(30, 120)
                    cloud_color = white

                    Color(*[component / 255 for component in cloud_color])
                    Ellipse(
                        pos=(cloud_pos_x, cloud_pos_y), size=(cloud_size, cloud_size)
                    )
                    cloud_pos_x += randint(-30, 30)
                    cloud_pos_y += randint(-10, 10)

            # add sunset at the center of bottom sky
            Color(*[component / 255 for component in sunset_color])
            Ellipse(pos=(self.width / 2 - 75, self.height * 0.7), size=(150, 150))

            # draw grass
            Color(*[component / 255 for component in green_grass])
            Rectangle(pos=(0, 0), size=(self.width, self.height * 0.8))

            # pov road bottom triangle
            Color(*[component / 255 for component in black])
            Triangle(
                points=[
                    0,
                    0,
                    self.width / 2,
                    0,
                    self.width / 4 + 50,
                    self.height * 0.8,
                ]
            )
            Triangle(
                points=[
                    self.width,
                    0,
                    self.width / 2,
                    0,
                    self.width * 3 / 4 - 50,
                    self.height * 0.8,
                ]
            )

            # draw road
            Color(*[component / 255 for component in black])
            Rectangle(
                pos=(self.width / 2.0 - 200, self.road_pos_y),
                size=(400, self.height * 0.8),
            )  # -200 from half of 400 rect make it center

            # Draw center line
            Color(1, 1, 1)
            dash_length = 100
            gap_length = 300
            Line(
                points=[self.width / 2.0, -100, self.width / 2.0, self.height * 0.8],
                dash_length=dash_length,
                dash_offset=self.dash_offset,
            )

            # draw bird
            self.bird.pos = (self.width / 2 - 200, self.height * 0.85)
            Rectangle(texture=self.bird.texture, pos=self.bird.pos, size=self.bird.size)

            # Draw hearts
            for heart in self.hearts:
                Rectangle(texture=heart.texture, pos=heart.pos, size=heart.size)

        self.car = Car(self.car.x, self.car.y)
        self.add_widget(self.car)

        # Draw time label
        self.time_label = Label(
            text=self.time_label.text,
            font_size="20sp",
            font_name="./fonts/pixel_font.ttf",
            pos=(20, self.height/2 - 40),
            color=(1, 1, 1, 1),  # White color
        )
        self.add_widget(self.time_label)

        # Draw score label
        self.score_label = Label(
            text=self.score_label.text,
            font_size="20sp",
            font_name="./fonts/pixel_font.ttf",
            pos=(self.width - 120, self.height/2 - 40),
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
            Clock.schedule_interval(self.update_road_position, 1 / 30)
            Clock.schedule_interval(self.move_car, 1 / 30)
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
