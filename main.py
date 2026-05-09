import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty

class AnyLoadApp(MDApp):
    dot_index = NumericProperty(0)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.title = "AnyLoad"
        return Builder.load_file("ui.kv")
    
    def on_pause(self):
        return True
    
    def on_start(self):
        self.animate_dots_event = None
    
    def start_dot_animation(self):
        if not self.animate_dots_event:
            self.animate_dots_event = Clock.schedule_interval(self.animate_dots, 0.5)
    
    def stop_dot_animation(self):
        if self.animate_dots_event:
            self.animate_dots_event.cancel()
            self.animate_dots_event = None
            self.dot_index = 0
    
    def animate_dots(self, dt):
        self.dot_index = (self.dot_index + 1) % 3

if __name__ == "__main__":
    AnyLoadApp().run()
