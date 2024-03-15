from kivy.config import Config

SCREEN_W = 1000
SCREEN_H = 700
RESIZE_ENABLE = False

Config.set("graphics", "resizable", RESIZE_ENABLE)
Config.set("graphics", "width", str(SCREEN_W))
Config.set("graphics", "height", str(SCREEN_H))

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Line, Quad, Triangle
from kivy.properties import NumericProperty
from kivy.core.image import Image as Im
from kivy.uix.image import Image
from random import randint

texture = Im("./images/road.jpg").texture
SCREEN_CX = SCREEN_W / 2
SCREEN_CY = SCREEN_H / 2

# STATE game
STATE_INIT = 1
STATE_PLAY = 2
STATE_RESTART = 3
STATE_GAMEOVER = 4

STATE_CURRENT = STATE_INIT


def switch_screen():
    global STATE_CURRENT
    if STATE_CURRENT == STATE_INIT:
        screen_manager.current = "start"
    if STATE_CURRENT == STATE_PLAY:
        screen_manager.current = "play"
    if STATE_CURRENT == STATE_RESTART:
        screen_manager.current = "stop"
    if STATE_CURRENT == STATE_GAMEOVER:
        screen_manager.current = "over"


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
        global STATE_CURRENT
        STATE_CURRENT = STATE_PLAY
        switch_screen()


class GameScreen(Screen):
    pass


class StopScreen(Screen):
    pass


class OverScreen(Screen):
    pass


