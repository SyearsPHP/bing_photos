#!/usr/bin/env python3
"""
命令行工具 - 多源歌词下载并预览选择
支持从所有源收集歌词候选，显示预览，让用户选择下载
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def download_multi_source_lyrics(artist: str, title: str, output_path: str = None):
    """
    从所有源下载歌词候选，显示预览，让用户选择
    """
    from core.lyrics_downloader import LyricsDownloader
    
    print("\n" + "="*80)
    print(f"多源歌词下载 - 收集所有源的候选")
    print("="*80)
    print(f"艺术家: {artist}")
    print(f"歌曲名: {title}")
    print("="*80 + "\n")
    
    metadata = {
        'artist': artist,
        'title': title
    }
    
    downloader = LyricsDownloader()
    
    # 获取所有源的候选
    print("正在从所有源收集歌词候选...\n")
    candidates = downloader.get_all_lyrics_candidates(metadata)
    
    if not candidates:
        print("\n✗ 未找到任何歌词候选")
        return False
    
    print(f"\n✓ 找到 {len(candidates)} 个歌词候选\n")
    
    # 显示候选列表
    print("="*80)
    print("可用的歌词候选:")
    print("="*80)
    
    for i, candidate in enumerate(candidates, 1):
        source = candidate.get('source', 'Unknown')
        artist_found = candidate.get('artist', 'Unknown')
        title_found = candidate.get('title', 'Unknown')
        score = candidate.get('score', 0)
        
        print(f"\n[{i}] 来源: {source}")
        print(f"    艺术家: {artist_found}")
        print(f"    歌曲名: {title_found}")
        print(f"    匹配分数: {score}")
        print(f"    预览:")
        
        preview = candidate.get('preview', '')
        if preview:
            for line in preview.split('\n')[:3]:
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"      (无预览)")
    
    print("\n" + "="*80)
    
    # 用户选择
    while True:
        try:
            choice = input(f"\n请选择要下载的歌词 (1-{len(candidates)}) 或 'q' 退出: ").strip()
            
            if choice.lower() == 'q':
                print("已取消")
                return False
            
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(candidates):
                selected = candidates[choice_idx]
                break
            else:
                print(f"请输入 1-{len(candidates)} 之间的数字")
        except ValueError:
            print("输入无效，请重试")
    
    # 获取完整歌词
    full_lyrics = selected.get('full_lyrics', '')
    
    if not full_lyrics:
        print("✗ 错误: 无法获取完整歌词")
        return False
    
    # 保存到文件
    if not output_path:
        output_path = f"{artist} - {title}.lrc"
    
    try:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_lyrics)
        
        print(f"\n✓ 成功: 歌词已保存到 {output_path}")
        print(f"  来源: {selected.get('source')}")
        print(f"  艺术家: {selected.get('artist')}")
        print(f"  歌曲名: {selected.get('title')}")
        print(f"  行数: {len(full_lyrics.split(chr(10)))}")
        
        return True
    
    except Exception as e:
        print(f"✗ 错误: 保存文件失败 - {e}")
        return False


def download_for_audio_file(audio_file: str):
    """
    为音乐文件下载歌词
    """
    from core.music_processor import MusicProcessor
    
    if not os.path.exists(audio_file):
        print(f"✗ 错误: 文件不存在 - {audio_file}")
        return False
    
    # 提取元数据
    metadata = MusicProcessor.extract_metadata(audio_file)
    
    if not metadata:
        print(f"✗ 错误: 无法提取音乐文件元数据")
        return False
    
    artist = metadata.get('artist', '').strip()
    title = metadata.get('title', '').strip()
    
    if not artist or not title:
        print(f"✗ 错误: 缺少艺术家或歌曲名")
        print(f"  艺术家: {artist}")
        print(f"  歌曲名: {title}")
        return False
    
    # 获取输出路径
    output_path = MusicProcessor.get_lrc_path(audio_file)
    
    print(f"音乐文件: {os.path.basename(audio_file)}")
    print(f"提取元数据: {artist} - {title}")
    print(f"输出路径: {output_path}\n")
    
    # 下载歌词
    return download_multi_source_lyrics(artist, title, output_path)


def main():
    """主函数"""
    
    if len(sys.argv) < 2:
        print("用法 1: python cli_download_multi_source.py <艺术家> <歌曲名> [输出文件]")
        print("用法 2: python cli_download_multi_source.py <音乐文件>")
        print("\n示例:")
        print("  python cli_download_multi_source.py 周杰伦 青花瓷")
        print("  python cli_download_multi_source.py 周杰伦 青花瓷 lyrics.lrc")
        print("  python cli_download_multi_source.py song.mp3")
        sys.exit(1)
    
    # 判断是歌曲搜索还是文件下载
    if len(sys.argv) == 2:
        # 可能是音乐文件
        arg = sys.argv[1]
        if os.path.isfile(arg) and arg.lower().endswith(('.mp3', '.wav', '.flac')):
            download_for_audio_file(arg)
        else:
            print(f"错误: 无法识别参数 - {arg}")
            print("请使用 '艺术家 歌曲名' 或指定一个音乐文件")
            sys.exit(1)
    
    elif len(sys.argv) >= 3:
        # 艺术家和歌曲名
        artist = sys.argv[1]
        title = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        download_multi_source_lyrics(artist, title, output_path)
    
    else:
        print("错误: 参数不正确")
        sys.exit(1)


if __name__ == "__main__":
    main()
