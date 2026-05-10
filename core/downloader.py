"""
Download Engine for AnyLoad v1.1
Lazy yt-dlp loading, queue management, and progress tracking
Thread-safe for Android multi-core processors
"""

import os
import re
import gc
import time
import threading
from queue import Queue
from kivy.clock import Clock
from kivy.utils import platform


class DownloadTask:
    """Individual download task with progress tracking"""
    
    def __init__(self, url, download_type, task_card, app, download_id):
        self.url = url
        self.download_type = download_type
        self.task_card = task_card
        self.app = app
        self.download_id = download_id
        self.is_paused = False
        self.is_cancelled = False
        self.thread = None
        self.download_path = self._get_download_path()
        
    def _get_download_path(self):
        """Get download path from settings or use default"""
        try:
            from db import db
            path = db.get_setting("download_path")
            if path:
                return path
        except:
            pass
        
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path
                return os.path.join(primary_external_storage_path(), "Download", "AnyLoad")
            except:
                return "/sdcard/Download/AnyLoad"
        else:
            return os.path.expanduser("~/Downloads/AnyLoad")
    
    def start(self):
        """Start download in background thread"""
        self.thread = threading.Thread(target=self._download_worker, daemon=True)
        self.thread.start()
    
    def _download_worker(self):
        """Worker thread - LAZY LOADS yt-dlp here"""
        try:
            # LAZY IMPORT - Only load yt-dlp inside thread to prevent boot timeout
            import yt_dlp
            
            os.makedirs(self.download_path, exist_ok=True)
            
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
                'no_color': True,  # Prevent ANSI codes
            }
            
            # Format selection based on download type
            if self.download_type == "audio":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif self.download_type == "playlist":
                ydl_opts['noplaylist'] = False
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
            else:  # video
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(self.url, download=False)
                
                if self.is_cancelled:
                    return
                
                title = info.get('title', 'Unknown')
                filesize = info.get('filesize') or info.get('filesize_approx', 0)
                
                # Update card with title
                Clock.schedule_once(lambda dt: setattr(self.task_card, 'filename', title), 0)
                
                # Start actual download
                ydl.download([self.url])
                
                # Download complete
                if not self.is_cancelled:
                    filename = ydl.prepare_filename(info)
                    self._on_complete(title, filename, filesize)
        
        except Exception as e:
            if not self.is_cancelled:
                error_msg = self._clean_string(str(e))
                Clock.schedule_once(lambda dt: self._on_error(error_msg), 0)
    
    def _progress_hook(self, d):
        """Progress callback from yt-dlp"""
        if self.is_cancelled:
            raise Exception("Download cancelled")
        
        # Handle pause
        while self.is_paused and not self.is_cancelled:
            time.sleep(0.5)
        
        if self.is_cancelled:
            raise Exception("Download cancelled")
        
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    progress = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)
                    
                    # Format speed
                    if speed:
                        if speed > 1024 * 1024:
                            speed_str = f"{speed / (1024 * 1024):.1f} MB/s"
                        else:
                            speed_str = f"{speed / 1024:.1f} KB/s"
                    else:
                        speed_str = "0 KB/s"
                    
                    # Format ETA
                    if eta:
                        mins = int(eta // 60)
                        secs = int(eta % 60)
                        eta_str = f"{mins:02d}:{secs:02d}"
                    else:
                        eta_str = "--:--"
                    
                    # Clean strings and update UI on main thread
                    speed_str = self._clean_string(speed_str)
                    Clock.schedule_once(lambda dt: self._update_ui(progress, speed_str, eta_str), 0)
            except Exception:
                pass
    
    def _update_ui(self, progress, speed, eta):
        """Update task card UI"""
        self.task_card.progress = progress
        self.task_card.speed = speed
        self.task_card.eta = eta
    
    def _on_complete(self, title, filepath, filesize):
        """Handle download completion - vanish card and add to library"""
        # Add to library database
        try:
            from db import db
            file_type = "audio" if self.download_type == "audio" else "video"
            db.add_to_library(title, filepath, file_type, filesize)
        except Exception as e:
            print(f"Failed to add to library: {e}")
        
        # Remove task card from UI (vanish logic)
        Clock.schedule_once(lambda dt: self._remove_card(), 0)
        
        # Notify queue manager
        Clock.schedule_once(lambda dt: self.app.queue_manager.on_download_complete(self.download_id), 0)
        
        # Reload library to show new file
        Clock.schedule_once(lambda dt: self.app.load_library_from_db(), 0)
        
        # Clean up memory for low-end devices
        gc.collect()
    
    def _on_error(self, error_msg):
        """Handle download error"""
        self.task_card.speed = "Failed"
        self.task_card.eta = ""
        
        # Show toast
        def show_toast(text):
            try:
                from kivymd.toast import toast as md_toast
                md_toast(text)
            except (ImportError, TypeError):
                print(f"[TOAST] {text}")
        
        show_toast(f"Error: {error_msg[:50]}")
        
        # Notify queue manager
        self.app.queue_manager.on_download_complete(self.download_id)
    
    def _remove_card(self):
        """Remove task card from UI"""
        if self.task_card.parent:
            self.task_card.parent.remove_widget(self.task_card)
    
    def pause(self):
        """Pause download"""
        self.is_paused = True
    
    def resume(self):
        """Resume download"""
        self.is_paused = False
    
    def cancel(self):
        """Cancel download and cleanup"""
        self.is_cancelled = True
        Clock.schedule_once(lambda dt: self._remove_card(), 0)
        Clock.schedule_once(lambda dt: self.app.queue_manager.on_download_complete(self.download_id), 0)
    
    @staticmethod
    def _clean_string(text):
        """Remove ANSI color codes and clean string"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class QueueManager:
    """Manages download queue with concurrency limit"""
    
    def __init__(self, app):
        self.app = app
        self.active_downloads = {}
        self.waiting_queue = Queue()
        self.max_concurrent = 3
        self.lock = threading.Lock()
        
        # Load max concurrent from database
        self._load_settings()
    
    def _load_settings(self):
        """Load queue limit from database"""
        try:
            from db import db
            limit = db.get_setting("queue_limit")
            if limit:
                self.max_concurrent = int(limit)
        except Exception:
            pass
    
    def update_max_concurrent(self, value):
        """Update concurrent download limit"""
        with self.lock:
            self.max_concurrent = int(value)
            # Try to start waiting downloads
            self._process_queue()
    
    def add_download(self, url, download_type):
        """Add download to queue"""
        def show_toast(text):
            try:
                from kivymd.toast import toast as md_toast
                md_toast(text)
            except (ImportError, TypeError):
                print(f"[TOAST] {text}")
        
        download_id = f"dl_{int(time.time() * 1000)}"
        
        # Create task card
        from main import TaskCard
        task_card = TaskCard(
            filename="Waiting...",
            progress=0,
            speed="Queued",
            eta="--:--",
            download_id=download_id
        )
        
        # Add card to UI
        Clock.schedule_once(lambda dt: self.app.root.ids.task_container.add_widget(task_card), 0)
        
        # Create download task
        download_task = DownloadTask(url, download_type, task_card, self.app, download_id)
        
        with self.lock:
            if len(self.active_downloads) < self.max_concurrent:
                # Start immediately
                self.active_downloads[download_id] = download_task
                download_task.start()
                Clock.schedule_once(lambda dt: show_toast("Download started"), 0)
            else:
                # Add to waiting queue
                self.waiting_queue.put((download_id, download_task))
                Clock.schedule_once(lambda dt: show_toast("Added to queue"), 0)
    
    def on_download_complete(self, download_id):
        """Handle download completion and start next in queue"""
        with self.lock:
            if download_id in self.active_downloads:
                del self.active_downloads[download_id]
            
            # Check if all downloads are complete
            if len(self.active_downloads) == 0:
                Clock.schedule_once(lambda dt: setattr(self.app, 'is_active_download', False), 0)
            
            # Process waiting queue
            self._process_queue()
    
    def _process_queue(self):
        """Start next download from waiting queue if slot available"""
        while len(self.active_downloads) < self.max_concurrent and not self.waiting_queue.empty():
            try:
                download_id, download_task = self.waiting_queue.get_nowait()
                self.active_downloads[download_id] = download_task
                
                # Update card status
                Clock.schedule_once(lambda dt: setattr(download_task.task_card, 'speed', 'Starting...'), 0)
                
                # Start download
                download_task.start()
            except:
                break
    
    def pause_download(self, download_id):
        """Pause a download"""
        with self.lock:
            if download_id in self.active_downloads:
                self.active_downloads[download_id].pause()
    
    def resume_download(self, download_id):
        """Resume a download"""
        with self.lock:
            if download_id in self.active_downloads:
                self.active_downloads[download_id].resume()
    
    def cancel_download(self, download_id):
        """Cancel a download"""
        with self.lock:
            if download_id in self.active_downloads:
                self.active_downloads[download_id].cancel()
