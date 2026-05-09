import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty
from kivy.animation import Animation
from kivy.utils import platform

class AnyLoadApp(MDApp):
    is_active_download = BooleanProperty(False)
    splash_dot_index = NumericProperty(0)
    spinner_angle = NumericProperty(0)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.title = "AnyLoad"
        return Builder.load_file("ui.kv")
    
    def on_pause(self):
        return True
    
    def on_start(self):
        # Request Android permissions
        if platform == "android":
            self.request_android_permissions()
        
        # Start splash screen dot animation
        self.splash_event = Clock.schedule_interval(self.animate_splash_dots, 0.5)
        
        # Switch to home after 3 seconds
        Clock.schedule_once(self.switch_to_home, 3)
    
    def request_android_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            permissions = [
                Permission.READ_MEDIA_VIDEO,
                Permission.READ_MEDIA_AUDIO,
                Permission.POST_NOTIFICATIONS,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ]
            request_permissions(permissions)
        except Exception:
            pass
    
    def animate_splash_dots(self, dt):
        self.splash_dot_index = (self.splash_dot_index + 1) % 3
    
    def switch_to_home(self, dt):
        if self.splash_event:
            self.splash_event.cancel()
        self.root.ids.screen_manager.current = "home"
    
    def on_is_active_download(self, instance, value):
        if value:
            self.start_spinner()
        else:
            self.stop_spinner()
    
    def start_spinner(self):
        anim = Animation(spinner_angle=360, duration=1.2)
        anim.bind(on_complete=self.loop_spinner)
        anim.start(self)
    
    def loop_spinner(self, *args):
        self.spinner_angle = 0
        if self.is_active_download:
            self.start_spinner()
    
    def stop_spinner(self):
        Animation.cancel_all(self, 'spinner_angle')
        self.spinner_angle = 0
    
    def paste_from_clipboard(self):
        try:
            from kivy.core.clipboard import Clipboard
            url = Clipboard.paste()
            self.root.ids.url_input.text = url
            self.root.ids.url_input.cursor = (0, 0)
        except Exception:
            pass

if __name__ == "__main__":
    AnyLoadApp().run()
