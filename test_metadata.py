#!/usr/bin/env python3
"""
Test script for metadata analysis functionality
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.music_processor import MusicProcessor

def test_metadata_cleaning():
    """Test the metadata cleaning function"""
    print("=== 测试元数据清理功能 ===\n")
    
    # Import the cleaning function
    from core.music_processor import _clean_metadata_string
    
    test_cases = [
        ("Normal Text", "Normal Text"),
        ("  Text with spaces  ", "Text with spaces"),
        ("Text\x00with\x00nulls", "Textwithnulls"),
        ("", None),
        (None, None),
        (b"Byte text", "Byte text"),
        (b"Byte\x00text", "Bytetext"),
        ("   ", None),
        ("\x00\x00\x00", None),
    ]
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = _clean_metadata_string(input_text)
        status = "✓" if result == expected else "✗"
        print(f"测试 {i}: {status}")
        print(f"  输入: {repr(input_text)}")
        print(f"  期望: {repr(expected)}")
        print(f"  结果: {repr(result)}")
        print()

def analyze_metadata_detailed(file_path):
    """Detailed metadata analysis similar to the GUI function"""
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    result = {
        'artist': '',
        'title': '',
        'issues': '',
        'raw_data': ''
    }
    
    try:
        issues = []
        raw_data_parts = []
        
        if ext == '.mp3':
            audio = MP3(file_path)
            if audio.tags:
                raw_data_parts.append(f"Tags: {list(audio.tags.keys())}")
                
                # Check artist tags
                artist_raw = None
                if 'TPE1' in audio.tags:
                    artist_raw = audio.tags['TPE1']
                    raw_data_parts.append(f"TPE1: {repr(artist_raw)}")
                elif 'ARTIST' in audio.tags:
                    artist_raw = audio.tags['ARTIST']
                    raw_data_parts.append(f"ARTIST: {repr(artist_raw)}")
                
                # Check title tags
                title_raw = None
                if 'TIT2' in audio.tags:
                    title_raw = audio.tags['TIT2']
                    raw_data_parts.append(f"TIT2: {repr(title_raw)}")
                elif 'TITLE' in audio.tags:
                    title_raw = audio.tags['TITLE']
                    raw_data_parts.append(f"TITLE: {repr(title_raw)}")
                
                # Analyze artist
                if artist_raw:
                    result['artist'] = str(artist_raw)
                    if isinstance(artist_raw, bytes):
                        issues.append("艺术家为字节类型")
                    if '\x00' in str(artist_raw):
                        issues.append("艺术家包含空字符")
                    if not str(artist_raw).strip():
                        issues.append("艺术家为空")
                else:
                    issues.append("缺少艺术家标签")
                
                # Analyze title
                if title_raw:
                    result['title'] = str(title_raw)
                    if isinstance(title_raw, bytes):
                        issues.append("歌曲名为字节类型")
                    if '\x00' in str(title_raw):
                        issues.append("歌曲名包含空字符")
                    if not str(title_raw).strip():
                        issues.append("歌曲名为空")
                else:
                    issues.append("缺少歌曲名标签")
            else:
                issues.append("没有元数据标签")
                raw_data_parts.append("No tags found")
        
        # Check for common issues
        if result['artist'] and result['title']:
            # Check for encoding issues
            try:
                result['artist'].encode('utf-8')
                result['title'].encode('utf-8')
            except UnicodeEncodeError:
                issues.append("编码问题")
            
            # Check for excessive whitespace
            if result['artist'] != result['artist'].strip():
                issues.append("艺术家有多余空格")
            if result['title'] != result['title'].strip():
                issues.append("歌曲名有多余空格")
            
            # Check for special characters that might cause issues
            problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
            for char in problematic_chars:
                if char in result['artist'] or char in result['title']:
                    issues.append(f"包含不可见字符: {repr(char)}")
        
        result['issues'] = '; '.join(issues) if issues else '正常'
        result['raw_data'] = ' | '.join(raw_data_parts)
        
    except Exception as e:
        result['issues'] = f"分析错误: {str(e)}"
        result['raw_data'] = ""
    
    return result

def main():
    print("=== LRC 歌词下载器 - 元数据检查功能测试 ===\n")
    
    # Test metadata cleaning function
    test_metadata_cleaning()
    
    print("=== 功能说明 ===")
    print("\n新增的元数据检查功能包含以下特点:")
    print("1. 双标签页界面：'批量下载' 和 '元数据检查'")
    print("2. 元数据检查功能可以:")
    print("   - 选择多个音乐文件进行分析")
    print("   - 检测常见的元数据问题：")
    print("     * 空字符 (\\x00) 问题")
    print("     * 字节类型数据")
    print("     * 空白或缺失的标签")
    print("     * 编码问题")
    print("     * 多余空格")
    print("   - 显示原始元数据用于调试")
    print("   - 提供详细的问题描述")
    print()
    print("=== 使用方法 ===")
    print("1. 运行主程序: python main.py")
    print("2. 点击 '元数据检查' 标签页")
    print("3. 点击 '选择音乐文件' 按钮选择要检查的音乐文件")
    print("4. 点击 '分析元数据' 按钮查看详细分析结果")
    print("5. 表格会显示每个文件的元数据问题和原始数据")
    print("6. 底部会统计正常文件和有问题文件的数量")
    print()
    print("=== 表格列说明 ===")
    print("• 文件名：音乐文件的名称")
    print("• 格式：MP3、WAV、FLAC")
    print("• 艺术家：提取的艺术家名称")
    print("• 歌曲名：提取的歌曲名称")
    print("• 问题：检测到的具体问题（如无问题则显示'正常'）")
    print("• 原始数据：用于调试的原始元数据信息")

if __name__ == "__main__":
    main()