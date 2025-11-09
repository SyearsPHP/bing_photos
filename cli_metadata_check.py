#!/usr/bin/env python3
"""
命令行元数据检查工具
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_file_metadata(file_path):
    """分析单个文件的元数据"""
    from core.music_processor import MusicProcessor
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.wave import WAVE
    
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    print(f"\n=== 分析文件: {filename} ===")
    print(f"格式: {ext.upper()}")
    
    # 标准提取
    metadata = MusicProcessor.extract_metadata(file_path)
    print(f"标准提取结果: {metadata}")
    
    # 详细分析
    try:
        issues = []
        raw_data = []
        artist = ""
        title = ""
        
        if ext == '.mp3':
            audio = MP3(file_path)
            if audio.tags:
                raw_data.append(f"Tags: {list(audio.tags.keys())}")
                
                # 检查艺术家
                if 'TPE1' in audio.tags:
                    artist_raw = audio.tags['TPE1']
                    artist = str(artist_raw)
                    raw_data.append(f"TPE1: {repr(artist_raw)}")
                elif 'ARTIST' in audio.tags:
                    artist_raw = audio.tags['ARTIST']
                    artist = str(artist_raw)
                    raw_data.append(f"ARTIST: {repr(artist_raw)}")
                else:
                    issues.append("缺少艺术家标签")
                
                # 检查歌曲名
                if 'TIT2' in audio.tags:
                    title_raw = audio.tags['TIT2']
                    title = str(title_raw)
                    raw_data.append(f"TIT2: {repr(title_raw)}")
                elif 'TITLE' in audio.tags:
                    title_raw = audio.tags['TITLE']
                    title = str(title_raw)
                    raw_data.append(f"TITLE: {repr(title_raw)}")
                else:
                    issues.append("缺少歌曲名标签")
            else:
                issues.append("没有元数据标签")
                
        elif ext == '.flac':
            audio = FLAC(file_path)
            raw_data.append(f"Tags: {list(audio.keys())}")
            
            if 'artist' in audio:
                artist_raw = audio['artist'][0] if isinstance(audio['artist'], list) else audio['artist']
                artist = str(artist_raw)
                raw_data.append(f"ARTIST: {repr(artist_raw)}")
            else:
                issues.append("缺少艺术家标签")
            
            if 'title' in audio:
                title_raw = audio['title'][0] if isinstance(audio['title'], list) else audio['title']
                title = str(title_raw)
                raw_data.append(f"TITLE: {repr(title_raw)}")
            else:
                issues.append("缺少歌曲名标签")
                
        elif ext == '.wav':
            audio = WAVE(file_path)
            if audio.tags:
                raw_data.append(f"Tags: {list(audio.tags.keys())}")
                
                if 'artist' in audio.tags:
                    artist_raw = audio.tags['artist'][0] if isinstance(audio.tags['artist'], list) else audio.tags['artist']
                    artist = str(artist_raw)
                    raw_data.append(f"ARTIST: {repr(artist_raw)}")
                else:
                    issues.append("缺少艺术家标签")
                
                if 'title' in audio.tags:
                    title_raw = audio.tags['title'][0] if isinstance(audio.tags['title'], list) else audio.tags['title']
                    title = str(title_raw)
                    raw_data.append(f"TITLE: {repr(title_raw)}")
                else:
                    issues.append("缺少歌曲名标签")
            else:
                issues.append("没有元数据标签")
        
        # 检查常见问题
        if artist:
            if isinstance(artist, bytes):
                issues.append("艺术家为字节类型")
            if '\x00' in artist:
                issues.append("艺术家包含空字符")
            if not artist.strip():
                issues.append("艺术家为空")
            if artist != artist.strip():
                issues.append("艺术家有多余空格")
        
        if title:
            if isinstance(title, bytes):
                issues.append("歌曲名为字节类型")
            if '\x00' in title:
                issues.append("歌曲名包含空字符")
            if not title.strip():
                issues.append("歌曲名为空")
            if title != title.strip():
                issues.append("歌曲名有多余空格")
        
        print(f"艺术家: '{artist}'")
        print(f"歌曲名: '{title}'")
        print(f"问题: {'; '.join(issues) if issues else '正常'}")
        print(f"原始数据: {' | '.join(raw_data)}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"分析错误: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python cli_metadata_check.py <音乐文件路径...>")
        print("示例: python cli_metadata_check.py song1.mp3 song2.flac")
        sys.exit(1)
    
    print("=== LRC 歌词下载器 - 命令行元数据检查工具 ===")
    
    total_files = len(sys.argv) - 1
    good_files = 0
    
    for i, file_path in enumerate(sys.argv[1:], 1):
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 - {file_path}")
            continue
        
        if analyze_file_metadata(file_path):
            good_files += 1
    
    print(f"\n=== 分析完成 ===")
    print(f"总文件数: {total_files}")
    print(f"正常文件: {good_files}")
    print(f"问题文件: {total_files - good_files}")

if __name__ == "__main__":
    main()