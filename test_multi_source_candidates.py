#!/usr/bin/env python3
"""Test script to verify all sources return candidates"""

from core.lyrics_downloader import LyricsDownloader

def test_candidates():
    downloader = LyricsDownloader()
    
    # Test metadata
    metadata = {
        'artist': 'Jay Chou',
        'title': 'Blue and White Porcelain'
    }
    
    print(f"Testing: {metadata['artist']} - {metadata['title']}\n")
    
    # Get all candidates
    candidates = downloader.get_all_lyrics_candidates(metadata)
    
    print(f"\n\nTotal candidates collected: {len(candidates)}\n")
    
    if candidates:
        print("Candidates by source:")
        for candidate in candidates:
            print(f"  [{candidate['source']:10}] {candidate['artist']:20} - {candidate['title']:30} (score: {candidate['score']:3})")
    else:
        print("No candidates found!")

if __name__ == '__main__':
    test_candidates()
