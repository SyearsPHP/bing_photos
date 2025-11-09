# Multi-Source Lyrics Selection Implementation Notes

## Problem Statement

The original implementation only downloaded lyrics from the first source that had them. However, when NetEase (the primary source) didn't have a song due to copyright restrictions (e.g., 周杰伦 - 青花瓷), the download would fail even though other sources (KuGou, QQ Music) might have the song available.

## Solution

Implemented a multi-source lyrics selection feature that:
1. Collects lyrics candidates from **all sources** (NetEase, KuGou, QQ Music)
2. Shows a **preview dialog** with all available options
3. Lets users **select** their preferred version based on source and preview
4. Falls back to original method if no candidates found

## Implementation Details

### Core Changes

#### 1. `core/lrc_sources.py`
- Added `base64` import for QQ Music lyrics decoding
- Added `get_lyrics_candidates()` method to base `LRCSource` class
- Implemented `get_lyrics_candidates()` in each source class:
  - `NetEaseSource`: Searches up to 15 best matches, returns candidates with preview
  - `KuGouSource`: Same approach as NetEase
  - `TencentQQSource`: Same approach with base64 decoding handling

**Key Features**:
- Each candidate includes: source name, artist, title, match score, preview (first 3 lines), full lyrics
- Uses same scoring algorithm as original matching
- Returns candidates sorted by score (highest first)

#### 2. `core/lyrics_downloader.py`
- Added `get_all_lyrics_candidates()` method
- Collects candidates from all sources with 1-second delay between sources
- Sorts all candidates by score
- Returns combined list or empty list if nothing found

#### 3. `gui/main_window.py`
- Added `LyricsSelectionDialog` class:
  - Shows list of candidates with source, artist, title, and score
  - Displays preview of selected lyrics
  - Allows user to switch between candidates
  - Two buttons: "Download Selected" and "Skip This File"

- Modified `WorkerThread` class:
  - Changed to get candidates instead of direct download
  - Emits `request_user_selection` signal when candidates available
  - Waits for user response via `set_user_selection()`
  - Falls back to original method if no candidates found
  - Thread-safe communication with main window

- Modified `MainWindow` class:
  - Added `on_user_selection_needed()` to handle selection dialog
  - Connects worker thread signals to dialog handling

### Signal Flow

```
WorkerThread.run()
  → get_all_lyrics_candidates()
  → emit request_user_selection signal (if candidates found)
     ↓
MainWindow.on_user_selection_needed()
  → create and show LyricsSelectionDialog
  → wait for user response
     ↓
User selects or skips
  → call worker_thread.set_user_selection()
     ↓
WorkerThread continues
  → save selected lyrics or mark as failed
```

## Design Decisions

1. **Per-Source Limits**: Each source tries up to 15 best matches (score >= 5)
   - Avoids API rate limiting
   - Provides diverse options without overwhelming user

2. **Preview Length**: First 3 timestamped lines (out of first 5 lines)
   - Enough to verify correct song
   - Not too much to overwhelm dialog

3. **Blocking Wait**: Worker thread uses `msleep()` to wait for user
   - Simple and effective
   - Prevents processing next file before user chooses
   - Qt handles events, so UI remains responsive

4. **Fallback Behavior**: If no candidates found, uses original `download_lyrics()`
   - Ensures backward compatibility
   - Handles edge cases gracefully

5. **Score Sorting**: Candidates sorted by score, first selected by default
   - User still has choice
   - Best match shown first

## Testing

Structure validated with `test_structure.py`:
- All new methods exist and are callable
- All required imports present
- Proper inheritance and override

## Benefits

1. **Solves Copyright Issues**: Users can access lyrics from alternative sources
2. **User Control**: Users see options and make informed choices
3. **Transparency**: Match scores show why each version was selected
4. **Backward Compatible**: Falls back if no candidates
5. **Non-Intrusive**: Only shows dialog when multiple sources available

## Potential Enhancements

1. Add "Auto-select best" checkbox to skip dialog
2. Cache results for repeated searches
3. Show full lyrics in preview instead of just header
4. Add quality metrics beyond just score
5. Support more sources (Genius, KuWo, NetEase International)

## Files Modified

- `core/lrc_sources.py`: Added candidates collection methods
- `core/lyrics_downloader.py`: Added multi-source aggregation
- `gui/main_window.py`: Added dialog and signal handling

## Files Added

- `MULTI_SOURCE_SELECTION.md`: User-facing feature documentation
- `IMPLEMENTATION_NOTES.md`: This file
