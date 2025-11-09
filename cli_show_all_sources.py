#!/usr/bin/env python3
"""
命令行工具 - 显示所有源的歌词搜索结果和日志
用于调试和查看每个源找到了什么
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def show_all_sources_results(artist: str, title: str):
    """
    从所有源搜索歌词，显示详细结果和日志
    """
    from core.lrc_sources import ALL_SOURCES
    
    print("\n" + "="*100)
    print(f"多源歌词搜索 - 显示所有源的结果")
    print("="*100)
    print(f"搜索: {artist} - {title}")
    print("="*100 + "\n")
    
    all_results = []
    
    # 遍历所有源
    for source_class in ALL_SOURCES:
        source = source_class()
        source_name = source.__class__.__name__
        
        print(f"\n{'='*100}")
        print(f"来源: {source_name}")
        print(f"{'='*100}")
        
        try:
            # 调用 get_lyrics_candidates 获取候选
            candidates = source.get_lyrics_candidates(artist, title)
            
            if not candidates:
                print(f"✗ 未找到歌词候选")
                continue
            
            print(f"✓ 找到 {len(candidates)} 个候选\n")
            
            # 显示每个候选
            for i, candidate in enumerate(candidates, 1):
                all_results.append(candidate)
                
                source_name_cand = candidate.get('source', 'Unknown')
                artist_found = candidate.get('artist', 'Unknown')
                title_found = candidate.get('title', 'Unknown')
                score = candidate.get('score', 0)
                preview = candidate.get('preview', '')
                
                print(f"[{i}] 匹配分数: {score:3d}")
                print(f"    艺术家: {artist_found}")
                print(f"    歌曲名: {title_found}")
                print(f"    预览:")
                
                if preview:
                    for line in preview.split('\n'):
                        if line.strip():
                            print(f"      {line}")
                else:
                    print(f"      (无预览)")
                
                # 显示完整歌词长度
                full_lyrics = candidate.get('full_lyrics', '')
                lines_count = len(full_lyrics.split('\n'))
                print(f"    完整歌词: {lines_count} 行")
                print()
        
        except Exception as e:
            print(f"✗ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 总结
    print(f"\n{'='*100}")
    print(f"总结")
    print(f"{'='*100}")
    print(f"总共找到: {len(all_results)} 个候选歌词")
    
    if all_results:
        # 按分数排序
        all_results_sorted = sorted(all_results, key=lambda x: x.get('score', 0), reverse=True)
        
        print(f"\n排序结果 (按分数从高到低):")
        print(f"{'-'*100}")
        
        for i, candidate in enumerate(all_results_sorted, 1):
            source = candidate.get('source', 'Unknown')
            artist_found = candidate.get('artist', 'Unknown')
            title_found = candidate.get('title', 'Unknown')
            score = candidate.get('score', 0)
            
            print(f"{i:2d}. [{score:3d}] {source:15s} | {artist_found:20s} | {title_found}")
    
    print(f"\n{'='*100}\n")
    
    return all_results


def main():
    """主函数"""
    
    if len(sys.argv) < 3:
        print("用法: python cli_show_all_sources.py <艺术家> <歌曲名>")
        print("\n示例:")
        print("  python cli_show_all_sources.py 周杰伦 青花瓷")
        print("  python cli_show_all_sources.py 'Ed Sheeran' 'Shape of You'")
        sys.exit(1)
    
    artist = sys.argv[1]
    title = sys.argv[2]
    
    show_all_sources_results(artist, title)


if __name__ == "__main__":
    main()
