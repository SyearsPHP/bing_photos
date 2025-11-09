#!/usr/bin/env python3
"""
LRC Lyrics Downloader for macOS
Automatic LRC file downloader based on music metadata
"""

import sys
import urllib3
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LRC Lyrics Downloader")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
