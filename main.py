#!/usr/bin/env python3
"""
LRC Lyrics Downloader for macOS
Automatic LRC file downloader based on music metadata
"""

import sys
import os
import warnings
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

# Suppress SSL warnings since we handle them gracefully in the sources
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Suppress macOS Input Method Kit (IMK) mach port errors
# These are harmless warnings from PyQt6 interacting with macOS input framework
os.environ['QT_MAC_WANTS_LAYER'] = '1'
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LRC Lyrics Downloader")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
