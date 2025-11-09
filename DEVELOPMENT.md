# Development Guide

## Setup Development Environment

### Prerequisites
- Python 3.7+
- macOS 10.12+

### Installation

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
python3 tests/test_music_processor.py
python3 tests/test_integration.py
```

## Project Structure

```
.
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
├── .gitignore                 # Git ignore file
├── LICENSE                    # MIT License
├── README.md                  # User documentation
├── DEVELOPMENT.md             # This file
├── gui/
│   ├── __init__.py
│   └── main_window.py         # PyQt6 GUI implementation
├── core/
│   ├── __init__.py
│   ├── music_processor.py     # Audio file metadata extraction
│   ├── lyrics_downloader.py   # Main download orchestration
│   └── lrc_sources.py         # LRC source implementations
└── tests/
    ├── __init__.py
    ├── test_music_processor.py
    └── test_integration.py
```

## Core Modules

### music_processor.py
Handles audio file discovery and metadata extraction.

**Key Functions:**
- `get_music_files(folder_path, recursive=True)` - Find all supported audio files
- `extract_metadata(music_file)` - Extract artist/title from audio file
- `get_lrc_path(music_file)` - Generate LRC file path
- `extract_metadata_from_filename(filename)` - Fallback filename parsing

**Supported Formats:**
- MP3 with ID3v2 tags
- FLAC with Vorbis comments
- WAV with ID3v2 or native tags

### lrc_sources.py
Implements multiple LRC source providers.

**Available Sources:**
- `NetEaseSource` - 网易云音乐
- `KuGouSource` - 酷狗音乐
- `TencentQQSource` - QQ音乐

Each source extends `LRCSource` base class with a `get_lyrics(artist, title)` method.

### lyrics_downloader.py
Orchestrates the download process across multiple sources.

**Key Class:**
- `LyricsDownloader` - Main downloader that tries all sources sequentially

### main_window.py
PyQt6 GUI implementation.

**Features:**
- Batch folder selection
- Music file discovery and preview
- Progress tracking with progress bar
- Worker thread for non-blocking UI
- Results summary with success/failure details

## Adding New LRC Sources

1. Create a new source class in `lrc_sources.py` extending `LRCSource`:

```python
class NewMusicSource(LRCSource):
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        # Implement your source API calls here
        # Return LRC content as string or None if not found
        pass
```

2. Add to `ALL_SOURCES` list in order of preference:

```python
ALL_SOURCES = [
    NetEaseSource,
    KuGouSource,
    TencentQQSource,
    NewMusicSource,  # Your new source
]
```

## Adding New Audio Format Support

1. Update `SUPPORTED_FORMATS` in `music_processor.py`:

```python
SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.m4a'}  # Add '.m4a'
```

2. Add metadata extraction in `extract_metadata()`:

```python
elif ext == '.m4a':
    from mutagen.mp4 import MP4
    audio = MP4(music_file)
    # Extract metadata
```

## API Rate Limiting

The downloader includes built-in rate limiting:
- 0.5 second delay between source attempts
- Prevents API blocking and respects server resources

To adjust, modify in `lyrics_downloader.py`:

```python
time.sleep(0.5)  # Change this value
```

## Testing

Run all tests:
```bash
python3 tests/test_music_processor.py
python3 tests/test_integration.py
```

Add new tests to maintain code quality and catch regressions.

## Debugging

Enable debug logging by modifying source files:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Common issues:
- **API errors**: Check internet connection and API status
- **Metadata not extracted**: Verify audio files have proper ID3/Vorbis tags
- **GUI won't start**: Ensure PyQt6 is properly installed

## Performance Considerations

- Batch processing uses worker threads to keep UI responsive
- Each source is tried sequentially with timeout (10 seconds)
- Failed downloads don't block subsequent sources
- File I/O is buffered for efficiency

## Future Improvements

- [ ] Add English lyrics support (Genius API)
- [ ] Implement fuzzy matching for better results
- [ ] Add proxy support for restricted networks
- [ ] Create command-line interface
- [ ] Support for more audio formats (M4A, OGG, etc.)
- [ ] Lyrics preview/validation before saving
- [ ] Playlist batch processing
- [ ] Settings/configuration UI

## Code Style

- Follow PEP 8 guidelines
- Use type hints in function signatures
- Add docstrings to classes and methods
- Minimize comments (code should be self-documenting)
- Use meaningful variable names

## Troubleshooting

### Import errors when running tests
```bash
# Make sure you're in the project root
cd /path/to/project
python3 tests/test_*.py
```

### Dependencies not installing
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### GUI not appearing on macOS
```bash
# Ensure PyQt6 is installed for macOS
pip install PyQt6
# Run from terminal directly
python3 main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.
