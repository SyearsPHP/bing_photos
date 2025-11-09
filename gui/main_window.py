"""
Main GUI Window for LRC Lyrics Downloader
"""

import os
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QLabel, QProgressBar,
    QMessageBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from core.music_processor import MusicProcessor
from core.lyrics_downloader import LyricsDownloader

class WorkerThread(QThread):
    progress_update = pyqtSignal(int, str)
    finished = pyqtSignal(list, list)
    
    def __init__(self, music_files: List[str], skip_existing: bool):
        super().__init__()
        self.music_files = music_files
        self.skip_existing = skip_existing
        self.downloader = LyricsDownloader()
        
    def run(self) -> None:
        successful: List[str] = []
        failed: List[str] = []
        
        total = len(self.music_files)
        for index, music_file in enumerate(self.music_files):
            try:
                self.progress_update.emit(index + 1, f"Processing: {os.path.basename(music_file)}")
                
                metadata = MusicProcessor.extract_metadata(music_file)
                if not metadata:
                    failed.append(os.path.basename(music_file))
                    continue
                
                lrc_path = MusicProcessor.get_lrc_path(music_file)
                if self.skip_existing and os.path.exists(lrc_path):
                    successful.append(os.path.basename(music_file))
                    continue
                
                if self.downloader.download_lyrics(metadata, lrc_path):
                    successful.append(os.path.basename(music_file))
                else:
                    failed.append(os.path.basename(music_file))
                    
            except Exception as e:
                print(f"Error processing {music_file}: {e}")
                failed.append(os.path.basename(music_file))
        
        self.finished.emit(successful, failed)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.music_files: List[str] = []
        self.worker_thread: Optional[WorkerThread] = None
        self.init_ui()
        
    def init_ui(self) -> None:
        self.setWindowTitle("LRC Lyrics Downloader")
        self.setGeometry(100, 100, 900, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Control Panel
        control_layout = QHBoxLayout()
        
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        control_layout.addWidget(self.select_folder_btn)
        
        self.skip_existing_cb = QCheckBox("Skip Existing LRC")
        self.skip_existing_cb.setChecked(True)
        control_layout.addWidget(self.skip_existing_cb)
        
        control_layout.addStretch()
        
        self.start_btn = QPushButton("Start Download")
        self.start_btn.clicked.connect(self.start_download)
        self.start_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)
        
        layout.addLayout(control_layout)
        
        # Status Label
        self.status_label = QLabel("No folder selected")
        layout.addWidget(self.status_label)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Filename", "Status", "Artist - Title"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)
        
        # Summary Label
        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)
        
    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if folder:
            self.music_files = MusicProcessor.get_music_files(folder)
            self.status_label.setText(f"Found {len(self.music_files)} music files")
            self.start_btn.setEnabled(len(self.music_files) > 0)
            self.populate_table()
            
    def populate_table(self) -> None:
        self.results_table.setRowCount(len(self.music_files))
        for idx, music_file in enumerate(self.music_files):
            filename_item = QTableWidgetItem(os.path.basename(music_file))
            status_item = QTableWidgetItem("Pending")
            metadata = MusicProcessor.extract_metadata(music_file)
            info_text = ""
            if metadata:
                info_text = f"{metadata.get('artist', 'Unknown')} - {metadata.get('title', 'Unknown')}"
            info_item = QTableWidgetItem(info_text)
            
            self.results_table.setItem(idx, 0, filename_item)
            self.results_table.setItem(idx, 1, status_item)
            self.results_table.setItem(idx, 2, info_item)
            
    def start_download(self) -> None:
        if not self.music_files:
            QMessageBox.warning(self, "Warning", "No music files selected")
            return
        
        self.select_folder_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.music_files))
        
        self.worker_thread = WorkerThread(self.music_files, self.skip_existing_cb.isChecked())
        self.worker_thread.progress_update.connect(self.update_progress)
        self.worker_thread.finished.connect(self.on_download_finished)
        self.worker_thread.start()
        
    def update_progress(self, current: int, message: str) -> None:
        self.progress_bar.setValue(current)
        self.status_label.setText(message)
        
    def on_download_finished(self, successful: List[str], failed: List[str]) -> None:
        self.progress_bar.setVisible(False)
        self.select_folder_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        
        success_count = len(successful)
        failed_count = len(failed)
        
        self.summary_label.setText(
            f"Completed! Success: {success_count}, Failed: {failed_count}"
        )
        
        if failed:
            failed_msg = "\n".join(failed)
            QMessageBox.information(
                self,
                "Download Complete",
                f"Success: {success_count}\nFailed: {failed_count}\n\nFailed files:\n{failed_msg}"
            )
        else:
            QMessageBox.information(
                self,
                "Download Complete",
                f"All {success_count} files processed successfully!"
            )
