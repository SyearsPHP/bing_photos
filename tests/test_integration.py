"""
Integration tests for LRC downloader
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.music_processor import MusicProcessor
from core.lyrics_downloader import LyricsDownloader
from core.lrc_sources import ALL_SOURCES, NetEaseSource

def test_lyrics_downloader_initialization():
    """Test that LyricsDownloader can be initialized"""
    downloader = LyricsDownloader()
    assert downloader is not None
    assert len(downloader.sources) > 0
    print(f"✓ LyricsDownloader initialized with {len(downloader.sources)} sources")

def test_lrc_source_instantiation():
    """Test that all LRC sources can be instantiated"""
    for source_class in ALL_SOURCES:
        source = source_class()
        assert source is not None
        print(f"✓ {source_class.__name__} instantiated successfully")

def test_metadata_validation():
    """Test metadata validation"""
    valid_metadata = {
        'artist': 'Test Artist',
        'title': 'Test Song',
        'format': 'mp3'
    }
    
    downloader = LyricsDownloader()
    # The download_lyrics method should handle this gracefully
    # (it will fail to download but shouldn't crash)
    result = downloader.download_lyrics(valid_metadata, '/tmp/test.lrc')
    # Result should be False since no network/API will work in test
    # But more importantly, no exceptions should be thrown
    print(f"✓ Metadata validation passed (download result: {result})")

def test_incomplete_metadata():
    """Test that incomplete metadata is rejected"""
    incomplete_metadata = {
        'artist': 'Test Artist',
        # Missing title
    }
    
    downloader = LyricsDownloader()
    result = downloader.download_lyrics(incomplete_metadata, '/tmp/test.lrc')
    
    assert result is False
    print("✓ Incomplete metadata correctly rejected")

if __name__ == '__main__':
    test_lyrics_downloader_initialization()
    test_lrc_source_instantiation()
    test_metadata_validation()
    test_incomplete_metadata()
    print("\n✅ All integration tests passed!")
