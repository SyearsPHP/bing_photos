# LRC Lyrics Downloader for macOS

A powerful batch LRC lyrics downloader for macOS with a user-friendly GUI. Automatically finds and downloads LRC files for your local music library based on music metadata (artist and title).

## Features

- **Batch Processing**: Download LRC files for multiple songs at once
- **Multi-Format Support**: Works with MP3, WAV, and FLAC audio files
- **Multiple Sources**: Searches lyrics from NetEase, KuGou, and Tencent QQ Music
- **GUI Interface**: Easy-to-use graphical interface for macOS
- **Smart Matching**: Uses music metadata (artist, title) to find matching lyrics
- **Error Handling**: Shows detailed results with success/failure statistics
- **Duplicate Prevention**: Option to skip files that already have LRC files
- **Metadata Review**: Analyze music file metadata to identify potential issues
- **Problem Detection**: Detects null characters, encoding issues, and missing tags

## Installation

### Prerequisites

- Python 3.7 or later
- macOS 10.12 or later

### Setup

1. Clone the repository:
```bash
git clone https://github.com/real-zony/ZonyLrcToolsX.git
cd ZonyLrcToolsX
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use setup.py:
```bash
pip install -e .
```

## Usage

### GUI Application

Run the application:
```bash
python3 main.py
```

The application now has two tabs:

#### Batch Download Tab
1. Click "Select Folder" to choose a directory containing your music files
2. Review the found music files and their metadata
3. (Optional) Check "Skip Existing LRC" to avoid overwriting existing lyrics
4. Click "Start Download" to begin batch processing
5. Monitor progress in the progress bar
6. Review results in the summary

#### Metadata Review Tab (New)
1. Click "选择音乐文件" to select specific music files for analysis
2. Click "分析元数据" to analyze the selected files
3. Review the detailed analysis in the table:
   - **文件名**: Music file name
   - **格式**: MP3/WAV/FLAC
   - **艺术家**: Extracted artist name
   - **歌曲名**: Extracted song title
   - **问题**: Detected issues (shows "正常" if no problems)
   - **原始数据**: Raw metadata for debugging
4. Check the summary for statistics on normal vs problematic files

### Command Line Tools

#### Metadata Check Tool
```bash
python cli_metadata_check.py song1.mp3 song2.flac
```

#### Test Script
```bash
python test_metadata.py
```

### Command Line (Future)

```bash
lrc-downloader --directory /path/to/music --skip-existing
```

## Supported Audio Formats

- **MP3**: With ID3v2 tags
- **FLAC**: With Vorbis comments
- **WAV**: With ID3v2 or WAV metadata tags

## Supported Metadata

The tool reads:
- Artist name
- Song title

Extracted from audio file tags using:
- ID3v2 for MP3 files (TPE1/TIT2 or ARTIST/TITLE)
- Vorbis comments for FLAC files (artist/title)
- ID3v2 or WAV tags for WAV files

## LRC Sources

The downloader tries multiple music streaming APIs in order:
1. **NetEase Music** (网易云音乐)
2. **KuGou Music** (酷狗音乐)
3. **Tencent QQ Music** (QQ音乐)

## Features in Detail

### Batch Processing
- Select any folder (recursively searches subdirectories by default)
- Process hundreds of songs in one batch
- Real-time progress feedback

### Smart Metadata Extraction
- Reads MP3 ID3 tags (TPE1, TIT2)
- Reads FLAC Vorbis comments
- Fallback to filename parsing (Artist - Title format)

### LRC File Handling
- Saves LRC files in the same directory as music files
- Uses identical filename as source music file (only extension changes)
- Preserves original file organization

## Troubleshooting

### LRC files not downloading
- Ensure your music files have proper metadata (artist and title)
- Check internet connection
- Some songs may not be available in any of the supported services
- Use the Metadata Review tab to check for metadata issues

### Wrong lyrics downloaded
- Verify that artist and title metadata are correct
- Consider removing the incorrect LRC file and trying again
- Use Metadata Review to identify encoding or character issues

### Metadata Issues
If songs fail to download despite having metadata, use the Metadata Review tab to check for:
- **Null characters** (\x00) in artist/title fields
- **Byte-type data** that needs proper decoding
- **Missing or empty tags**
- **Encoding problems** with non-UTF8 characters
- **Extra whitespace** in metadata fields

### Application won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python 3.7+ is installed: `python3 --version`

## Project Structure

```
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Setup configuration
├── cli_metadata_check.py  # Command-line metadata tool
├── test_metadata.py       # Test script for metadata functions
├── METADATA_REVIEW.md     # Detailed metadata review guide
├── gui/
│   ├── __init__.py
│   └── main_window.py     # GUI implementation with dual tabs
└── core/
    ├── __init__.py
    ├── music_processor.py  # Audio file processing with cleaning
    ├── lyrics_downloader.py # Main downloader logic
    └── lrc_sources.py     # LRC source implementations
```

## Performance Notes

- NetEase: Most reliable for Chinese songs
- KuGou: Good coverage, fast API
- Tencent QQ: Comprehensive database but complex API

Rate limiting is built-in to prevent API blocking (0.5s delay between sources).

## Known Limitations

- Requires proper metadata in audio files
- Some songs may not be available in any of the supported services
- API endpoints may change or become unavailable (community-maintained)
- No English lyrics support yet (Chinese music focused)

## Future Enhancements

- [ ] Support for more LRC sources
- [ ] Command-line interface
- [ ] English lyrics support (Genius API)
- [ ] Advanced search with fuzzy matching
- [ ] Proxy support
- [ ] Lyrics preview/editing
- [ ] Playlist support
- [ ] Scheduled automatic downloads

## License

MIT License - See LICENSE file for details

## References

- Original Windows project: [ZonyLrcToolsX](https://github.com/real-zony/ZonyLrcToolsX)
- Music metadata: [Mutagen library](https://mutagen.readthedocs.io/)
- NetEase Music API research
- KuGou Music API documentation
- QQ Music API references

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Disclaimer

This tool is for personal use only. Users are responsible for complying with the terms of service of the music platforms and copyright laws in their jurisdiction. The author is not responsible for misuse.
