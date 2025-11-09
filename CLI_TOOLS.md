# CLI Tools for Multi-Source Lyrics Selection

This document describes the new command-line tools for testing and using the multi-source lyrics download feature.

## Overview

The LRC Lyrics Downloader now includes two powerful CLI tools that allow you to:
1. View all available lyrics sources and their results
2. Interactively select and download lyrics from multiple sources with preview

## Tools

### 1. cli_show_all_sources.py - View All Sources' Results

This tool shows you what each lyrics source (NetEase, KuGou, QQ Music) finds for a given song.

**Usage:**
```bash
python3 cli_show_all_sources.py <artist> <title>
```

**Example:**
```bash
python3 cli_show_all_sources.py 周杰伦 青花瓷
```

**Output:**
- Detailed logs from each source's API calls
- Search results with match scores
- Lyrics fetching status (success/failure)
- Final summary showing all candidates sorted by score

**Example Output:**
```
================================================================================
多源歌词搜索 - 显示所有源的结果
================================================================================
搜索: 周杰伦 - 青花瓷
================================================================================

============================
来源: NetEaseSource
============================
✓ 找到 5 个候选

[1] 匹配分数:  18
    艺术家: 沈幼楚
    歌曲名: 青花瓷周杰伦（正式版）
    预览:
      [00:00.000] 作词 : 沈幼楚
      [00:00.000] 作曲 : 夜神鹿
      [00:00.000] 编曲 : 夜神鹿
    完整歌词: 25 行

============================
来源: KuGouSource
============================
✗ 未找到歌词候选

============================
来源: TencentQQSource
============================
✓ 找到 3 个候选

总结
============================
总共找到: 8 个候选歌词

排序结果 (按分数从高到低):
 1. [ 40] QQ Music     | 周杰伦                  | 青花瓷
 2. [ 18] NetEase      | 沈幼楚                  | 青花瓷周杰伦（正式版）
 3. [ 15] NetEase      | 周杰伦, 李玟              | 刀马旦
...
```

### 2. cli_download_multi_source.py - Interactive Download with Preview

This tool allows you to download lyrics while previewing candidates from all sources.

**Usage:**
```bash
# Download by searching artist and title
python3 cli_download_multi_source.py <artist> <title> [output_file]

# Download for an audio file (extracts metadata automatically)
python3 cli_download_multi_source.py <audio_file>
```

**Examples:**
```bash
# Search and download
python3 cli_download_multi_source.py 周杰伦 青花瓷
python3 cli_download_multi_source.py 周杰伦 青花瓷 lyrics.lrc

# Download for an audio file
python3 cli_download_multi_source.py song.mp3
```

**Interactive Session:**
```
================================================================================
多源歌词下载 - 收集所有源的候选
================================================================================
艺术家: 周杰伦
歌曲名: 青花瓷
================================================================================

正在从所有源收集歌词候选...

✓ 找到 5 个歌词候选

================================================================================
可用的歌词候选:
================================================================================

[1] 来源: NetEase
    艺术家: 沈幼楚
    歌曲名: 青花瓷周杰伦（正式版）
    匹配分数: 18
    预览:
      [00:00.000] 作词 : 沈幼楚
      [00:00.000] 作曲 : 夜神鹿
      [00:00.000] 编曲 : 夜神鹿

[2] 来源: NetEase
    艺术家: 周杰伦, 李玟
    歌曲名: 刀马旦
    匹配分数: 15
    预览:
      [00:00.000] 制作人 : 周杰伦
      [00:01.000] 作词 : 方文山
      [00:02.000] 作曲 : 周杰伦

================================================================================

请选择要下载的歌词 (1-5) 或 'q' 退出: 1

✓ 成功: 歌词已保存到 周杰伦 - 青花瓷.lrc
  来源: NetEase
  艺术家: 沈幼楚
  歌曲名: 青花瓷周杰伦（正式版）
  行数: 25
```

## Features

### Logging and Transparency

Both tools show detailed logs of what's happening:

