import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ObjectProperty
from kivy.animation import Animation
from kivy.utils import platform
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu

class ActionCard(MDCard):
    icon = StringProperty("")
    title = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_behavior = True
        self.md_bg_color = "#1A1A1A"
        self.radius = [15]
        self.elevation = 0
        self.size_hint_y = None
        self.height = "70dp"

class TaskCard(MDCard):
    filename = StringProperty("video.mp4")
    progress = NumericProperty(0)
    speed = StringProperty("0 MB/s")
    eta = StringProperty("00:00")
    is_paused = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = "#1A1A1A"
        self.radius = [15]
        self.elevation = 0
        self.size_hint_y = None
        self.height = "140dp"
        self.padding = "15dp"
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
    
    def cancel_download(self):
        # Remove this card from parent
        if self.parent:
            self.parent.remove_widget(self)

class LibraryCard(MDCard):
    filename = StringProperty("video.mp4")
    thumbnail = StringProperty("assets/logo.png")
    file_type = StringProperty("video")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = "#1A1A1A"
        self.radius = [15]
        self.elevation = 0
        self.size_hint_y = None
        self.height = "200dp"
        self.menu = None
    
    def show_menu(self, button):
        menu_items = [
            {
                "text": "Play",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.play_file()
            },
            {
                "text": "Details",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.show_details()
            },
            {
                "text": "Rename",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.rename_file()
            },
            {
                "text": "Delete",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.delete_file()
            }
        ]
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4
        )
        self.menu.open()
    
    def play_file(self):
        if self.menu:
            self.menu.dismiss()
        print(f"Playing: {self.filename}")
    
    def show_details(self):
        if self.menu:
            self.menu.dismiss()
        print(f"Details: {self.filename}")
    
    def rename_file(self):
        if self.menu:
            self.menu.dismiss()
        print(f"Rename: {self.filename}")
    
    def delete_file(self):
        if self.menu:
            self.menu.dismiss()
        if self.parent:
            self.parent.remove_widget(self)

class AnyLoadApp(MDApp):
    is_active_download = BooleanProperty(False)
    splash_dot_index = NumericProperty(0)
    spinner_angle = NumericProperty(0)
    library_filter = StringProperty("videos")
    max_downloads = NumericProperty(3)
    wifi_only = BooleanProperty(False)
    download_path = StringProperty("/storage/emulated/0/Download/AnyLoad")
    
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
        
        # Switch to home after exactly 3 seconds
        Clock.schedule_once(self.switch_to_home, 3.0)
        
        # Add mock data after splash
        Clock.schedule_once(self.add_mock_data, 3.5)
    
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
        anim = Animation(spinner_angle=360, duration=1.0)
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
            if url:
                self.root.ids.url_input.text = url
                self.root.ids.url_input.cursor = (0, 0)
        except Exception:
            pass
    
    def add_mock_data(self, dt):
        # Add mock task cards
        task_container = self.root.ids.task_container
        
        task1 = TaskCard(
            filename="Amazing Video Tutorial.mp4",
            progress=74,
            speed="1.7 MB/s",
            eta="00:45"
        )
        task_container.add_widget(task1)
        
        task2 = TaskCard(
            filename="Podcast Episode 42.mp3",
            progress=32,
            speed="850 KB/s",
            eta="02:15"
        )
        task_container.add_widget(task2)
        
        task3 = TaskCard(
            filename="Documentary Series S01E03.mp4",
            progress=91,
            speed="2.3 MB/s",
            eta="00:12"
        )
        task_container.add_widget(task3)
        
        # Add mock library cards
        library_container = self.root.ids.library_container
        
        lib1 = LibraryCard(
            filename="Tutorial Video.mp4",
            file_type="video"
        )
        library_container.add_widget(lib1)
        
        lib2 = LibraryCard(
            filename="Favorite Song.mp3",
            file_type="audio"
        )
        library_container.add_widget(lib2)
        
        lib3 = LibraryCard(
            filename="Documentary.mp4",
            file_type="video"
        )
        library_container.add_widget(lib3)
        
        lib4 = LibraryCard(
            filename="Podcast Episode.mp3",
            file_type="audio"
        )
        library_container.add_widget(lib4)
    
    def filter_library(self, filter_type):
        self.library_filter = filter_type
        print(f"Library filtered to: {filter_type}")
    
    def change_download_path(self):
        print("Opening file picker for download path...")

if __name__ == "__main__":
    AnyLoadApp().run()
