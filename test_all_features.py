#!/usr/bin/env python3
"""Test script to verify all implemented features"""

print("=" * 60)
print("Testing All Implemented Features")
print("=" * 60)

# Test 1: Source Priority
print("\n[TEST 1] Source Priority Order")
print("-" * 60)
from core.lrc_sources import ALL_SOURCES
source_names = [s.__name__ for s in ALL_SOURCES]
expected = ['TencentQQSource', 'KuGouSource', 'NetEaseSource']
if source_names == expected:
    print("✓ PASS: Priority is QQ > KuGou > NetEase")
else:
    print(f"✗ FAIL: Expected {expected}, got {source_names}")

# Test 2: Multi-source candidates collection
print("\n[TEST 2] Multi-source Candidates Collection")
print("-" * 60)
from core.lyrics_downloader import LyricsDownloader
downloader = LyricsDownloader()

metadata = {'artist': '儿歌', 'title': '两只老虎'}
candidates = downloader.get_all_lyrics_candidates(metadata)

if candidates:
    print(f"✓ PASS: Collected {len(candidates)} candidates")
    sources = set(c['source'] for c in candidates)
    print(f"  Sources present: {sources}")
else:
    print("⚠ WARNING: No candidates found (may be network issue)")

# Test 3: GUI Dialog with preview
print("\n[TEST 3] GUI Dialog Implementation")
print("-" * 60)
try:
    from gui.main_window import LyricsSelectionDialog
    print("✓ PASS: LyricsSelectionDialog imports successfully")
    
    # Check if dialog has required methods
    dialog_methods = ['init_ui', 'on_selection_changed', 'get_selected_lyrics']
    for method in dialog_methods:
        if hasattr(LyricsSelectionDialog, method):
            print(f"  ✓ Method '{method}' exists")
        else:
            print(f"  ✗ Method '{method}' missing")
except ImportError as e:
    print(f"✗ FAIL: Cannot import LyricsSelectionDialog: {e}")

# Test 4: Right-click delete functionality
print("\n[TEST 4] Right-click Delete Functionality")
print("-" * 60)
try:
    from gui.main_window import MainWindow
    print("✓ PASS: MainWindow imports successfully")
    
    if hasattr(MainWindow, 'on_table_right_click'):
        print("  ✓ Method 'on_table_right_click' exists")
    else:
        print("  ✗ Method 'on_table_right_click' missing")
except ImportError as e:
    print(f"✗ FAIL: Cannot import MainWindow: {e}")

# Test 5: Code compilation
print("\n[TEST 5] Python Code Compilation")
print("-" * 60)
import py_compile
files_to_check = [
    'gui/main_window.py',
    'core/lyrics_downloader.py',
    'core/lrc_sources.py'
]
all_ok = True
for file_path in files_to_check:
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"  ✓ {file_path}")
    except py_compile.PyCompileError as e:
        print(f"  ✗ {file_path}: {e}")
        all_ok = False

if all_ok:
    print("✓ PASS: All files compile successfully")
else:
    print("✗ FAIL: Some files have compilation errors")

print("\n" + "=" * 60)
print("Test Summary Complete")
print("=" * 60)
