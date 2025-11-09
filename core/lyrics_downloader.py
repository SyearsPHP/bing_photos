"""
Lyrics downloader from multiple sources
"""

import os
import time
from typing import Optional, Dict, List
from core.lrc_sources import ALL_SOURCES

class LyricsDownloader:
    """
    Downloads LRC files from various sources.
    Primary sources: NetEase, QQ Music, KuGou
    """
    
    def __init__(self):
        self.sources = [source_class() for source_class in ALL_SOURCES]
    
    def download_lyrics(self, metadata: Dict, output_path: str) -> bool:
        """
        Download lyrics for a song based on metadata
        """
        if not metadata:
            return False
        
        artist = metadata.get('artist', '').strip()
        title = metadata.get('title', '').strip()
        
        if not artist or not title:
            return False
        
        # Try multiple sources
        for idx, source in enumerate(self.sources):
            try:
                lrc_content = source.get_lyrics(artist, title)
                if lrc_content and lrc_content.strip():
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(lrc_content)
                    return True
            except Exception as e:
                print(f"Error downloading from {source.__class__.__name__} for '{artist} - {title}': {e}")
            
            # Add delay between source attempts to avoid rate limiting
            if idx < len(self.sources) - 1:
                time.sleep(1.0)
        
        return False
    
    def get_all_lyrics_candidates(self, metadata: Dict) -> List[Dict]:
        """
        Get lyrics candidates from all sources
        Returns a list of dicts with: source, artist, title, preview, full_lyrics
        """
        if not metadata:
            return []
        
        artist = metadata.get('artist', '').strip()
        title = metadata.get('title', '').strip()
        
        if not artist or not title:
            return []
        
        all_candidates = []
        
        # Collect candidates from all sources
        for idx, source in enumerate(self.sources):
            try:
                candidates = source.get_lyrics_candidates(artist, title)
                all_candidates.extend(candidates)
            except Exception as e:
                print(f"Error getting candidates from {source.__class__.__name__} for '{artist} - {title}': {e}")
            
            # Add delay between source attempts
            if idx < len(self.sources) - 1:
                time.sleep(1.0)
        
        # Sort by score (descending)
        all_candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return all_candidates
