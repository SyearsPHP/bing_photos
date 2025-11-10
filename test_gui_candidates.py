#!/usr/bin/env python3
"""Test script to verify GUI dialog shows all candidates correctly"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import LyricsSelectionDialog

def test_dialog():
    app = QApplication(sys.argv)
    
    # Create sample candidates from different sources
    candidates = [
        {
            'source': 'QQ Music',
            'artist': '周杰伦',
            'title': '青花瓷',
            'preview': '[00:00.00] 灵动中国风\n[00:05.00] 青花瓷\n[00:10.00] 怎样描绘',
            'full_lyrics': '[00:00.00] 灵动中国风\n[00:05.00] 青花瓷\n[00:10.00] 怎样描绘\n[00:15.00] 这意象\n[00:20.00] 要不要酒\n' + '\n'.join(f'[{i:02d}:00.00] Line {i}' for i in range(21, 50)),
            'score': 40
        },
        {
            'source': 'KuGou',
            'artist': '周杰伦',
            'title': '青花瓷',
            'preview': '[00:00.50] 素胚勾勒出青花笔意\n[00:05.00] 尓留在手心里芬芳\n[00:10.00] 如传世的青花瓷',
            'full_lyrics': '[00:00.50] 素胚勾勒出青花笔意\n[00:05.00] 尓留在手心里芬芳\n[00:10.00] 如传世的青花瓷\n[00:15.00] 自己手中慢慢泛黄\n[00:20.00] 我想告诉你\n' + '\n'.join(f'[{i:02d}:00.50] Line {i}' for i in range(21, 50)),
            'score': 38
        },
        {
            'source': 'NetEase',
            'artist': '周杰伦',
            'title': '青花瓷',
            'preview': '[00:00.00] 青花瓷\n[00:05.00] 素胚勾勒出青花笔意\n[00:10.00] 尓留在手心里芬芳',
            'full_lyrics': '[00:00.00] 青花瓷\n[00:05.00] 素胚勾勒出青花笔意\n[00:10.00] 尓留在手心里芬芳\n[00:15.00] 如传世的青花瓷\n[00:20.00] 自己手中慢慢泛黄\n' + '\n'.join(f'[{i:02d}:00.00] Line {i}' for i in range(21, 50)),
            'score': 35
        }
    ]
    
    dialog = LyricsSelectionDialog("test_song.mp3", candidates)
    result = dialog.exec()
    
    if result:
        lyrics = dialog.get_selected_lyrics()
        print(f"Selected {len(lyrics)} characters of lyrics")
        print(f"Preview: {lyrics[:100]}...")
    else:
        print("Dialog cancelled")
    
    app.quit()

if __name__ == '__main__':
    test_dialog()
