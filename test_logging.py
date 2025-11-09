#!/usr/bin/env python3
"""
Test script to verify enhanced logging for lyrics download
"""

from core.lyrics_downloader import LyricsDownloader
import tempfile
import os

def test_lyrics_logging():
    """Test the enhanced logging output"""
    
    # Test case: 周杰伦 - 青花瓷
    test_metadata = {
        'artist': '周杰伦',
        'title': '青花瓷'
    }
    
    print("="*80)
    print("Testing lyrics download with enhanced logging")
    print("="*80)
    print(f"\nTest metadata:")
    print(f"  Artist: {test_metadata['artist']}")
    print(f"  Title: {test_metadata['title']}")
    print("\n" + "="*80)
    
    # Create temp output file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lrc', delete=False) as tmp:
        output_path = tmp.name
    
    try:
        downloader = LyricsDownloader()
        success = downloader.download_lyrics(test_metadata, output_path)
        
        print("\n" + "="*80)
        if success:
            print(f"✓ SUCCESS: Lyrics downloaded to {output_path}")
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"\nLyrics preview (first 5 lines):")
                for line in lines[:5]:
                    print(f"  {line}")
        else:
            print(f"✗ FAILED: Could not download lyrics")
        print("="*80)
        
    finally:
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    test_lyrics_logging()
