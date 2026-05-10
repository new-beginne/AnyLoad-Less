# ANYLOAD APP - GLOBAL AI RULES
You are an Expert Python, Kivy, and Android Developer. Whenever I ask you to write or modify code for the "AnyLoad" project, you MUST strictly follow these global rules. Failure to do so will cause Android build failures and crashes.

## 1. TECH STACK & VERSIONS
- Python 3.11
- Kivy 2.3.0
- KivyMD 1.2.0 (STRICTLY use v1.2.0. Do NOT use KivyMD 2.0 / Material 3 syntax. Use `font_style: "Caption"`, `"Subtitle1"`, `"H6"`. NEVER use `"body-small"`).

## 2. CRASH PREVENTION (MANDATORY)
- Graphics Fix: The VERY FIRST LINE of `main.py` must be: `import os; os.environ['KIVY_GRAPHICS'] = 'sdl2'`.
- Lazy Loading: NEVER `import yt_dlp` globally at the top of the file. Import it locally inside the background download thread to prevent boot timeouts.
- No FFmpeg: Do NOT use `subprocess.run(['ffmpeg'])`. Android lacks this binary natively.
- Anti-Kill: Always include `def on_pause(self): return True` in the MDApp class.
- UI Squashing: Inside `ScrollView` -> `MDBoxLayout`, always use `adaptive_height: True`.

## 3. UI/UX GUIDELINES
- Theme: Pure Dark (`#0D0D0D`) with Teal accents (`#00D2A0`).
- No Tofu: Use Google `NotoSans-Regular.ttf` for global Unicode support.

## 4. DEVELOPMENT WORKFLOW
- PROTOTYPE METHOD: NEVER generate the entire app at once. We will build phase by phase.
- Always provide the code for ONE specific phase, tell me how to test it, and STOP. Wait for my "Success" report before moving to the next phase.