# Quick Start - CLI Tools

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Examples

### Example 1: See what all sources have for a song

```bash
python3 cli_show_all_sources.py 周杰伦 青花瓷
```

This will show:
- Search logs from NetEase, KuGou, and QQ Music
- Match scores for each found song
- Whether lyrics were successfully fetched
- Final summary of all candidates

### Example 2: Interactively download a song

```bash
python3 cli_download_multi_source.py 周杰伦 青花瓷
```

This will:
1. Collect lyrics from all sources
2. Show preview of each option
3. Ask you to select which version to download
4. Save the selected lyrics

### Example 3: Download lyrics for an audio file

```bash
python3 cli_download_multi_source.py my_song.mp3
```

This will:
1. Extract artist and title from the MP3
2. Find matching lyrics from all sources
3. Show previews for each option
4. Ask you to select and download
5. Save as `my_song.lrc` in the same directory

## What you'll see

### cli_show_all_sources.py output example:

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
    完整歌词: 25 行

============================
来源: KuGouSource
============================
✗ 未找到歌词候选

============================
来源: TencentQQSource
============================
Found 20 songs in search results
Top scores: [40, 40, 30, 30, 25]
Trying: 周杰伦 - 青花瓷 (score: 40)
✗ No lyrics available
...

================================================================================
总结 - 排序结果 (按分数从高到低)
================================================================================
1. [ 18] NetEase    | 沈幼楚 - 青花瓷周杰伦（正式版）
2. [ 15] NetEase    | 周杰伦, 李玟 - 刀马旦
3. [ 10] NetEase    | 刘芳 - 青花瓷
...
```

### cli_download_multi_source.py interactive session:

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

## Key Features

✓ **Multi-Source**: Automatically searches NetEase, KuGou, and QQ Music
✓ **Smart Matching**: Intelligent scoring to find the right song
✓ **Preview**: See first few lines of each candidate before downloading
✓ **User Choice**: Select which version you want
✓ **Transparent Logging**: See exactly what the API returns and why
✓ **CLI & GUI**: Use command line for quick tasks, GUI for batch operations

## Troubleshooting

**No candidates found?**
- The song might not be in any of the sources
- Try different search terms
- Check metadata with `python3 cli_metadata_check.py`

**Some sources show no results?**
- It's normal - not all sources have all songs
- Copyright restrictions may apply
- Try other sources

**Low match scores?**
- Your metadata might differ from the source
- Try manually correcting artist/title
- Use the exact names as they appear in the source

## Related Commands

```bash
# Check audio file metadata
python3 cli_metadata_check.py song.mp3

# Run GUI application
python3 main.py

# Run tests
python3 test_logging.py
python3 test_all_sources.py
```

## More Information

See `CLI_TOOLS.md` for detailed documentation and advanced usage.
