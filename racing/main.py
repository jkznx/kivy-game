# main.py
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.uix.image import Image
from kivy.clock import Clock
import random


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        start_button = Button(text='Start Game', size_hint=(0.2, 0.1), pos_hint={'x': 0.4, 'y': 0.45})
        start_button.bind(on_press=self.start_game)
        layout.add_widget(start_button)
        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.current = 'game'
        game_screen = self.manager.get_screen('game')
        game_screen.start_game()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = None

    def start_game(self):
        self.game = ChocoboRacingGame()
        self.add_widget(self.game)

    def on_pre_leave(self, *args):
        if self.game:
            self.game.stop_game()


class Chocobo(Image):
    velocity = NumericProperty(0)

    def move(self):
        self.x += self.velocity


class Obstacle(Widget):
    pass


class ChocoboRacingGame(Widget):
    chocobo = ObjectProperty(None)
    obstacles = ListProperty([])
    score = NumericProperty(0)
    game_over = BooleanProperty(False)
    sound = SoundLoader.load('background_music.mp3')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chocobo = Chocobo(source='car.png', size=(100, 50))
        self.add_widget(self.chocobo)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.sound.loop = True
        self.sound.play()

    def update(self, dt):
        if not self.game_over:
            self.chocobo.move()
            self.score += 1
            self.generate_obstacles()

            # Check for collisions
            for obstacle in self.obstacles:
                if obstacle.collide_widget(self.chocobo):
                    self.end_game()

    def generate_obstacles(self):
        if random.randint(1, 100) > 90:
            obstacle = Obstacle()
            obstacle.x = self.width
            obstacle.y = random.randint(0, self.height - obstacle.height)
            self.add_widget(obstacle)
            self.obstacles.append(obstacle)

    def end_game(self):
        self.game_over = True
        self.sound.stop()

    def stop_game(self):
        self.sound.stop()
        Clock.unschedule(self.update)


class ChocoboRacingApp(App):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(StartScreen(name='start'))
        screen_manager.add_widget(GameScreen(name='game'))
        return screen_manager


if __name__ == '__main__':
    ChocoboRacingApp().run()
