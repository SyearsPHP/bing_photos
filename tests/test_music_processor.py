"""
Tests for music_processor module
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.music_processor import MusicProcessor, SUPPORTED_FORMATS

def test_supported_formats():
    """Test that supported formats are correctly defined"""
    assert '.mp3' in SUPPORTED_FORMATS
    assert '.flac' in SUPPORTED_FORMATS
    assert '.wav' in SUPPORTED_FORMATS
    print("✓ Supported formats test passed")

def test_get_music_files():
    """Test getting music files from a directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        open(os.path.join(tmpdir, 'song1.mp3'), 'w').close()
        open(os.path.join(tmpdir, 'song2.flac'), 'w').close()
        open(os.path.join(tmpdir, 'file.txt'), 'w').close()
        
        # Get music files
        files = MusicProcessor.get_music_files(tmpdir, recursive=False)
        
        assert len(files) == 2
        assert any('song1.mp3' in f for f in files)
        assert any('song2.flac' in f for f in files)
        print("✓ get_music_files test passed")

def test_get_lrc_path():
    """Test LRC path generation"""
    music_file = "/path/to/song.mp3"
    lrc_path = MusicProcessor.get_lrc_path(music_file)
    
    assert lrc_path == "/path/to/song.lrc"
    print("✓ get_lrc_path test passed")

def test_extract_metadata_from_filename():
    """Test metadata extraction from filename"""
    filename = "Artist Name - Song Title.mp3"
    metadata = MusicProcessor.extract_metadata_from_filename(filename)
    
    assert metadata is not None
    assert metadata['artist'] == 'Artist Name'
    assert metadata['title'] == 'Song Title'
    print("✓ extract_metadata_from_filename test passed")

if __name__ == '__main__':
    test_supported_formats()
    test_get_music_files()
    test_get_lrc_path()
    test_extract_metadata_from_filename()
    print("\n✅ All tests passed!")