class Car(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "./images/car.png"
        self.size = (300, 300)  # Adjusted size


class GameWidget(Widget):
    # keyboard input
    # from user_actions import _on_key_down, _on_key_up, _on_keyboard_closed

    # view
    from tranforms import transform, transform_2D, transform_perspective

    pause_text = "p for pause"

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 6
    V_LINES_SPACING = 0.4  # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = 0.1  # percentage in screen height
    horizontal_lines = []

    DRIVING_SPEED = 1.2
    current_offset_y = 0
    current_y_loop = 0

    CAR_MOVE_SPEED = 3.0
    current_direction_car = 0
    current_offset_x = 0

    number_segment = 10
    floors = []
    floors_coordinates = []

    car = None
    car_coordinates = [(0, 0), (0, 0), (0, 0)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_floors()
        self.generate_floors_coordinates()
        self.init_car()
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        with self.canvas.before:
            # self.bg = Rectangle(
            #     size=Window.size,
            #     source="./images/racing_bg_3.png",
            #     pos=(0, 0),
            # )
            # draw sky
            Color(*[component / 255 for component in blue_sky])
            Rectangle(pos=(0, 0), size=(Window.size))

            # cloud on sky
            cloud_group_positions = [
                (Window.size[0] * 0.2, Window.size[1] * 0.85),
                (Window.size[0] * 0.5, Window.size[1] * 0.88),
                (Window.size[0] * 0.8, Window.size[1] * 0.9),
            ]

            for cloud_pos_x, cloud_pos_y in cloud_group_positions:
                for _ in range(30):
                    cloud_size = randint(30, 120)
                    cloud_color = white

                    Color(*[component / 255 for component in cloud_color])
                    self.clound = Ellipse(
                        pos=(cloud_pos_x, cloud_pos_y), size=(cloud_size, cloud_size)
                    )
                    cloud_pos_x += randint(-30, 30)
                    cloud_pos_y += randint(-10, 10)

            # add sunset at the center of bottom sky
            # Color(*[component / 255 for component in sunset_color])
            # Ellipse(
            #     pos=(Window.size[0] / 2 - 75, Window.size[1] * 0.7), size=(150, 150)
            # )

            # draw grass
            Color(*[component / 255 for component in green_grass])
            Rectangle(
                pos=(0, 0),
                size=(Window.size[0], Window.size[1] * 0.35 + 3),
            )
            self.pause = Label(
                text=self.pause_text,
                font_size="30sp",
                font_name="./fonts/pixel_font.ttf",
                pos=(600, 600),
            )
        self.game_running = Clock.schedule_interval(self.update, 1 / 30)

    # keyboard
    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if "a" in keycode[1]:
            self.current_direction_car = self.CAR_MOVE_SPEED
        elif "d" in keycode[1]:
            self.current_direction_car = -self.CAR_MOVE_SPEED
        elif "p" in keycode[1]:
            global STATE_CURRENT
            if STATE_CURRENT == STATE_RESTART:
                self.pause_text = "p for pause"
                STATE_CURRENT = STATE_PLAY
                switch_screen()
                self.game_running = Clock.schedule_interval(self.update, 1 / 30)
            elif STATE_CURRENT == STATE_PLAY:
                self.pause_text = "p for resume"
                STATE_CURRENT = STATE_RESTART
                switch_screen()
                Clock.unschedule(self.game_running)
            print("stop", self.pause_text)

    def _on_key_up(self, keyboard, keycode):
        self.current_direction_car = 0

    # car
    def init_car(self):
        with self.canvas:
            self.car = Car()

    def update_car(self):
        self.car.pos = [SCREEN_CX, 6]

    # get line x
    # |     /\    |         \
    # |   /   \  |           \
    # |_/______\_| Ex.in 3D   \ <-
    def get_line_x_from_index(self, index):

        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + (offset * spacing) + self.current_offset_x
        print(index, line_x)
        return line_x

    # get line y
    # |     /_\    |
    # |   /____\  |
    # |_/_______\_|     ____ <-
    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = (index * spacing_y) - self.current_offset_y
        return line_y

    # tile
    def init_floors(self):
        with self.canvas:
            for i in range(0, self.number_segment):
                self.floors.append(Quad(texture=texture))

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def generate_floors_coordinates(self):
        last_x = 0
        last_y = 0

        for i in range(len(self.floors_coordinates) - 1, -1, -1):
            if self.floors_coordinates[i][1] < self.current_y_loop:
                del self.floors_coordinates[i]

        if len(self.floors_coordinates) > 0:
            last_coordinates = self.floors_coordinates[-1]
            last_y = last_coordinates[1] + 1

        for i in range(len(self.floors_coordinates), self.number_segment):
            self.floors_coordinates.append((0, last_y))
            last_y += 1

    def update_floors(self):
        start_index = -int(self.V_NB_LINES / 2) + 1

        for i in range(0, self.number_segment):
            tile = self.floors[i]
            tile_coordinates = self.floors_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(start_index, tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(
                start_index + self.V_NB_LINES - 1, tile_coordinates[1] + 1
            )
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    # line
    def init_vertical_lines(self):
        with self.canvas:
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        # -1 0 1 2
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    # seg
    def init_horizontal_lines(self):
        with self.canvas:
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    # main update
    def update(self, dt):
        if STATE_CURRENT == STATE_INIT:
            return
        time_factor = dt * 30
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_floors()
        self.update_car()
        speed_y = self.DRIVING_SPEED * self.height / 100
        self.current_offset_y += speed_y * time_factor

        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1
            self.generate_floors_coordinates()
            print("loop : " + str(self.current_y_loop))

        speed_x = self.current_direction_car * self.width / 100
        # print(self.current_offset_x, speed_x)
        self.current_offset_x += speed_x * time_factor


class Chocobo_RacingApp(App):
    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        start_screen = StartScreen(name="start")
        game_screen = GameScreen(name="play")
        stop_screen = StopScreen(name="stop")
        over_screen = OverScreen(name="over")

        game_widget = GameWidget()
        game_screen.add_widget(game_widget)

        screen_manager.add_widget(start_screen)
        screen_manager.add_widget(game_screen)
        screen_manager.add_widget(stop_screen)
        screen_manager.add_widget(over_screen)

        return screen_manager


if __name__ == "__main__":
    Chocobo_RacingApp().run()
