"""
Database Manager for AnyLoad v1.1
Handles settings persistence and library management
Thread-safe for Android multi-threading
"""

import sqlite3
import os
from threading import Lock
from datetime import datetime


class DatabaseManager:
    """Thread-safe SQLite database manager"""
    
    def __init__(self):
        self.db_path = None
        self.lock = Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database with proper path for Android/Desktop"""
        try:
            # Try Android path first
            from android.storage import app_storage_path
            base_path = app_storage_path()
        except:
            # Fallback to desktop path
            base_path = os.path.expanduser("~/.anyload")
            os.makedirs(base_path, exist_ok=True)
        
        self.db_path = os.path.join(base_path, "anyload.db")
        self._create_tables()
        self._init_default_settings()
    
    def _get_connection(self):
        """Get thread-safe database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """Create settings and library tables"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Settings table (key-value pairs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            # Library table (downloaded files)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    size INTEGER,
                    date TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def _init_default_settings(self):
        """Initialize default settings if not exists"""
        defaults = {
            "queue_limit": "3",
            "wifi_only": "False",
            "download_path": "/sdcard/Download/AnyLoad"
        }
        
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for key, value in defaults.items():
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
            
            conn.commit()
            conn.close()
    
    def get_setting(self, key):
        """Get a setting value by key"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            return result["value"] if result else None
    
    def update_setting(self, key, value):
        """Update or insert a setting"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
            conn.commit()
            conn.close()
    
    def add_to_library(self, title, path, file_type, size=0):
        """Add a downloaded file to library"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                cursor.execute(
                    "INSERT INTO library (title, path, type, size, date) VALUES (?, ?, ?, ?, ?)",
                    (title, path, file_type, size, date)
                )
                conn.commit()
                conn.close()
                return True
            except sqlite3.IntegrityError:
                # File already exists in library
                conn.close()
                return False
    
    def get_library(self, file_type=None):
        """Get library items, optionally filtered by type"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if file_type:
                cursor.execute(
                    "SELECT * FROM library WHERE type = ? ORDER BY date DESC",
                    (file_type,)
                )
            else:
                cursor.execute("SELECT * FROM library ORDER BY date DESC")
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
    
    def delete_from_library(self, item_id):
        """Delete an item from library"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM library WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
    
    def clear_library(self):
        """Clear all library items"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM library")
            conn.commit()
            conn.close()
