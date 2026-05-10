import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.animation import Animation
from kivy.utils import platform
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast
import threading
import queue
import time
import re

class DownloadManager:
    def __init__(self, app):
        self.app = app
        self.active_downloads = {}
        self.download_queue = queue.Queue()
        self.max_concurrent = 3
        self.running = True
        
        self.queue_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.queue_thread.start()
    
    def process_queue(self):
        while self.running:
            try:
                if len(self.active_downloads) < self.max_concurrent:
                    if not self.download_queue.empty():
                        download_info = self.download_queue.get()
                        self.start_download(download_info)
                time.sleep(0.5)
            except Exception as e:
                print(f"Queue error: {e}")
    
    def add_to_queue(self, url, download_type="video"):
        download_info = {
            'url': url,
            'type': download_type,
            'id': f"dl_{int(time.time() * 1000)}"
        }
        self.download_queue.put(download_info)
        Clock.schedule_once(lambda dt: toast("Added to download queue"), 0)
    
    def start_download(self, download_info):
        download_id = download_info['id']
        
        task_card = TaskCard(
            filename="Fetching info...",
            progress=0,
            speed="0 KB/s",
            eta="--:--",
            download_id=download_id
        )
        
        Clock.schedule_once(lambda dt: self.app.root.ids.task_container.add_widget(task_card), 0)
        
        download_thread = threading.Thread(
            target=self.download_worker,
            args=(download_info, task_card),
            daemon=True
        )
        
        self.active_downloads[download_id] = {
            'thread': download_thread,
            'card': task_card,
            'paused': False,
            'cancelled': False
        }
        
        download_thread.start()
        Clock.schedule_once(lambda dt: setattr(self.app, 'is_active_download', True), 0)
    
    def download_worker(self, download_info, task_card):
        try:
            import yt_dlp
            
            download_id = download_info['id']
            url = download_info['url']
            download_type = download_info['type']
            
            if platform == "android":
                from android.storage import primary_external_storage_path
                download_path = os.path.join(primary_external_storage_path(), "Download", "AnyLoad")
            else:
                download_path = os.path.expanduser("~/Downloads/AnyLoad")
            
            os.makedirs(download_path, exist_ok=True)
            
            ydl_opts = {
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [lambda d: self.progress_hook(d, task_card, download_id)],
                'quiet': True,
                'no_warnings': True
            }
            
            if download_type == "audio":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                })
            elif download_type == "playlist":
                ydl_opts['noplaylist'] = False
            else:
                ydl_opts['format'] = 'best'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                
                Clock.schedule_once(
                    lambda dt: setattr(task_card, 'filename', info.get('title', 'Unknown')),
                    0
                )
                
                if self.active_downloads.get(download_id, {}).get('cancelled'):
                    return
                
                ydl.download([url])
                Clock.schedule_once(lambda dt: self.download_complete(download_id, task_card, filename), 0)
        
        except Exception as e:
            error_msg = str(e)
            Clock.schedule_once(lambda dt: self.download_failed(download_id, task_card, error_msg), 0)
    
    def progress_hook(self, d, task_card, download_id):
        if d['status'] == 'downloading':
            if self.active_downloads.get(download_id, {}).get('cancelled'):
                raise Exception("Download cancelled")
            
            while self.active_downloads.get(download_id, {}).get('paused'):
                time.sleep(0.5)
                if self.active_downloads.get(download_id, {}).get('cancelled'):
                    raise Exception("Download cancelled")
            
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    progress = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)
                    
                    if speed:
                        if speed > 1024 * 1024:
                            speed_str = f"{speed / (1024 * 1024):.1f} MB/s"
                        else:
                            speed_str = f"{speed / 1024:.1f} KB/s"
                    else:
                        speed_str = "0 KB/s"
                    
                    if eta:
                        mins = int(eta // 60)
                        secs = int(eta % 60)
                        eta_str = f"{mins:02d}:{secs:02d}"
                    else:
                        eta_str = "--:--"
                    
                    Clock.schedule_once(lambda dt: setattr(task_card, 'progress', progress), 0)
                    Clock.schedule_once(lambda dt: setattr(task_card, 'speed', speed_str), 0)
                    Clock.schedule_once(lambda dt: setattr(task_card, 'eta', eta_str), 0)
            except Exception:
                pass
    
    def download_complete(self, download_id, task_card, filename):
        if download_id in self.active_downloads:
            del self.active_downloads[download_id]
        
        if task_card.parent:
            task_card.parent.remove_widget(task_card)
        
        if len(self.active_downloads) == 0:
            self.app.is_active_download = False
        
        toast("Download complete!")
    
    def download_failed(self, download_id, task_card, error):
        if download_id in self.active_downloads:
            del self.active_downloads[download_id]
        
        task_card.speed = "Failed"
        task_card.eta = ""
        
        if len(self.active_downloads) == 0:
            self.app.is_active_download = False
        
        toast(f"Download failed: {error[:50]}")
    
    def pause_download(self, download_id):
        if download_id in self.active_downloads:
            self.active_downloads[download_id]['paused'] = True
    
    def resume_download(self, download_id):
        if download_id in self.active_downloads:
            self.active_downloads[download_id]['paused'] = False
    
    def cancel_download(self, download_id):
        if download_id in self.active_downloads:
            self.active_downloads[download_id]['cancelled'] = True
            del self.active_downloads[download_id]

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
            app.download_manager.pause_download(self.download_id)
        else:
            app.download_manager.resume_download(self.download_id)
    
    def cancel_download(self):
        app = MDApp.get_running_app()
        app.download_manager.cancel_download(self.download_id)
        if self.parent:
            self.parent.remove_widget(self)

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

class AnyLoadApp(MDApp):
    is_active_download = BooleanProperty(False)
    splash_dot_index = NumericProperty(0)
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
        
        self.download_manager = DownloadManager(self)
        
        return Builder.load_file("ui.kv")
    
    def on_pause(self):
        return True
    
    def on_start(self):
        if platform == "android":
            self.request_android_permissions()
        
        self.splash_event = Clock.schedule_interval(self.animate_splash_dots, 0.5)
        Clock.schedule_once(self.switch_to_home, 3.0)
        Clock.schedule_once(self.add_mock_library, 3.5)
    
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
        self.download_manager.add_to_queue(url, download_type)
        self.root.ids.url_input.text = ""
        
        # Switch to tasks tab
        self.root.ids.screen_manager.current = "tasks"
    
    def animate_button_press(self, button):
        anim = Animation(scale_x=0.95, scale_y=0.95, duration=0.1)
        anim += Animation(scale_x=1.0, scale_y=1.0, duration=0.1)
        anim.start(button)
    
    def add_mock_library(self, dt):
        library_container = self.root.ids.library_container
        
        for i, (name, ftype) in enumerate([
            ("Tutorial Video.mp4", "video"),
            ("Favorite Song.mp3", "audio"),
            ("Documentary.mp4", "video"),
            ("Podcast Episode.mp3", "audio")
        ]):
            card = LibraryCard(filename=name, file_type=ftype)
            library_container.add_widget(card)
    
    def filter_library(self, filter_type):
        self.library_filter = filter_type
        toast(f"Showing {filter_type}")
    
    def change_download_path(self):
        toast("File picker coming in Phase 5")
    
    def on_max_downloads(self, instance, value):
        self.download_manager.max_concurrent = int(value)
    
    def show_menu(self):
        menu_items = [
            {"text": "About AnyLoad", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_action("about")},
            {"text": "Privacy Policy", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_action("privacy")},
            {"text": "App Version (v1.1)", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_action("version")}
        ]
        if not hasattr(self, 'menu'):
            self.menu = MDDropdownMenu(items=menu_items, width_mult=4)
        self.menu.items = menu_items
        self.menu.open()
    
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
