from kivy.config import Config

SCREEN_W = 1000
SCREEN_H = 700
RESIZE_ENABLE = True

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
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Line, Quad, Triangle
from kivy.properties import NumericProperty, StringProperty
from kivy.core.image import Image as Im
from kivy.uix.image import Image
from random import randint, randrange, choice
import math

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

        self.game_widget = GameWidget()
        self.add_widget(self.game_widget)

    def set_difficulty(self, difficulty_level):
        self.game_widget.difficulty_level = difficulty_level

class StopScreen(Screen):
    pass


class OverScreen(Screen):
    pass


class Car(Widget):

    def __init__(self):
        super(Car).__init__()
        # self.source = "./images/car.png"
        self.color = [0, 0, 1]
        self.size = (100, 100)  # Adjusted size


class GameWidget(Widget):
    # keyboard input
    # from user_actions import _on_key_down, _on_key_up, _on_keyboard_closed
    difficulty = StringProperty("easy")  # Default difficulty level
    score_increment = 10  # Default score increment value
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

    DRIVING_SPEED = 0.75
    current_offset_y = 0
    current_y_loop = 0

    CAR_MOVE_SPEED = 3.0
    current_direction_car = 0
    current_offset_x = 0

    number_segment = 10
    floors = []
    floors_coordinates = []

    car = None
    # left right
    car_coordinates = [(0, 0), (0, 0)]
    car_opacity = 1
    number_enemy = 10
    enemys = []
    enemys_coordinates = []

    car_hitbox = 0.1
    enemys_hitbox = 0.25

    HEART = 3
    Immortal = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.is_paused = False

        self.init_background()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_floors()
        self.generate_floors_coordinates()
        self.init_enemys()
        self.init_car()
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.game_running = Clock.schedule_interval(self.update, 1 / 30)

    def restart(self):
        Clock.unschedule(self.game_running)

        self.pause_text = "p for pause"
        self.HEART = 3
        self.Immortal = 0
        self.floors_coordinates = []
        for i in range(0, len(self.enemys)):
            self.canvas.remove(self.enemys[i])
        self.enemys = []
        self.enemys_coordinates = []

        self.current_direction_car = 0
        self.current_offset_x = 0
        self.current_offset_y = 0
        self.current_y_loop = 0

        self.DRIVING_SPEED = 0.3
        self.generate_floors_coordinates()
        self.game_running = Clock.schedule_interval(self.update, 1 / 30)

        self.time_label = Label(
            text="Time: 0",
            font_size=int(50 * min(SCREEN_W / 1440, SCREEN_H / 800)),
            font_name="./fonts/pixel_font.ttf",
            pos=(75, self.height/2 + 500),  # Adjust position as needed
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
                self.width/2 + 1450 * min(SCREEN_W / 1440, SCREEN_H / 800),
                self.height/2 + 500,
            ),  # Adjust position as needed
            color=(1, 1, 1, 1),  # White color
        )
        self.add_widget(self.score_label)

        Clock.schedule_interval(self.update_time_and_score, 1)

        # Add hearts
        self.hearts = []
        heart_y = self.height / 2 + 1000 * min(SCREEN_W / 1440, SCREEN_H / 800)  # Set y-coordinate for all hearts
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

    def set_difficulty(self, difficulty_level):
        self.difficulty = difficulty_level

        # Update score increment rate based on difficulty
        if self.difficulty == "easy":
            self.score += 10
        elif self.difficulty == "normal":
            self.score += 20
        elif self.difficulty == "hard":
            self.score += 30

    #time and score
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

    # keyboard
    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if "a" == keycode[1]:
            self.current_direction_car = -self.CAR_MOVE_SPEED
        elif "d" == keycode[1]:
            self.current_direction_car = self.CAR_MOVE_SPEED
        elif "w" == keycode[1]:
            self.DRIVING_SPEED += 0.01
        elif "s" == keycode[1]:
            self.DRIVING_SPEED -= 0.01
        elif "n" == keycode[1]:
            # wClock.unschedule(self.game_running)
            self.restart()
        elif "p" == keycode[1]:
            global STATE_CURRENT
            if STATE_CURRENT == STATE_RESTART:
                self.pause_text = "p for pause"
                STATE_CURRENT = STATE_PLAY
                # switch_screen()
                self.game_running = Clock.schedule_interval(self.update, 1 / 30)
            elif STATE_CURRENT == STATE_PLAY:
                self.pause_text = "p for resume"
                STATE_CURRENT = STATE_RESTART
                # switch_screen()
                Clock.unschedule(self.game_running)
            print("stop", self.pause_text)

    def _on_key_up(self, keyboard, keycode):
        self.current_direction_car = 0

    # background
    def init_background(self):
        with self.canvas.before:
            # self.bg = Rectangle(
            #     size=Window.size,
            #     source="./images/racing_bg_3.png",
            #     pos=(0, 0),
            # )
            # draw sky
            Color(*[component / 255 for component in blue_sky])
            self.sky = Rectangle(pos=(0, 0), size=(Window.size))

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
            self.im = Label(
                text=str(self.Immortal),
                font_size="30sp",
                font_name="./fonts/pixel_font.ttf",
                pos=(800, 500),
            )
            self.heart = Label(
                text=str(self.HEART),
                font_size="30sp",
                font_name="./fonts/pixel_font.ttf",
                pos=(800, 400),
            )

    def update_background(self): ...

    # car
    def init_car(self):
        with self.canvas:
            Color(1, 1, 1, self.car_opacity)
            self.car = Rectangle(
                fit_mode="cover",
                source="./images/car_cut.png",
            )

    def update_car(self):
        y_car = 6
        left_x = self.perspective_point_x - self.car.size[0] / 2
        right_x = self.perspective_point_x + self.car.size[0] / 2
        self.car_coordinates[0] = (left_x, y_car)
        self.car_coordinates[1] = (right_x, y_car)
        self.car.size = (self.width * 0.2, self.height * 0.18)
        self.car.pos = [left_x, y_car]

    def collision_car(self):
        for i in range(0, self.number_enemy):
            car = Widget(
                pos=self.car.pos,
                size=(self.car.size[0], self.car.size[1] * self.car_hitbox),
            )
            enemy = Widget(
                pos=self.enemys[i].pos,
                size=(
                    self.enemys[i].size[0],
                    self.enemys[i].size[1] * self.enemys_hitbox,
                ),
            )
            if car.collide_widget(enemy):
                return True
        return False

    # get x of line
    # |     /\    |         \
    # |   /   \  |           \
    # |_/______\_| Ex.in 3D   \ <-
    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + (offset * spacing) + self.current_offset_x
        return line_x

    # get y of line
    # |     /_\    |
    # |   /____\  |
    # |_/_______\_|     ____ <-
    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = (index * spacing_y) - self.current_offset_y
        return line_y

    # floor
    def init_floors(self):
        with self.canvas:
            for i in range(0, self.number_segment):
                self.floors.append(Quad(source="images/road.jpg"))

    def get_floor_coordinates(self, fl_x, fl_y):
        fl_y = fl_y - self.current_y_loop
        x = self.get_line_x_from_index(fl_x)
        y = self.get_line_y_from_index(fl_y)
        return x, y

    def generate_floors_coordinates(self):
        last_y = 0

        # del floor that out of screen
        for i in range(len(self.floors_coordinates) - 1, -1, -1):
            if self.floors_coordinates[i][1] < self.current_y_loop:
                del self.floors_coordinates[i]

        # avoid duplicate floor
        if len(self.floors_coordinates) > 0:
            last_coordinates = self.floors_coordinates[-1]
            last_y = last_coordinates[1] + 1

        # add new floor by index pos of floor
        for i in range(len(self.floors_coordinates), self.number_segment):
            self.floors_coordinates.append((0, last_y))
            last_y += 1

    def update_floors(self):
        start_index = -int(self.V_NB_LINES / 2) + 1

        for i in range(0, self.number_segment):
            floor = self.floors[i]
            floor_coordinates = self.floors_coordinates[i]
            # xmin, ymin = self.get_floor_coordinates(
            #     floor_coordinates[0], floor_coordinates[1]
            # )
            # xmax, ymax = self.get_floor_coordinates(
            #     floor_coordinates[0] + 1, floor_coordinates[1] + 1
            # )
            xmin, ymin = self.get_floor_coordinates(start_index, floor_coordinates[1])
            xmax, ymax = self.get_floor_coordinates(
                start_index + self.V_NB_LINES - 1, floor_coordinates[1] + 1
            )
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            floor.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    # enemy
    def init_enemys(self):
        with self.canvas:
            for i in range(0, self.number_enemy):
                self.enemys.append(
                    Rectangle(
                        source=choice(
                            [
                                "./images/car_2_cut.png",
                                "./images/car_3_cut.png",
                                "./images/car_4_cut.png",
                            ]
                        ),
                        pos=(-100, -100),
                        fit_mode="cover",
                    )
                )

    def get_enemy_coordinates(self, emy_x, em_y):
        em_y = em_y - self.current_y_loop
        x = self.get_line_x_from_index(emy_x)
        y = self.get_line_y_from_index(em_y)
        return x, y

    def generate_enemys_coordinates(self):
        last_y = 20

        start_index = -int(self.V_NB_LINES / 2) + 1

        # del enemy that out of screen
        for i in range(len(self.enemys_coordinates) - 1, -1, -1):
            if self.enemys_coordinates[i][1] < self.current_y_loop:
                del self.enemys_coordinates[i]
                self.canvas.remove(self.enemys[i])
                del self.enemys[i]
        # avoid duplicate enemy
        if len(self.enemys_coordinates) > 0:
            last_coordinates = self.enemys_coordinates[-1]
            last_y = last_coordinates[1] + 1

        # add new enemy by index pos of enemy
        for i in range(len(self.enemys_coordinates), self.number_enemy):
            self.fill_enemy()
            self.enemys_coordinates.append(
                (randint(start_index, start_index + self.V_NB_LINES - 2), last_y)
            )
            last_y += 1

    def fill_enemy(self):
        with self.canvas:
            self.enemys.append(
                Rectangle(
                    source=choice(
                        [
                            "./images/car_2_cut.png",
                            "./images/car_3_cut.png",
                            "./images/car_4_cut.png",
                        ]
                    ),
                    pos=(-100, -100),
                    fit_mode="cover",
                )
            )

    def redraw_behide_car(self, i):
        old_car = self.car
        old_enemy = self.enemys[i]
        self.canvas.remove(self.car)
        self.canvas.remove(self.enemys[i])
        self.canvas.add(old_car)
        self.canvas.add(old_enemy)

    def redraw_enemy(self):
        for i in range(self.number_enemy - 1, -1, -1):
            old_enemy = self.enemys[i]
            self.canvas.remove(old_enemy)
            self.canvas.add(old_enemy)

    def update_enemys(self):
        self.redraw_enemy()
        for i in range(0, self.number_enemy):
            enemy = self.enemys[i]
            enemy_coordinates = self.enemys_coordinates[i]
            xmin, ymin = self.get_enemy_coordinates(
                enemy_coordinates[0], enemy_coordinates[1] + 0.5
            )
            xmax, ymax = self.get_enemy_coordinates(
                enemy_coordinates[0] + 1, enemy_coordinates[1] + 1
            )
            #  2    3
            #
            #  1    4
            x1, y1 = self.transform(xmin, ymin)
            x4, y4 = self.transform(xmax, ymin)
            distance_x = math.dist((x1, y1), (x4, y4))
            enemy.size = [distance_x * 0.45, distance_x * 0.45 * 0.7]

            if enemy_coordinates[0] < 0:
                enemy.pos = [x4 - distance_x / 2, y1]
            elif enemy_coordinates[0] > 0:
                enemy.pos = [x1, y1]
            else:
                enemy.pos = [x1 + enemy.size[0] / 2, y1]

            # draw new z index car and enemy
            if self.enemys[i].pos[1] < self.car.pos[1] - self.car.size[1] * 0.2:
                self.redraw_behide_car(i)

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

    def opacity_car(self):
        old_car = self.car
        self.canvas.remove(self.car)
        self.canvas.add(Color(1, 1, 1, 0.5))
        self.canvas.add(old_car)
        self.canvas.add(Color(1, 1, 1, 1))

    # main update
    def update(self, dt):
        if STATE_CURRENT == STATE_INIT:
            return
        # real time
        time_factor = dt * 30
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_floors()
        self.update_car()

        if self.Immortal > 0:
            self.opacity_car()
            self.Immortal -= dt

        if len(self.enemys_coordinates) != 0:
            self.update_enemys()
            if self.collision_car():
                if self.HEART <= 0 and self.Immortal <= 0:
                    print("over")
                    Clock.unschedule(self.game_running)
                    return
                elif self.HEART > 0 and self.Immortal <= 0:
                    print("hit")
                    self.HEART -= 1
                    self.Immortal = 3

        self.update_background()

        speed_y = self.DRIVING_SPEED * self.height / 100
        self.current_offset_y += speed_y * time_factor

        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1
            self.generate_floors_coordinates()
            if self.current_y_loop > 5 and self.current_y_loop % 4 == 0:
                self.generate_enemys_coordinates()
            print("loop : " + str(self.current_y_loop))
        speed_x = self.current_direction_car * self.width / 100
        start_index = -int(self.V_NB_LINES / 2) + 1

        ## make car contain in road
        # self.car_coordinates[0][0] left x car
        # self.car_coordinates[1][0] right x car
        # <-
        if (
            self.current_direction_car < 0
            and self.vertical_lines[start_index].points[0] < self.car_coordinates[0][0]
        ):
            self.current_offset_x -= speed_x * time_factor
        # ->
        elif (
            self.current_direction_car > 0
            and self.vertical_lines[start_index + self.V_NB_LINES - 1].points[0]
            > self.car_coordinates[1][0]
        ):
            self.current_offset_x -= speed_x * time_factor

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


class Chocobo_RacingApp(App):
    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        start_screen = StartScreen(name="start")
        game_screen = GameScreen(name="play")
        stop_screen = StopScreen(name="stop")
        over_screen = OverScreen(name="over")

        screen_manager.add_widget(start_screen)
        screen_manager.add_widget(game_screen)
        screen_manager.add_widget(stop_screen)
        screen_manager.add_widget(over_screen)

        return screen_manager


if __name__ == "__main__":
    Chocobo_RacingApp().run()
