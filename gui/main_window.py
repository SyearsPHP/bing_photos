"""
Main GUI Window for LRC Lyrics Downloader
"""

import os
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QLabel, QProgressBar,
    QMessageBox, QCheckBox, QSpinBox, QTabWidget, QGroupBox, QHeaderView,
    QDialog, QTextEdit, QComboBox, QListWidget, QListWidgetItem, QSplitter,
    QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEventLoop, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap
from core.music_processor import MusicProcessor
from core.lyrics_downloader import LyricsDownloader
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE

class LyricsSelectionDialog(QDialog):
    """Dialog for user to preview and select lyrics from multiple sources"""
    
    def __init__(self, filename: str, candidates: List[dict], parent=None):
        super().__init__(parent)
        self.filename = filename
        self.candidates = candidates
        self.selected_lyrics = None
        self.init_ui()
    
    def init_ui(self) -> None:
        self.setWindowTitle(f"Select Lyrics - {self.filename}")
        self.setGeometry(100, 100, 1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(f"Found {len(self.candidates)} lyrics source(s). Please select one:")
        layout.addWidget(title_label)
        
        # Main splitter with candidates list on left and preview on right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - candidates list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.candidates_list = QListWidget()
        for i, candidate in enumerate(self.candidates):
            source = candidate.get('source', 'Unknown')
            artist = candidate.get('artist', 'Unknown')
            title = candidate.get('title', 'Unknown')
            score = candidate.get('score', 0)
            item_text = f"[{source}] {artist} - {title} (score: {score})"
            item = QListWidgetItem(item_text)
            item.setData(1001, i)  # Store index
            self.candidates_list.addItem(item)
        
        self.candidates_list.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.candidates_list)
        splitter.addWidget(left_widget)
        
        # Right panel - preview with eye icon
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview header with eye icon
        preview_header = QHBoxLayout()
        preview_label = QLabel("👁️ Full Lyrics Preview:")
        preview_header.addWidget(preview_label)
        preview_header.addStretch()
        right_layout.addLayout(preview_header)
        
        # Preview text - show full lyrics
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        right_layout.addWidget(self.preview_text)
        splitter.addWidget(right_widget)
        
        # Set initial sizes (50-50 split)
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Select first item by default
        if self.candidates_list.count() > 0:
            self.candidates_list.setCurrentRow(0)
            self.on_selection_changed()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("Download Selected")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.skip_btn = QPushButton("Skip This File")
        self.skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.skip_btn)
        
        layout.addLayout(button_layout)
    
    def on_selection_changed(self) -> None:
        """Update preview when selection changes"""
        current_row = self.candidates_list.currentRow()
        if current_row >= 0:
            candidate = self.candidates[current_row]
            # Show full lyrics in preview
            full_lyrics = candidate.get('full_lyrics', '')
            self.preview_text.setPlainText(full_lyrics)
            self.selected_lyrics = full_lyrics
    
    def get_selected_lyrics(self) -> Optional[str]:
        """Get the full lyrics of the selected candidate"""
        return self.selected_lyrics

