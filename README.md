# 📱 AnyLoad v1.1

**Premium Android Media Downloader** - Lightweight, crash-proof, and blazing fast.

## ✨ Features

- 🎥 **Auto Best Quality** - Smart video downloads (1080p max)
- 🎵 **Audio Only** - Extract audio from videos (MP3)
- 📋 **Playlist Support** - Batch downloads
- 📊 **Real-time Progress** - Speed, ETA, and progress tracking
- 📚 **Built-in Library** - Organized media management with 3 sub-tabs
- 🌙 **Dark Theme** - OLED Black (#0D0D0D) + Teal (#00D2A0)
- ⚡ **Queue Management** - Concurrent downloads (1-5 configurable)
- 💾 **Database Persistence** - Settings and library saved automatically

## 🏗️ Tech Stack

- **Python 3.11**
- **Kivy 2.3.0**
- **KivyMD 1.2.0** (Material Design 2)
- **yt-dlp** (lazy-loaded for fast boot)
- **SQLite3** for persistence
- **Threading** for background downloads

## 🚀 Architecture Highlights

### Crash Prevention
- ✅ Graphics fix: `os.environ['KIVY_GRAPHICS'] = 'sdl2'`
- ✅ Lazy yt-dlp loading (imports only in worker thread)
- ✅ No FFmpeg subprocess calls
- ✅ `adaptive_height: True` in all ScrollViews
- ✅ `on_pause()` returns True for Android lifecycle

### Download Engine
- **Lazy Loading**: yt-dlp imported only inside download thread
- **Queue Management**: Respects concurrent limit (1-5)
- **ANSI Cleaning**: Regex removes color codes from progress strings
- **Memory Management**: `gc.collect()` after each download
- **Vanish Logic**: Task cards auto-remove at 100% and migrate to Library

### Database
- **Thread-safe**: Uses `threading.Lock()`
- **Settings**: queue_limit, wifi_only, download_path
- **Library**: title, path, type, size, date

## 📦 Project Structure

```
AnyLoad/
├── main.py                 # App lifecycle and UI bridge
├── ui.kv                   # Complete UI (KivyMD 1.2.0 syntax)
├── buildozer.spec          # Android build configuration
├── db/
│   ├── __init__.py
│   └── manager.py          # SQLite persistence
├── core/
│   ├── __init__.py
│   └── downloader.py       # Download engine + Queue manager
└── assets/
    └── logo.png            # App logo
```

## 🛠️ Build Instructions

### Prerequisites
- Python 3.11
- Buildozer
- Android SDK (API 33)
- Android NDK 25b

### Desktop Test
```bash
python main.py
```

### Build APK
```bash
buildozer android debug
```

### Build Release APK
```bash
buildozer android release
```

## 📱 Android Requirements

- **Min SDK:** 21 (Android 5.0)
- **Target SDK:** 33 (Android 13)
- **Architectures:** arm64-v8a, armeabi-v7a (includes 32-bit for budget devices)

## 🔒 Permissions

- `INTERNET` - Download media
- `WRITE_EXTERNAL_STORAGE` - Save files
- `READ_EXTERNAL_STORAGE` - Access library
- `READ_MEDIA_VIDEO` - Android 11+ video access
- `READ_MEDIA_AUDIO` - Android 11+ audio access
- `POST_NOTIFICATIONS` - Background download notifications
- `ACCESS_NETWORK_STATE` - Check connectivity
- `WAKE_LOCK` - Prevent sleep during downloads

## 🎨 UI Design

### Theme
- **Background**: OLED Black (#0D0D0D)
- **Accent**: Teal (#00D2A0)
- **Cards**: Dark Gray (#1A1A1A)

### Screens
1. **Splash** - 3-second animated logo
2. **Home** - URL input + 3 download buttons
3. **Tasks** - Active downloads with progress
4. **Library** - 3 tabs (Videos, Audio, Playlists)
5. **Configs** - Settings (Queue limit, Wi-Fi only, Path)

### Top Bar Animation
- 3 dots blink sequentially **only when downloads are active**
- Hidden when no downloads

## ⚙️ Configuration

### Queue Limit
- Slider: 1-5 concurrent downloads
- Saved to database
- Updates queue manager dynamically

### Wi-Fi Only Mode
- Toggle switch
- Prevents downloads on mobile data (Phase 5)

### Download Path
- Default: `/sdcard/Download/AnyLoad`
- Customizable (file picker in Phase 5)

## 🧪 Testing

### Verify Phase 4
```bash
python verify_phase4.py
```

### Check Database
```bash
python test_db.py
```

## 📝 Development Phases

- [x] **Phase 1**: App Skeleton & Navigation
- [x] **Phase 2**: UI Implementation
- [x] **Phase 3**: Database & Settings Logic
- [x] **Phase 4**: Download Engine & Queue Manager
- [ ] **Phase 5**: Android Native Features (File picker, Notifications)

## 🐛 Known Issues

### Desktop Testing
- KivyMD 2.0 compatibility issues on desktop
- Use `verify_phase4.py` for engine testing
- Full UI works perfectly on Android with KivyMD 1.2.0

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

This project follows strict phase-by-phase development. Please check current phase before contributing.

## 🔧 Troubleshooting

### App crashes on boot
- Check `os.environ['KIVY_GRAPHICS'] = 'sdl2'` is first line
- Verify yt-dlp is NOT imported globally

### Downloads fail
- Check internet connection
- Verify storage permissions granted
- Check logcat: `adb logcat -s python`

### UI squashed
- Ensure `adaptive_height: True` in ScrollView containers

## 📞 Support

For issues, check logcat:
```bash
adb logcat -s python
```

---

**Built with ❤️ using Kivy & KivyMD**

**Version**: 1.1  
**Last Updated**: 2026-05-11
