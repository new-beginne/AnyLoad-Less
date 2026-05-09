[app]
title = AnyLoad
package.name = anyload
package.domain = com.anyload

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.1

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pyjnius,android,requests,certifi,yt-dlp,sqlite3,libffi,openssl

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
