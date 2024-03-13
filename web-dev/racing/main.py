from kivy.config import Config
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle
from canvas_test import draw_background  # Import the draw_background function

# Define class for game screen
class GameScreen(Screen):
    pass

# Define class for game widget
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update)
        self.bind(pos=self._update)

        # Add custom-drawn background using the draw_background function
        draw_background(self, self.width, self.height)

        # Add player car
        with self.canvas:
            self.car_size = min(self.width, self.height) * 0.2
            self.hero = Rectangle(
                pos=(self.center_x - self.car_size / 2, self.center_y - self.car_size / 2),
                size=(self.car_size, self.car_size),
                source="./images/car.png",
            )

    def _update(self, instance, value):
        self.canvas.clear()
        draw_background(self, self.width, self.height)
        self.hero.size = (self.car_size, self.car_size)
        self.hero.pos = (self.center_x - self.car_size / 2, self.center_y - self.car_size / 2)

# Define the main app
class Chocobo_Racing(App):
    def build(self):
        screen_manager = ScreenManager()

        # Add start and game screens
        game_screen = GameScreen(name="game")
        game_widget = GameWidget()

        screen_manager.add_widget(game_screen)
        game_screen.add_widget(game_widget)

        return screen_manager

# Run the app
if __name__ == "__main__":
    Config.set("graphics", "resizable", 1)
    app = Chocobo_Racing()
    app.run()
