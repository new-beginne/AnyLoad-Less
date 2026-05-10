import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.animation import Animation
from kivy.utils import platform
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast

from db import db
from core import QueueManager


class TaskCard(MDCard):
    filename = StringProperty("video.mp4")
    progress = NumericProperty(0)
    speed = StringProperty("0 MB/s")
    eta = StringProperty("00:00")
    is_paused = BooleanProperty(False)
    download_id = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = "#1A1A1A"
        self.radius = [15, 15, 15, 15]
        self.elevation = 0
        self.size_hint_y = None
        self.height = "140dp"
        self.padding = "15dp"
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        app = MDApp.get_running_app()
        if self.is_paused:
            app.queue_manager.pause_download(self.download_id)
        else:
            app.queue_manager.resume_download(self.download_id)
    
    def cancel_download(self):
        app = MDApp.get_running_app()
        app.queue_manager.cancel_download(self.download_id)

class LibraryCard(MDCard):
    filename = StringProperty("video.mp4")
    thumbnail = StringProperty("assets/logo.png")
    file_type = StringProperty("video")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = "#1A1A1A"
        self.radius = [15, 15, 15, 15]
        self.elevation = 0
        self.size_hint_y = None
        self.height = "200dp"
        self.menu = None
    
    def show_menu(self, button):
        menu_items = [
            {"text": "Play", "viewclass": "OneLineListItem", "on_release": lambda: self.play_file()},
            {"text": "Details", "viewclass": "OneLineListItem", "on_release": lambda: self.show_details()},
            {"text": "Rename", "viewclass": "OneLineListItem", "on_release": lambda: self.rename_file()},
            {"text": "Delete", "viewclass": "OneLineListItem", "on_release": lambda: self.delete_file()}
        ]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=4)
        self.menu.open()
    
    def play_file(self):
        if self.menu:
            self.menu.dismiss()
        toast(f"Playing: {self.filename}")
    
    def show_details(self):
        if self.menu:
            self.menu.dismiss()
        toast(f"Details: {self.filename}")
    
    def rename_file(self):
        if self.menu:
            self.menu.dismiss()
        toast(f"Rename: {self.filename}")
    
    def delete_file(self):
        if self.menu:
            self.menu.dismiss()
        if self.parent:
            self.parent.remove_widget(self)
        toast("File deleted")

class Tab(MDBoxLayout, MDTabsBase):
    pass

