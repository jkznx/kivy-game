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
from kivy.graphics import Line, Quad, Triangle
from kivy.properties import NumericProperty
from kivy.core.image import Image
from kivy.graphics import Color
import random
import math

texture = Image("./images/road.jpg").texture
SCREEN_CX = SCREEN_W / 2
SCREEN_CY = SCREEN_H / 2


class Segment:
    def __init__(self, index, z):
        self.index = index
        self.x = 0
        self.y = 0
        self.z = z
        self.X = 0
        self.Y = 0
        self.W = 0
        self.scale = -1
        self.color = lambda: None
        self.color.road = Color(0, 1, 0)


class RLine:
    def __init__(self):
        self.total_segments = None
        self.visible_segments = 200
        self.segmentLength = 100
        self.rumble_segments = 5
        self.roadLanes = 3
        self.roadWidth = 1000
        self.roadLength = None

    def create(self):
        self.segments = []
        self.createRoad()

    def createRoad(self):
        self.createSection(1000)
        for i in range(self.rumble_segments):
            self.segments[i].color.road = Color(255, 255, 255)
            self.segments[len(self.segments) - 1 - i].color.road = Color(
                (145, 145, 145)
            )

        self.total_segments = len(self.segments)

        self.roadLength = self.total_segments * self.segmentLength

    def createSection(self, nSegments):
        for i in range(nSegments):
            self.createSegment()

    def createSegment(self):
        n = len(self.segments)
        self.segments.append(Segment(n, n * self.segmentLength))

    def getSegment(self, positionZ):
        if positionZ < 0:
            positionZ += self.roadLength
        index = math.floor(positionZ / self.segmentLength) % self.total_segments
        return self.segments[index]

    def project3D(self, point, cameraX, cameraY, cameraZ, cameraDepth):
        transX = point.world.x - cameraX
        transY = point.world.y - cameraY
        transZ = point.world.z - cameraZ

        point.scale = cameraDepth / transZ

        projectedX = point.scale * transX
        projectedY = point.scale * transY
        projectedW = point.scale * self.roadWidth

        point.screen.x = math.round((1 + projectedX) * SCREEN_CX)
        point.screen.y = math.round((1 - projectedY) * SCREEN_CY)
        point.screen.w = math.round(projectedW * SCREEN_CX)

    def render3D(self):
        self.graphics.clear()

        camera = self.scene.camera

        baseSegment = self.getSegment(camera.z)
        baseIndex = baseSegment.index

        for n in range(self.visible_segments):
            currIndex = (baseIndex + n) % self.total_segments
            currSegment = self.segments[currIndex]

            self.project3D(
                currSegment.point, camera.x, camera.y, camera.z, camera.distToPlane
            )

            if n > 0:
                prevIndex = (
                    currIndex - 1 if (currIndex > 0) else self.total_segments - 1
                )
                prevSegment = self.segments[prevIndex]

                p1 = prevSegment.point.screen
                p2 = currSegment.point.screen

                self.drawSegment(p1.x, p1.y, p1.w, p2.x, p2.y, p2.w, currSegment.color)

    def drawSegment(self, x1, y1, w1, x2, y2, w2, color):
        self.graphics.fillStyle(color.grass, 1)
        self.graphics.fillRect(0, y2, SCREEN_W, y1 - y2)

        self.drawPolygon(x1 - w1, y1, x1 + w1, y1, x2 + w2, y2, x2 - w2, y2, color.road)

        rumble_w1 = w1 / 5
        rumble_w2 = w2 / 5
        self.drawPolygon(
            x1 - w1 - rumble_w1,
            y1,
            x1 - w1,
            y1,
            x2 - w2,
            y2,
            x2 - w2 - rumble_w2,
            y2,
            color.rumble,
        )
        self.drawPolygon(
            x1 + w1 + rumble_w1,
            y1,
            x1 + w1,
            y1,
            x2 + w2,
            y2,
            x2 + w2 + rumble_w2,
            y2,
            color.rumble,
        )

        if color.lane:
            line_w1 = (w1 / 20) / 2
            line_w2 = (w2 / 20) / 2

            lane_w1 = (w1 * 2) / self.roadLanes
            lane_w2 = (w2 * 2) / self.roadLanes

            lane_x1 = x1 - w1
            lane_x2 = x2 - w2

            for i in range(1, self.roadLanes):
                lane_x1 += lane_w1
                lane_x2 += lane_w2
                self.drawPolygon(
                    lane_x1 - line_w1,
                    y1,
                    lane_x1 + line_w1,
                    y1,
                    lane_x2 + line_w2,
                    y2,
                    lane_x2 - line_w2,
                    y2,
                    color.lane,
                )

    def drawPolygon(self, x1, y1, x2, y2, x3, y3, x4, y4, color):
        self.graphics.fillStyle(color, 1)
        self.graphics.beginPath()

        self.graphics.moveTo(x1, y1)
        self.graphics.lineTo(x2, y2)
        self.graphics.lineTo(x3, y3)
        self.graphics.lineTo(x4, y4)

        self.graphics.closePath()
        self.graphics.fill()


class GameWidget(Widget):
    from user_actions import _on_key_down, _on_key_up, _on_keyboard_closed
    from tranforms import transform, transform_2D, transform_perspective

    # state game
    STATE_INIT = 1
    STATE_RESTART = 2
    STATE_PLAY = 3
    STATE_GAMEOVER = 4

    pause_text = "p for pause"

    CAR_MOVE_SPEED = 3.0
    current_direction_car = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = self.STATE_INIT
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self.create()
        self.game_running = Clock.schedule_interval(self.update, 1.0 / 60.0)

    def create(self):
        with self.canvas.before:
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
            RLine().create()
            self.state = self.STATE_INIT
        elif self.state == self.STATE_RESTART:
            print("restart")
            self.state = self.STATE_RESTART
        elif self.state == self.STATE_PLAY:
            self.state = self.STATE_PLAY
        elif self.state == self.STATE_GAMEOVER:
            print("over")
            self.state = self.STATE_GAMEOVER


class Chocobo_RacingApp(App):
    pass


Chocobo_RacingApp().run()
