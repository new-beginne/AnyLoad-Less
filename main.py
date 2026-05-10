import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.animation import Animation
from kivy.utils import platform
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout

from db import db
from core import QueueManager

# Cross-platform toast wrapper
def toast(text):
    """Toast notification for Android, console print for desktop"""
    try:
        from kivymd.toast import toast as md_toast
        md_toast(text)
    except (ImportError, TypeError):
        print(f"[TOAST] {text}")


class TaskCard(MDCard):
    """Download task card with progress tracking"""
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
        """Toggle pause/resume state"""
        self.is_paused = not self.is_paused
        app = MDApp.get_running_app()
        if self.is_paused:
            app.queue_manager.pause_download(self.download_id)
        else:
            app.queue_manager.resume_download(self.download_id)
    
    def cancel_download(self):
        """Cancel download and remove card"""
        app = MDApp.get_running_app()
        app.queue_manager.cancel_download(self.download_id)


class LibraryCard(MDCard):
    """Library item card with 3-dot menu"""
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
        """Show 3-dot menu"""
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


class Tab(MDBoxLayout):
    """Tab container for Library sub-tabs"""
    pass


class AnyLoadApp(MDApp):
    """Main application class"""
    
    # Properties
    is_active_download = BooleanProperty(False)
    splash_dot_index = NumericProperty(0)
    topbar_dot_index = NumericProperty(0)
    max_downloads = NumericProperty(3)
    wifi_only = BooleanProperty(False)
    download_path = StringProperty("/sdcard/Download/AnyLoad")
    url_error_visible = BooleanProperty(False)
    
    def build(self):
        """Build the app UI"""
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.title = "AnyLoad"
        
        # Initialize queue manager
        self.queue_manager = QueueManager(self)
        
        return Builder.load_file("ui.kv")
    
    def on_pause(self):
        """Handle app pause (Android lifecycle)"""
        return True
    
    def on_start(self):
        """App startup logic"""
        if platform == "android":
            self.request_android_permissions()
        
        # Load settings from database
        self.load_settings_from_db()
        
        # Start splash animation
        self.splash_event = Clock.schedule_interval(self.animate_splash_dots, 0.5)
        Clock.schedule_once(self.switch_to_home, 3.0)
        Clock.schedule_once(self.load_library_from_db, 3.5)
    
    def request_android_permissions(self):
        """Request Android 11+ permissions"""
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
        """Animate splash screen dots"""
        self.splash_dot_index = (self.splash_dot_index + 1) % 3
    
    def switch_to_home(self, dt):
        """Switch from splash to home screen"""
        if self.splash_event:
            self.splash_event.cancel()
        self.root.ids.screen_manager.current = "home"
        
        # Start top bar animation
        Clock.schedule_interval(self.animate_topbar_dots, 0.6)
    
    def animate_topbar_dots(self, dt):
        """Animate top bar dots only when downloads are active"""
        if self.is_active_download:
            self.topbar_dot_index = (self.topbar_dot_index + 1) % 3
        else:
            self.topbar_dot_index = -1  # Hide all dots when no downloads
    
    def handle_paste(self):
        """Paste URL from clipboard"""
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
        """Validate URL format"""
        if not url or not url.strip():
            return False
        url = url.strip()
        if 'http' not in url.lower():
            return False
        return True
    
    def handle_download(self, download_type):
        """Handle download button click"""
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
        
        # Mark downloads as active
        self.is_active_download = True
    
    def animate_button_press(self, button):
        """Animate button press"""
        anim = Animation(opacity=0.7, duration=0.1)
        anim += Animation(opacity=1.0, duration=0.1)
        anim.start(button)
    
    def load_settings_from_db(self):
        """Load settings from database"""
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
        """Update queue limit"""
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
        """Update download path"""
        self.download_path = path
        db.update_setting("download_path", path)
        toast("Download path updated")
    
    def load_library_from_db(self, dt=None):
        """Load library items from database"""
        try:
            videos_container = self.root.ids.videos_container
            audio_container = self.root.ids.audio_container
            playlists_container = self.root.ids.playlists_container
            
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
    
    def change_download_path(self):
        """Change download path (file picker in Phase 5)"""
        toast("File picker coming in Phase 5")
    
    def show_menu(self):
        """Show top menu"""
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
        except Exception:
            toast("Menu unavailable")
    
    def menu_action(self, action):
        """Handle menu actions"""
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
