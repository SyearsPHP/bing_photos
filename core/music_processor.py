"""
Music file processor for extracting metadata from audio files
"""

import os
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE

SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac'}

class MusicProcessor:
    @staticmethod
    def get_music_files(folder_path, recursive=True):
        """
        Get all supported music files from a folder
        """
        music_files = []
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in SUPPORTED_FORMATS:
                        music_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                filepath = os.path.join(folder_path, file)
                if os.path.isfile(filepath) and os.path.splitext(file)[1].lower() in SUPPORTED_FORMATS:
                    music_files.append(filepath)
        
        return sorted(music_files)
    
    @staticmethod
    def extract_metadata(music_file):
        """
        Extract artist and title from music file metadata
        Returns dict with 'artist' and 'title' keys, or None if failed
        """
        try:
            ext = os.path.splitext(music_file)[1].lower()
            
            if ext == '.mp3':
                audio = MP3(music_file)
                # Try different ID3 tag formats
                artist = None
                title = None
                
                if audio.tags:
                    # Try TPE1 (lead performer) first
                    if 'TPE1' in audio.tags:
                        artist = str(audio.tags['TPE1'])
                    # Fallback to ARTIST
                    elif 'ARTIST' in audio.tags:
                        artist = str(audio.tags['ARTIST'])
                    
                    # Try TIT2 (title) first
                    if 'TIT2' in audio.tags:
                        title = str(audio.tags['TIT2'])
                    # Fallback to TITLE
                    elif 'TITLE' in audio.tags:
                        title = str(audio.tags['TITLE'])
                
                if artist and title:
                    return {
                        'artist': artist.strip(),
                        'title': title.strip(),
                        'format': 'mp3'
                    }
            
            elif ext == '.flac':
                audio = FLAC(music_file)
                artist = None
                title = None
                
                if 'artist' in audio:
                    artist = audio['artist'][0] if isinstance(audio['artist'], list) else audio['artist']
                
                if 'title' in audio:
                    title = audio['title'][0] if isinstance(audio['title'], list) else audio['title']
                
                if artist and title:
                    return {
                        'artist': artist.strip(),
                        'title': title.strip(),
                        'format': 'flac'
                    }
            
            elif ext == '.wav':
                audio = WAVE(music_file)
                artist = None
                title = None
                
                if audio.tags:
                    if 'artist' in audio.tags:
                        artist = audio.tags['artist'][0] if isinstance(audio.tags['artist'], list) else audio.tags['artist']
                    
                    if 'title' in audio.tags:
                        title = audio.tags['title'][0] if isinstance(audio.tags['title'], list) else audio.tags['title']
                
                if artist and title:
                    return {
                        'artist': artist.strip(),
                        'title': title.strip(),
                        'format': 'wav'
                    }
            
            return None
            
        except Exception as e:
            print(f"Error extracting metadata from {music_file}: {e}")
            return None
    
    @staticmethod
    def get_lrc_path(music_file):
        """
        Get the LRC file path for a music file
        """
        base, ext = os.path.splitext(music_file)
        return base + '.lrc'
    
    @staticmethod
    def extract_metadata_from_filename(filename):
        """
        Extract artist and title from filename if metadata extraction fails
        Supports: "Artist - Title.ext" format
        """
        try:
            name = os.path.splitext(filename)[0]
            if ' - ' in name:
                parts = name.split(' - ', 1)
                return {
                    'artist': parts[0].strip(),
                    'title': parts[1].strip(),
                }
        except Exception:
            pass
        return None
