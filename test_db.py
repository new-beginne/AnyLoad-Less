#!/usr/bin/env python3
"""
Test script for database functionality
Run this to verify database operations work correctly
"""

from db import db

print("=" * 50)
print("AnyLoad Database Test")
print("=" * 50)

# Test 1: Check default settings
print("\n1. Testing default settings...")
queue_limit = db.get_setting("queue_limit")
wifi_only = db.get_setting("wifi_only")
download_path = db.get_setting("download_path")

print(f"   Queue Limit: {queue_limit}")
print(f"   Wi-Fi Only: {wifi_only}")
print(f"   Download Path: {download_path}")

# Test 2: Update settings
print("\n2. Testing settings update...")
db.update_setting("queue_limit", 5)
db.update_setting("wifi_only", "True")
print(f"   Updated Queue Limit: {db.get_setting('queue_limit')}")
print(f"   Updated Wi-Fi Only: {db.get_setting('wifi_only')}")

# Test 3: Add library items
print("\n3. Testing library additions...")
success1 = db.add_to_library("Test Video.mp4", "/path/to/video.mp4", "video", 1024000)
success2 = db.add_to_library("Test Audio.mp3", "/path/to/audio.mp3", "audio", 512000)
print(f"   Video added: {success1}")
print(f"   Audio added: {success2}")

# Test 4: Retrieve library items
print("\n4. Testing library retrieval...")
videos = db.get_library("video")
audios = db.get_library("audio")
all_items = db.get_library()

print(f"   Total videos: {len(videos)}")
print(f"   Total audios: {len(audios)}")
print(f"   Total items: {len(all_items)}")

if videos:
    print(f"\n   Sample video: {videos[0]['title']}")
if audios:
    print(f"   Sample audio: {audios[0]['title']}")

# Test 5: Database path
print(f"\n5. Database location: {db.db_path}")

print("\n" + "=" * 50)
print("All tests completed!")
print("=" * 50)