class WorkerThread(QThread):
    progress_update = pyqtSignal(int, str)
    request_user_selection = pyqtSignal(str, list)  # filename, candidates
    finished = pyqtSignal(list, list)
    
    def __init__(self, music_files: List[str], skip_existing: bool, parent_window=None):
        super().__init__()
        self.music_files = music_files
        self.skip_existing = skip_existing
        self.downloader = LyricsDownloader()
        self.parent_window = parent_window
        self.user_selected_lyrics = None
        self.user_action = None  # None means waiting for response
        self.event_loop = QEventLoop()
        
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
                
                # Get all lyrics candidates from all sources
                candidates = self.downloader.get_all_lyrics_candidates(metadata)
                
                if candidates:
                    # Request user selection
                    self.user_selected_lyrics = None
                    self.user_action = None
                    
                    # Emit signal to show dialog
                    self.request_user_selection.emit(os.path.basename(music_file), candidates)
                    
                    # Wait for user response
                    while self.user_action is None:
                        self.msleep(100)
                    
                    # Save the selected lyrics if user chose one
                    if self.user_selected_lyrics:
                        try:
                            with open(lrc_path, 'w', encoding='utf-8') as f:
                                f.write(self.user_selected_lyrics)
                            successful.append(os.path.basename(music_file))
                        except Exception as e:
                            print(f"Error saving lyrics for {music_file}: {e}")
                            failed.append(os.path.basename(music_file))
                    else:
                        failed.append(os.path.basename(music_file))
                else:
                    # Fall back to original method
                    if self.downloader.download_lyrics(metadata, lrc_path):
                        successful.append(os.path.basename(music_file))
                    else:
                        failed.append(os.path.basename(music_file))
                    
            except Exception as e:
                print(f"Error processing {music_file}: {e}")
                failed.append(os.path.basename(music_file))
        
        self.finished.emit(successful, failed)
    
    def set_user_selection(self, lyrics: Optional[str]):
        """Called by main window when user selects lyrics"""
        self.user_selected_lyrics = lyrics
        self.user_action = 'done'  # Signal that we're done waiting

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.music_files: List[str] = []
        self.review_files: List[str] = []
        self.worker_thread: Optional[WorkerThread] = None
        self.init_ui()
        
    def init_ui(self) -> None:
        self.setWindowTitle("LRC Lyrics Downloader")
        self.setGeometry(100, 100, 1200, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create Tab Widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Download Tab
        download_tab = QWidget()
        self.init_download_tab(download_tab)
        self.tab_widget.addTab(download_tab, "批量下载")
        
        # Metadata Review Tab
        review_tab = QWidget()
        self.init_review_tab(review_tab)
        self.tab_widget.addTab(review_tab, "元数据检查")
        
    def init_download_tab(self, tab_widget) -> None:
        layout = QVBoxLayout(tab_widget)
        
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
        
    def init_review_tab(self, tab_widget) -> None:
        layout = QVBoxLayout(tab_widget)
        
        # Control Panel for Review
        review_control_layout = QHBoxLayout()
        
        self.select_files_btn = QPushButton("选择音乐文件")
        self.select_files_btn.clicked.connect(self.select_files_for_review)
        review_control_layout.addWidget(self.select_files_btn)
        
        review_control_layout.addStretch()
        
        self.analyze_btn = QPushButton("分析元数据")
        self.analyze_btn.clicked.connect(self.analyze_metadata)
        self.analyze_btn.setEnabled(False)
        review_control_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(review_control_layout)
        
        # Status Label for Review
        self.review_status_label = QLabel("请选择要检查的音乐文件")
        layout.addWidget(self.review_status_label)
        
        # Metadata Review Table
        self.metadata_table = QTableWidget()
        self.metadata_table.setColumnCount(6)
        self.metadata_table.setHorizontalHeaderLabels([
            "文件名", "格式", "艺术家", "歌曲名", "问题", "原始数据"
        ])
        
        # Set column widths
        header = self.metadata_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # 文件名
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 格式
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 艺术家
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 歌曲名
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # 问题
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # 原始数据
        
        header.resizeSection(1, 60)  # 格式列固定宽度
        
        self.metadata_table.horizontalHeader().setStretchLastSection(False)
        layout.addWidget(self.metadata_table)
        
        # Review Summary Label
        self.review_summary_label = QLabel("")
        layout.addWidget(self.review_summary_label)
        
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
        
        # Enable right-click context menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.on_table_right_click)
            
    def start_download(self) -> None:
        if not self.music_files:
            QMessageBox.warning(self, "Warning", "No music files selected")
            return
        
        self.select_folder_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.music_files))
        
        self.worker_thread = WorkerThread(self.music_files, self.skip_existing_cb.isChecked(), self)
        self.worker_thread.progress_update.connect(self.update_progress)
        self.worker_thread.request_user_selection.connect(self.on_user_selection_needed)
        self.worker_thread.finished.connect(self.on_download_finished)
        self.worker_thread.start()
        
    def update_progress(self, current: int, message: str) -> None:
        self.progress_bar.setValue(current)
        self.status_label.setText(message)
    
    def on_table_right_click(self, position) -> None:
        """Handle right-click on table to delete row"""
        item = self.results_table.itemAt(position)
        if item is None:
            return
        
        row = item.row()
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("Delete")
        action = context_menu.exec(self.results_table.mapToGlobal(position))
        
        if action == delete_action:
            # Remove from music_files list and table
            if row < len(self.music_files):
                del self.music_files[row]
                self.results_table.removeRow(row)
                self.status_label.setText(f"Found {len(self.music_files)} music files")
                self.start_btn.setEnabled(len(self.music_files) > 0)
    
    def on_user_selection_needed(self, filename: str, candidates: List[dict]) -> None:
        """Show dialog for user to select lyrics"""
        dialog = LyricsSelectionDialog(filename, candidates, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_lyrics = dialog.get_selected_lyrics()
            self.worker_thread.set_user_selection(selected_lyrics)
        else:
            self.worker_thread.set_user_selection(None)
        
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
    
    def select_files_for_review(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择音乐文件", 
            "", 
            "音乐文件 (*.mp3 *.wav *.flac);;MP3 文件 (*.mp3);;WAV 文件 (*.wav);;FLAC 文件 (*.flac)"
        )
        if files:
            self.review_files = files
            self.review_status_label.setText(f"已选择 {len(files)} 个文件")
            self.analyze_btn.setEnabled(True)
            self.populate_metadata_table()
    
    def populate_metadata_table(self) -> None:
        self.metadata_table.setRowCount(len(self.review_files))
        
        for idx, file_path in enumerate(self.review_files):
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            
            # Default values
            format_text = ext[1:].upper()  # Remove dot and convert to upper
            artist_text = ""
            title_text = ""
            issues_text = "待分析"
            raw_data_text = "待分析"
            
            # Set basic info
            self.metadata_table.setItem(idx, 0, QTableWidgetItem(filename))
            self.metadata_table.setItem(idx, 1, QTableWidgetItem(format_text))
            self.metadata_table.setItem(idx, 2, QTableWidgetItem(artist_text))
            self.metadata_table.setItem(idx, 3, QTableWidgetItem(title_text))
            self.metadata_table.setItem(idx, 4, QTableWidgetItem(issues_text))
            self.metadata_table.setItem(idx, 5, QTableWidgetItem(raw_data_text))
    
    def analyze_metadata(self) -> None:
        if not self.review_files:
            return
        
        total_files = len(self.review_files)
        problematic_files = 0
        
        for idx, file_path in enumerate(self.review_files):
            try:
                filename = os.path.basename(file_path)
                ext = os.path.splitext(filename)[1].lower()
                
                # Get detailed metadata analysis
                analysis = self._detailed_metadata_analysis(file_path)
                
                # Update table with analysis results
                self.metadata_table.setItem(idx, 2, QTableWidgetItem(analysis['artist']))
                self.metadata_table.setItem(idx, 3, QTableWidgetItem(analysis['title']))
                self.metadata_table.setItem(idx, 4, QTableWidgetItem(analysis['issues']))
                self.metadata_table.setItem(idx, 5, QTableWidgetItem(analysis['raw_data']))
                
                if analysis['issues']:
                    problematic_files += 1
                    
            except Exception as e:
                self.metadata_table.setItem(idx, 2, QTableWidgetItem("错误"))
                self.metadata_table.setItem(idx, 3, QTableWidgetItem("错误"))
                self.metadata_table.setItem(idx, 4, QTableWidgetItem(f"分析失败: {str(e)}"))
                self.metadata_table.setItem(idx, 5, QTableWidgetItem(""))
                problematic_files += 1
        
        # Update summary
        good_files = total_files - problematic_files
        self.review_summary_label.setText(
            f"分析完成！正常: {good_files}, 有问题: {problematic_files}"
        )
    
    def _detailed_metadata_analysis(self, file_path):
        """Detailed metadata analysis to identify specific issues"""
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
                    
            elif ext == '.flac':
                audio = FLAC(file_path)
                raw_data_parts.append(f"Tags: {list(audio.keys())}")
                
                if 'artist' in audio:
                    artist_raw = audio['artist'][0] if isinstance(audio['artist'], list) else audio['artist']
                    result['artist'] = str(artist_raw)
                    raw_data_parts.append(f"ARTIST: {repr(artist_raw)}")
                    
                    if isinstance(artist_raw, bytes):
                        issues.append("艺术家为字节类型")
                    if '\x00' in str(artist_raw):
                        issues.append("艺术家包含空字符")
                    if not str(artist_raw).strip():
                        issues.append("艺术家为空")
                else:
                    issues.append("缺少艺术家标签")
                
                if 'title' in audio:
                    title_raw = audio['title'][0] if isinstance(audio['title'], list) else audio['title']
                    result['title'] = str(title_raw)
                    raw_data_parts.append(f"TITLE: {repr(title_raw)}")
                    
                    if isinstance(title_raw, bytes):
                        issues.append("歌曲名为字节类型")
                    if '\x00' in str(title_raw):
                        issues.append("歌曲名包含空字符")
                    if not str(title_raw).strip():
                        issues.append("歌曲名为空")
                else:
                    issues.append("缺少歌曲名标签")
                    
            elif ext == '.wav':
                audio = WAVE(file_path)
                if audio.tags:
                    raw_data_parts.append(f"Tags: {list(audio.tags.keys())}")
                    
                    if 'artist' in audio.tags:
                        artist_raw = audio.tags['artist'][0] if isinstance(audio.tags['artist'], list) else audio.tags['artist']
                        result['artist'] = str(artist_raw)
                        raw_data_parts.append(f"ARTIST: {repr(artist_raw)}")
                        
                        if isinstance(artist_raw, bytes):
                            issues.append("艺术家为字节类型")
                        if '\x00' in str(artist_raw):
                            issues.append("艺术家包含空字符")
                        if not str(artist_raw).strip():
                            issues.append("艺术家为空")
                    else:
                        issues.append("缺少艺术家标签")
                    
                    if 'title' in audio.tags:
                        title_raw = audio.tags['title'][0] if isinstance(audio.tags['title'], list) else audio.tags['title']
                        result['title'] = str(title_raw)
                        raw_data_parts.append(f"TITLE: {repr(title_raw)}")
                        
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
