#!/usr/bin/env python3
"""
LRC Lyrics Downloader for macOS
Automatic LRC file downloader based on music metadata
"""

import sys
import warnings
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

# Suppress SSL warnings since we handle them gracefully in the sources
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LRC Lyrics Downloader")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
