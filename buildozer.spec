[app]
title = AnyLoad
package.name = anyload
package.domain = com.anyload

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.1

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pyjnius,android,requests,certifi,yt-dlp,libffi,openssl

orientation = portrait
fullscreen = 0

# App Icon and Splash Screen
icon.filename = %(source.dir)s/assets/logo.png
presplash.filename = %(source.dir)s/assets/logo.png
android.presplash_color = #0D0D0D

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.skip_update = False
android.release_artifact = apk

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
