# 🛠️ AnyLoad App - Developer & AI Master Guide

**Attention Developer / AI Assistant:** 
If you are reading this document, you are about to modify or build the "AnyLoad" Android App. This app uses Kivy, KivyMD, and yt-dlp. Android environments are highly sensitive. **Strictly follow the rules below to prevent Build Failures and App Crashes.**

---

## 📌 1. Environment & Version Requirements
To successfully compile and run this app without architecture conflicts, these exact versions MUST be maintained in `.github/workflows/main.yml` and `buildozer.spec`:

*   **Python Version (GitHub Actions):** `3.11`
*   **Java Version (JDK):** `17` (Temurin)
*   **Kivy Version:** `2.3.0`
*   **KivyMD Version:** `1.2.0` (Recommended for stability) OR `master` (If using master, strictly follow Material 3 rules).
*   **Android API:** `33`
*   **Android NDK:** `25b`
*   **Architectures:** `arm64-v8a, armeabi-v7a` (Must include 32-bit `armeabi-v7a` for budget devices like Unisoc processors).

---

## 🚨 2. App Crash Prevention (Runtime Errors)
If the app installs but crashes immediately (Silent Boot Crash) or crashes during an action, check these critical areas:

### A. Heavy Global Imports (The `yt-dlp` Trap)
*   **DON'T:** Never put `import yt_dlp` at the top of `main.py` globally. It requires heavy C-libraries (`sqlite3`, `libffi`, `openssl`). If these take too long to load on low-end devices, Android will kill the app on boot.
*   **DO:** Import heavy libraries locally inside the download thread (e.g., inside the `run()` method of the downloader class).

### B. FFmpeg & Subprocess Calls
*   **DON'T:** Do not use `subprocess.run(['ffmpeg', ...])` for thumbnail generation or audio conversion. Android does NOT have a native FFmpeg binary. The app will crash immediately with a "Command Not Found" error.
*   **DO:** Download media directly in target formats (e.g., `bestaudio[ext=m4a]`) or use native Android APIs via `pyjnius` for metadata retrieval.

### C. Graphics Context (Black Screen Crash)
*   Budget phones (like Realme/Unisoc) often fail to render Kivy's default OpenGL context.
*   **DO:** Always put `os.environ['KIVY_GRAPHICS'] = 'sdl2'` at the very top of `main.py` before any Kivy imports.

### D. Android 13+ Storage Permissions
*   **DON'T:** Do not rely only on `WRITE_EXTERNAL_STORAGE`. It doesn't work effectively on Android 11+.
*   **DO:** Request modern media permissions: `READ_MEDIA_VIDEO`, `READ_MEDIA_AUDIO`, and `POST_NOTIFICATIONS`. Delay the permission request using `Clock.schedule_once` after app boot to avoid freezing the UI.

---

## 🎨 3. UI & Design Crash Prevention (`ui.kv`)
UI bugs in Kivy will cause immediate app exits without providing standard Python tracebacks.

*   **Version Mismatch:** If using KivyMD `1.2.0`, use `font_style: "H6"` or `"Caption"`. If using KivyMD `master` (v2.0), you MUST use `font_style: "title-large"` or `"label-small"`. Mixing them will crash the app instantly.
*   **Missing Assets:** Hardcoding `source: "assets/logo.png"` will crash the app if the image is accidentally deleted, corrupted, or paths mismatch (case-sensitivity). Always use a safe check:
    ```yaml
    source: "assets/logo.png" if os.path.exists("assets/logo.png") else ""
    ```
*   **Layout Squashing:** Inside a `ScrollView`, if you use an `MDBoxLayout` without `adaptive_height: True` (or `size_hint_y: None` + `height: self.minimum_height`), all widgets will squash to the bottom and ruin the UI.

---

## 📦 4. Buildozer Spec Requirements (`buildozer.spec`)
For this app to run flawlessly with `yt-dlp` and network requests, the `requirements` line MUST look exactly like this:

```ini
requirements = python3, kivy==2.3.0, kivymd==1.2.0, pyjnius, android, requests, certifi, yt-dlp, sqlite3, libffi, openssl
(Notice the inclusion of sqlite3, libffi, and openssl — yt-dlp will crash globally without them).
Permissions Line:android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO, POST_NOTIFICATIONS

🛑 5. Build Fail Prevention (GitHub Actions)
If the GitHub Action fails before generating the APK, verify these:
YAML Syntax: .github/workflows/main.yml is extremely sensitive to indentation. Extra spaces or misplaced hyphens (-) will cause YAML parsing errors.
No Non-ASCII Characters: NEVER put Bengali or other non-English characters in buildozer.spec (even inside comments). It causes UnicodeError during the recipe fetching phase.
Missing Section Headers: buildozer.spec MUST start with [app] on line 1.
Network Errors: Sometimes fetching dependencies fails due to GitHub server issues. Re-run the job if a random timeout or "Broken Pipe" occurs.
[Note] Reply me always in Bangla.

End of Document. Code Smart, Build Responsibly! 🚀