class AnyLoadApp(MDApp):
    is_active_download = BooleanProperty(False)
    splash_dot_index = NumericProperty(0)
    topbar_dot_index = NumericProperty(0)
    spinner_angle = NumericProperty(0)
    library_filter = StringProperty("videos")
    max_downloads = NumericProperty(3)
    wifi_only = BooleanProperty(False)
    download_path = StringProperty("/storage/emulated/0/Download/AnyLoad")
    url_error_visible = BooleanProperty(False)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.title = "AnyLoad"
        
        self.queue_manager = QueueManager(self)
        
        return Builder.load_file("ui.kv")
    
    def on_pause(self):
        return True
    
    def on_start(self):
        if platform == "android":
            self.request_android_permissions()
        
        # Load settings from database
        self.load_settings_from_db()
        
        self.splash_event = Clock.schedule_interval(self.animate_splash_dots, 0.5)
        Clock.schedule_once(self.switch_to_home, 3.0)
        Clock.schedule_once(self.load_library_from_db, 3.5)
        Clock.schedule_once(self.start_topbar_animation, 3.5)
    
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
    
    def start_topbar_animation(self, dt):
        Clock.schedule_interval(self.animate_topbar_dots, 0.6)
    
    def animate_topbar_dots(self, dt):
        self.topbar_dot_index = (self.topbar_dot_index + 1) % 3
    
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
    
    def handle_paste(self):
        try:
            from kivy.core.clipboard import Clipboard
            url = Clipboard.paste()
            if url:
                self.root.ids.url_input.text = url
                self.root.ids.url_input.cursor = (0, 0)
                self.url_error_visible = False
        except Exception:
            pass
    
    def validate_url(self, url):
        if not url or not url.strip():
            return False
        url = url.strip()
        if 'http' not in url.lower():
            return False
        return True
    
    def handle_download(self, download_type):
        url = self.root.ids.url_input.text.strip()
        
        if not self.validate_url(url):
            self.url_error_visible = True
            toast("Please paste a valid URL first!")
            return
        
        self.url_error_visible = False
        self.queue_manager.add_download(url, download_type)
        self.root.ids.url_input.text = ""
        
        # Switch to tasks tab
        self.root.ids.screen_manager.current = "tasks"
    
    def animate_button_press(self, button):
        # MDRaisedButton doesn't support scale_x/scale_y, use opacity instead
        anim = Animation(opacity=0.7, duration=0.1)
        anim += Animation(opacity=1.0, duration=0.1)
        anim.start(button)
    
    def load_settings_from_db(self):
        """Load settings from database and update UI"""
        try:
            queue_limit = db.get_setting("queue_limit")
            wifi_only = db.get_setting("wifi_only")
            download_path = db.get_setting("download_path")
            
            if queue_limit:
                self.max_downloads = int(queue_limit)
            if wifi_only:
                self.wifi_only = wifi_only == "True"
            if download_path:
                self.download_path = download_path
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def change_queue_limit(self, value):
        """Update queue limit in database and app"""
        self.max_downloads = int(value)
        db.update_setting("queue_limit", int(value))
        self.queue_manager.update_max_concurrent(int(value))
        toast(f"Queue limit set to {int(value)}")
    
    def toggle_wifi(self, active):
        """Toggle Wi-Fi only mode"""
        self.wifi_only = active
        db.update_setting("wifi_only", str(active))
        status = "enabled" if active else "disabled"
        toast(f"Wi-Fi only mode {status}")
    
    def set_download_path(self, path):
        """Update download path in database"""
        self.download_path = path
        db.update_setting("download_path", path)
        toast(f"Download path updated")
    
    def load_library_from_db(self, dt=None):
        """Load library items from database"""
        try:
            videos_container = self.root.ids.library_tabs.ids.videos_container
            audio_container = self.root.ids.library_tabs.ids.audio_container
            playlists_container = self.root.ids.library_tabs.ids.playlists_container
            
            # Clear existing widgets
            videos_container.clear_widgets()
            audio_container.clear_widgets()
            playlists_container.clear_widgets()
            
            # Load videos
            videos = db.get_library("video")
            if videos:
                for item in videos:
                    card = LibraryCard(filename=item['title'], file_type="video")
                    videos_container.add_widget(card)
            else:
                from kivymd.uix.label import MDLabel
                label = MDLabel(
                    text="No videos found",
                    halign="center",
                    theme_text_color="Custom",
                    text_color="#666666",
                    size_hint_y=None,
                    height="50dp"
                )
                videos_container.add_widget(label)
            
            # Load audio
            audios = db.get_library("audio")
            if audios:
                for item in audios:
                    card = LibraryCard(filename=item['title'], file_type="audio")
                    audio_container.add_widget(card)
            else:
                from kivymd.uix.label import MDLabel
                label = MDLabel(
                    text="No audio files found",
                    halign="center",
                    theme_text_color="Custom",
                    text_color="#666666",
                    size_hint_y=None,
                    height="50dp"
                )
                audio_container.add_widget(label)
            
            # Playlists placeholder
            from kivymd.uix.label import MDLabel
            label = MDLabel(
                text="No playlists found",
                halign="center",
                theme_text_color="Custom",
                text_color="#666666",
                size_hint_y=None,
                height="50dp"
            )
            playlists_container.add_widget(label)
            
        except Exception as e:
            print(f"Error loading library: {e}")
    
    def filter_library(self, filter_type):
        self.library_filter = filter_type
        if filter_type == "videos":
            self.root.ids.library_tabs.switch_tab("Videos")
        elif filter_type == "audio":
            self.root.ids.library_tabs.switch_tab("Audio")
        elif filter_type == "playlists":
            self.root.ids.library_tabs.switch_tab("Playlists")
        toast(f"Showing {filter_type}")
    
    def change_download_path(self):
        # For now, just show toast. File picker in Phase 5
        toast("File picker coming in Phase 5")
        # Example: self.set_download_path("/new/path")
    

    
    def show_menu(self):
        try:
            menu_button = self.root.ids.get('menu_button')
            if not menu_button:
                toast("Menu coming soon")
                return
            
            menu_items = [
                {"text": "About AnyLoad", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_action("about")},
                {"text": "Privacy Policy", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_action("privacy")},
                {"text": "App Version (v1.1)", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_action("version")}
            ]
            if not hasattr(self, 'menu'):
                self.menu = MDDropdownMenu(caller=menu_button, items=menu_items, width_mult=4)
            else:
                self.menu.caller = menu_button
                self.menu.items = menu_items
            self.menu.open()
        except Exception as e:
            toast("Menu unavailable")
    
    def menu_action(self, action):
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        
        if action == "about":
            toast("AnyLoad — Download Anything. Anytime.")
        elif action == "privacy":
            toast("Privacy Policy")
        elif action == "version":
            toast("AnyLoad v1.1")

if __name__ == "__main__":
    AnyLoadApp().run()