- **Search Phase**: Shows which API was called and what keywords were searched
- **Matching Phase**: Displays match scores for all found songs
- **Lyrics Fetching**: Shows success/failure status for each candidate
- **Summary**: Lists all found candidates sorted by relevance score

### Multi-Source Collection

The tools automatically collect candidates from:
1. **NetEase Music** - Primary Chinese source
2. **KuGou Music** - Alternative Chinese source
3. **QQ Music** - Tencent's music platform

### Smart Matching Algorithm

Each source applies the same intelligent matching:
- Artist matching (exact, partial, or found in text)
- Title matching (exact, partial, or found in text)
- Penalties for unwanted versions (covers, live, instrumental)
- Score-based ranking for relevance

### Preview Functionality

For each candidate, you can see:
- Source platform
- Artist and song title
- Match score (how relevant it is)
- First 3 lines of the lyrics preview
- Total number of lines in the lyrics

## Use Cases

### 1. Verify Multi-Source Collection

Use `cli_show_all_sources.py` to:
- Test that all sources are being searched
- Verify scoring and matching logic
- Debug API connectivity issues
- See which sources have the song available

### 2. Download with User Selection

Use `cli_download_multi_source.py` to:
- Download lyrics while seeing all options
- Compare different versions from different sources
- Make an informed choice about which version to keep
- Batch download lyrics for multiple songs interactively

### 3. Process Audio Files

Use `cli_download_multi_source.py <audio_file>` to:
- Automatically extract metadata from music files
- Download matching lyrics
- Save directly as .lrc file in the same directory

## Integration with GUI

The GUI application (`main.py`) uses the same multi-source collection system:

1. Start the GUI: `python3 main.py`
2. Select a folder of music files
3. Click "Start Download"
4. For each file, a dialog appears showing all available lyrics sources
5. Select your preferred version
6. Download proceeds automatically

## Troubleshooting

### No candidates found

If you see "✗ 未找到任何歌词候选", this could mean:
- The song doesn't exist in any of the sources
- The artist/title combination is not recognized
- Try using different search terms or check metadata

### Some sources show no results

It's normal for some sources to not have results:
- KuGou: May have limited Chinese music library
- QQ Music: Copyright restrictions on some songs
- NetEase: Primary fallback source

### Low match scores

If all candidates have low scores (< 10):
- The metadata may be different from the source data
- Try manually correcting the artist/title metadata
- Use `cli_metadata_check.py` to analyze audio file metadata

## Tips

1. **For multiple files**: Use the GUI batch mode for efficiency
2. **For single songs**: Use CLI tools for quick testing
3. **For debugging**: Run `cli_show_all_sources.py` first to see what's available
4. **For bulk downloads**: Combine with shell scripts for automation

## Examples

### Example 1: Quick lookup of a song

```bash
python3 cli_show_all_sources.py 蔡徐坤 孤独的衍生物
```

This shows all available versions from all sources.

### Example 2: Interactive download

```bash
python3 cli_download_multi_source.py 蔡徐坤 孤独的衍生物
# Then select option 1, 2, 3, etc. to download
```

### Example 3: Batch processing with shell script

```bash
#!/bin/bash
for file in *.mp3; do
    python3 cli_download_multi_source.py "$file" << EOF
1
EOF
done
```

This downloads lyrics for all MP3 files, always selecting option 1.

### Example 4: Check metadata quality

```bash
python3 cli_metadata_check.py song1.mp3 song2.flac song3.wav
```

This analyzes metadata of audio files to ensure they're correct.

## Performance

- **NetEase search**: ~0.5-1 second per source
- **KuGou search**: ~0.5-1 second per source  
- **QQ Music search**: ~0.5-1 second per source
- **Total collection time**: ~3-5 seconds for all sources

The tools add ~1 second delay between source requests to avoid rate limiting.

## See Also

- `LOGGING_AND_TROUBLESHOOTING.md` - Detailed logging information
- `README.md` - Main project documentation
- `core/lyrics_downloader.py` - Core download logic
- `core/lrc_sources.py` - Individual source implementations
