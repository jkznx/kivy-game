from turtle import color
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
from kivy.graphics.vertex_instructions import Line
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Color
import math

SCREEN_CX = SCREEN_W / 2
SCREEN_CY = SCREEN_H / 2


class GameWidget(Widget):
    # keyboard input

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    # state game
    STATE_INIT = 1
    STATE_RESTART = 2
    STATE_PLAY = 3
    STATE_PAUSE = 4
    STATE_GAMEOVER = 5

    pause_text = "p for pause"

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.state = self.STATE_PLAY
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        print(Segment(2, 5, 6).x)
        self.create()
        self.game_running = Clock.schedule_interval(self.update, 1 / 30)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if "a" in keycode[1]:
            ...
        elif "d" in keycode[1]:
            ...
        elif "p" in keycode[1]:
            if self.pause_text == "p for resume":
                self.pause_text = "p for pause"
                self.pause.text = self.pause_text
                self.game_running = Clock.schedule_interval(self.update, 1 / 30)
            elif self.pause_text == "p for pause":
                self.pause_text = "p for resume"
                self.pause.text = self.pause_text
                Clock.unschedule(self.game_running)
            print("stop", self.pause_text)

    def _on_key_up(self, keyboard, keycode): ...
    def create(self):
        with self.canvas:
            self.bg = Rectangle(
                size=Window.size,
                source="./images/racing_bg_3.png",
                pos=(0, 0),
            )
            self.pause = Label(
                text=self.pause_text,
                font_size="30sp",
                font_name="./fonts/pixel_font.ttf",
                pos=(750, 700),
            )

    def update(self, dt):
        self.switch_state()

    def switch_state(self):
        if self.state == self.STATE_INIT:
            print("start")
            self.state = self.STATE_INIT
            # self.manager.current = "start"
        elif self.state == self.STATE_RESTART:
            print("restart")
            self.state = self.STATE_RESTART
            # self.manager.current = "restart"
        elif self.state == self.STATE_PLAY:
            # print("playing")
            self.state = self.STATE_PLAY
            # self.manager.current = "play"
        # elif self.state == self.STATE_PAUSE:
        #     print("stop")
        #     self.state = self.STATE_PAUSE
        #     # self.manager.current = "play"
        elif self.state == self.STATE_GAMEOVER:
            print("over")
            self.state = self.STATE_GAMEOVER
            # self.manager.current = "over"


class Road:

    #  array of road segments
    segments = []

    #  single segment length
    segmentLength = 100

    #  total number of road segments
    total_segments = 0

    #  number of visible segments to be drawn
    visible_segments = 200

    #  number of segments that forms a rumble strip
    rumble_segments = 5

    #  number of road lanes
    roadLanes = 3

    #  road width (actually half of the road)
    roadWidth = 1000

    #  total road length
    roadLength = 0

    def __init__(self, **kwargs):
        self.create()

    def create(self):
        self.segments = []
        self.createRoad()

    def createRoad(self):
        self.createSection(1000)

    def createSection(self, nsegment):
        for i in range(nsegment):
            self.createSegment()

    def createSegment(self):
        n = self.segments.lenght
        s = ObjectProperty(None)
        point = ObjectProperty(None)
        # point.world.x=
        s.index = n
        s.point = n
        self.segments.push(s)


class Segment:
    def __init__(self, n, segmentLength, rumble_segments):
        self.index = n
        self.world.x = 0
        self.point.world.y = 0
        setattr(self, "point")
        self.point.world.z = n * segmentLength
        self.point.screen.x = 0
        self.point.screen.y = 0
        self.point.screen.w = 0
        self.point.scale = -1
        self.color = (
            Color(0, 0, 0)
            if math.floor(n / rumble_segments) % 2 == 0
            else Color(255, 255, 255)
        )


class Chocobo_RacingApp(App):
    pass


Chocobo_RacingApp().run()
