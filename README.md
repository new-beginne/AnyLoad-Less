# 📱 AnyLoad v1.1

**Premium Android Media Downloader** - Lightweight, crash-proof, and blazing fast.

![Build Status](https://github.com/YOUR_USERNAME/AnyLoad/workflows/Build%20AnyLoad%20APK/badge.svg)

## ✨ Features

- 🎥 **Auto Best Quality** - Smart video downloads
- 🎵 **Audio Only** - Extract audio from videos
- 📋 **Playlist Support** - Batch downloads
- 📊 **Real-time Progress** - Speed, ETA, and progress tracking
- 📚 **Built-in Library** - Organized media management
- 🌙 **Dark Theme** - Easy on the eyes (#0D0D0D + #00D2A0 teal)

## 🏗️ Tech Stack

- **Python 3.11**
- **Kivy 2.3.0**
- **KivyMD 1.2.0**
- **yt-dlp** (lazy-loaded)
- **SQLite3** for library management

## 🚀 Development Status

**Current Phase:** Phase 1 - App Skeleton & Navigation ✅

### Roadmap:
- [x] Phase 1: App Skeleton & Navigation
- [ ] Phase 2: UI Implementation
- [ ] Phase 3: Database & Settings Logic
- [ ] Phase 4: Download Engine & Queue Manager
- [ ] Phase 5: Android Native Features

## 📦 Download APK

Download the latest APK from [GitHub Actions Artifacts](https://github.com/YOUR_USERNAME/AnyLoad/actions) or [Releases](https://github.com/YOUR_USERNAME/AnyLoad/releases).

## 🛠️ Build Locally

### Prerequisites:
- Python 3.11
- Buildozer
- Android SDK (API 33)
- Android NDK 25b

### Desktop Test:
```bash
python main.py
```

### Build APK:
```bash
buildozer android debug
```

## 📱 Android Requirements

- **Min SDK:** 21 (Android 5.0)
- **Target SDK:** 33 (Android 13)
- **Architectures:** arm64-v8a, armeabi-v7a

## 🔒 Permissions

- `INTERNET` - Download media
- `WRITE_EXTERNAL_STORAGE` - Save files
- `READ_EXTERNAL_STORAGE` - Access library
- `ACCESS_NETWORK_STATE` - Check connectivity
- `WAKE_LOCK` - Prevent sleep during downloads

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

This project follows a strict phase-by-phase development methodology. Please check the current phase before contributing.

---

**Built with ❤️ using Kivy & KivyMD**
