# Multi-Source Lyrics Selection Feature

## Overview

This feature addresses the issue where single-source lyrics download could miss available lyrics from other platforms, particularly when the preferred source (NetEase) doesn't have certain songs due to licensing restrictions.

## How It Works

### User Experience

1. **Batch Download**: Users select a folder and start the download process
2. **Candidate Collection**: For each song, the downloader searches **all sources** (NetEase, KuGou, QQ Music) simultaneously
3. **Preview Dialog**: If multiple sources have the song, a dialog appears showing:
   - List of all available sources with artist name, song title, and match score
   - Preview of the first 3 lines of lyrics for selected option
   - User can switch between options to see different previews
4. **User Selection**: Users can:
   - **Download Selected**: Save the currently selected lyrics
   - **Skip This File**: Skip to the next file
5. **Fallback**: If no candidates found, falls back to original single-source method

### Architecture

#### New Methods

**`core/lrc_sources.py`**:
- Added `get_lyrics_candidates(artist, title)` to each LRCSource subclass
- Returns list of candidate dictionaries:
  ```python
  {
      'source': 'NetEase',        # or 'KuGou', 'QQ Music'
      'artist': 'Artist Name',
      'title': 'Song Title',
      'preview': '[00:00.00]...',  # First 3 lines with timestamps
      'full_lyrics': '[00:00.00]...', # Complete lyrics
      'score': 50                   # Match quality score
  }
  ```

**`core/lyrics_downloader.py`**:
- Added `get_all_lyrics_candidates(metadata)` method
- Collects candidates from all sources
- Sorts by score descending
- Returns combined list from all sources

**`gui/main_window.py`**:
- New `LyricsSelectionDialog` class for preview and selection
- Modified `WorkerThread` to:
  - Get candidates instead of immediately downloading
  - Emit `request_user_selection` signal when candidates available
  - Wait for user response via `set_user_selection()` callback
  - Save selected lyrics to file

### Benefits

1. **Solves Copyright Issues**: When NetEase doesn't have a song (e.g., 周杰伦), can use KuGou or QQ Music
2. **User Control**: Users can compare different sources and pick the best version
3. **Multiple Versions**: See different artists' interpretations if available
4. **Scoring Transparency**: See how well each match scored
5. **Backward Compatible**: Falls back to original method if only one source has lyrics

### Example Scenario

User downloads lyrics for "周杰伦 - 青花瓷":

1. NetEase doesn't have it (licensing)
2. KuGou has "沈幼楚 - 青花瓷周杰伦" (cover) - score 18
3. QQ Music has "周杰伦 - 青花瓷" - score 52

User sees both options and can choose the QQ Music version (higher score, exact match).

### Implementation Details

#### Multi-Source Collection
- Each source searches independently with 1-second delay between sources
- Collects up to 15 best matches per source (score >= 5)
- Returns all valid candidates with lyrics

#### Preview Generation
- Extracts first 5 lines of lyrics
- Filters to lines starting with `[` (timestamped)
- Shows first 3 such lines as preview

#### Thread Safety
- Uses Qt signals to communicate between WorkerThread and MainWindow
- Blocks worker thread while waiting for user response (via `msleep`)
- Unblocks when MainWindow calls `set_user_selection()`

#### Scoring
- Same intelligent matching algorithm used for all sources
- Candidates sorted by score for default selection
- User can see exact scores for each option

## Usage

No change needed for users - the feature works automatically:

1. Open application
2. Select music folder
3. Click "Start Download"
4. When multiple sources available, selection dialog appears
5. Choose desired version and click "Download Selected" or skip

## Technical Notes

### Performance
- Parallel searching from all sources (sequential with 1s delay)
- Network timeout: 15 seconds per request
- Typical response: 2-4 seconds for 3 sources

### Error Handling
- If source fails, continues to next source
- If no candidates found, uses original download method
- User can skip any file

### Future Enhancements
- Sort preview options by quality (song name match, artist match)
- Add "auto-select best" option
- Cache results for repeated searches
- Show full lyrics instead of preview only
