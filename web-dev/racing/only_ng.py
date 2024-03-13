from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Ellipse, Triangle
import random

# colors
black = (0, 0, 0)
gray = (100, 100, 100)
green_grass = (86, 125, 70)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)
blue_sky = (115, 215, 255)
sunset_color = (255, 165, 0)


class MyWidget(Widget):
    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        self.bind(pos=self.draw_my_stuff)
        self.bind(size=self.draw_my_stuff)
        self.draw_my_stuff()

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
                    cloud_size = random.randint(30, 120)
                    cloud_color = white

                    Color(*[component / 255 for component in cloud_color])
                    Ellipse(
                        pos=(cloud_pos_x, cloud_pos_y), size=(cloud_size, cloud_size)
                    )
                    cloud_pos_x += random.randint(-30, 30)
                    cloud_pos_y += random.randint(-10, 10)

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
                pos=(self.width / 2.0 - 200, 0), size=(400, self.height * 0.8)
            )  # -200 from half of 400 rect make it center

            # Draw center line
            Color(1, 1, 1)
            dash_length = 40
            gap_length = 50
            Line(
                points=[self.width / 2.0, 0, self.width / 2.0, self.height * 0.8],
                dash_length=dash_length,
                dash_offset=gap_length,
            )


class MyApp(App):
    def build(self):
        return MyWidget()


if __name__ == "__main__":
    MyApp().run()