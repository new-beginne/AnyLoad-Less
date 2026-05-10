#!/usr/bin/env python3
"""
Test script for Phase 4 - Download Engine
Verifies the structure without actually downloading
"""

print("=" * 60)
print("Phase 4 - Download Engine Test")
print("=" * 60)

# Test 1: Import core modules
print("\n1. Testing core module imports...")
try:
    from core import DownloadTask, QueueManager
    print("   ✓ DownloadTask imported")
    print("   ✓ QueueManager imported")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test 2: Check DownloadTask structure
print("\n2. Testing DownloadTask structure...")
try:
    # Check if methods exist
    methods = ['start', 'pause', 'resume', 'cancel', '_download_worker', '_progress_hook']
    for method in methods:
        if hasattr(DownloadTask, method):
            print(f"   ✓ Method '{method}' exists")
        else:
            print(f"   ✗ Method '{method}' missing")
except Exception as e:
    print(f"   ✗ Structure check failed: {e}")

# Test 3: Check QueueManager structure
print("\n3. Testing QueueManager structure...")
try:
    methods = ['add_download', 'on_download_complete', 'update_max_concurrent', 
               'pause_download', 'resume_download', 'cancel_download']
    for method in methods:
        if hasattr(QueueManager, method):
            print(f"   ✓ Method '{method}' exists")
        else:
            print(f"   ✗ Method '{method}' missing")
except Exception as e:
    print(f"   ✗ Structure check failed: {e}")

# Test 4: Verify lazy loading (yt-dlp should NOT be imported yet)
print("\n4. Testing lazy loading...")
import sys
if 'yt_dlp' in sys.modules:
    print("   ✗ WARNING: yt-dlp is already loaded (should be lazy)")
else:
    print("   ✓ yt-dlp is NOT loaded yet (correct lazy loading)")

# Test 5: Check database integration
print("\n5. Testing database integration...")
try:
    from db import db
    queue_limit = db.get_setting("queue_limit")
    print(f"   ✓ Queue limit from DB: {queue_limit}")
except Exception as e:
    print(f"   ✗ Database integration failed: {e}")

print("\n" + "=" * 60)
print("Phase 4 structure verification complete!")
print("=" * 60)
print("\nNext: Run 'python main.py' to test the full app")
