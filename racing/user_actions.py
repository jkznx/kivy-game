from kivy.clock import Clock


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
        if self.pause_text == "p for resume":
            self.pause_text = "p for pause"
            self.pause.text = self.pause_text
            self.game_running = Clock.schedule_interval(self.update, 1 / 30)
        elif self.pause_text == "p for pause":
            self.pause_text = "p for resume"
            self.pause.text = self.pause_text
            Clock.unschedule(self.game_running)
        print("stop", self.pause_text)


def _on_key_up(self, keyboard, keycode):
    self.current_direction_car = 0
