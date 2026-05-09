import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation

class AnyLoadApp(MDApp):
    splash_dot_index = NumericProperty(0)
    is_active_download = BooleanProperty(False)
    spinner_rotation = NumericProperty(0)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.title = "AnyLoad"
        return Builder.load_file("ui.kv")
    
    def on_pause(self):
        return True
    
    def on_start(self):
        # Start splash screen animation
        self.splash_animation_event = Clock.schedule_interval(self.animate_splash_dots, 0.5)
        # Switch to home after 3 seconds
        Clock.schedule_once(self.switch_to_home, 3)
    
    def animate_splash_dots(self, dt):
        self.splash_dot_index = (self.splash_dot_index + 1) % 3
    
    def switch_to_home(self, dt):
        # Stop splash animation
        if self.splash_animation_event:
            self.splash_animation_event.cancel()
        # Switch to home screen
        self.root.ids.screen_manager.current = "home"
    
    def on_is_active_download(self, instance, value):
        # Start or stop spinner animation based on download state
        if value:
            self.start_spinner_animation()
        else:
            self.stop_spinner_animation()
    
    def start_spinner_animation(self):
        # Continuous rotation animation for spinner
        anim = Animation(spinner_rotation=360, duration=1)
        anim.bind(on_complete=self.reset_spinner_rotation)
        anim.start(self)
    
    def reset_spinner_rotation(self, *args):
        self.spinner_rotation = 0
        if self.is_active_download:
            self.start_spinner_animation()
    
    def stop_spinner_animation(self):
        Animation.cancel_all(self, 'spinner_rotation')
        self.spinner_rotation = 0

if __name__ == "__main__":
    AnyLoadApp().run()
