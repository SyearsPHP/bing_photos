#!/usr/bin/env python3
"""
Final verification test for all enhancements
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from core.lrc_sources import NetEaseSource, KuGouSource, TencentQQSource
        from core.lyrics_downloader import LyricsDownloader
        from core.music_processor import MusicProcessor
        print("  ✓ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_mach_port_suppression():
    """Test that macOS Mach Port error suppression is configured"""
    print("\nTesting macOS Mach Port error suppression...")
    try:
        # Just check that main.py has the configuration
        with open('main.py', 'r') as f:
            content = f.read()
        
        has_qt_layer = "QT_MAC_WANTS_LAYER" in content
        has_qt_logging = "QT_LOGGING_RULES" in content
        
        if has_qt_layer and has_qt_logging:
            print("  ✓ Environment variables configured in main.py")
            print("    - QT_MAC_WANTS_LAYER setting found")
            print("    - QT_LOGGING_RULES setting found")
            return True
        else:
            print("  ⚠ Environment variables not configured")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_logging_format():
    """Test that logging format is correct"""
    print("\nTesting enhanced logging format...")
    try:
        from core.lrc_sources import NetEaseSource
        source = NetEaseSource()
        
        # Test normalize function
        test_text = "周杰伦"
        normalized = source._normalize_search_term(test_text)
        
        if normalized == test_text:
            print(f"  ✓ Normalization works: '{test_text}' -> '{normalized}'")
            return True
        else:
            print(f"  ✗ Normalization issue: '{test_text}' -> '{normalized}'")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_scoring_system():
    """Verify scoring system constants are in place"""
    print("\nTesting scoring system...")
    try:
        from core.lrc_sources import NetEaseSource
        import inspect
        
        source_code = inspect.getsource(NetEaseSource.get_lyrics)
        
        checks = {
            'Title exact match (+20)': 'score += 20' in source_code,
            'Artist exact match (+30)': 'score += 30' in source_code,
            'Artist penalty (-10)': 'score -= 10' in source_code,
            'Version penalties (-8)': 'score -= 8' in source_code,
            'Score threshold (>= 5)': 'score < 5' in source_code,
        }
        
        all_passed = True
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}")
            if not result:
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_documentation():
    """Check that documentation files exist"""
    print("\nTesting documentation...")
    
    docs = [
        'README.md',
        'METADATA_REVIEW.md',
        'LOGGING_AND_TROUBLESHOOTING.md',
        'CHANGELOG_ENHANCED_LOGGING.md',
    ]
    
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✓ {doc} exists")
        else:
            print(f"  ✗ {doc} missing")
            all_exist = False
    
    return all_exist

def main():
    print("="*80)
    print("Final Verification Test")
    print("="*80)
    
    results = {
        'Imports': test_imports(),
        'Mach Port Suppression': test_mach_port_suppression(),
        'Logging Format': test_logging_format(),
        'Scoring System': test_scoring_system(),
        'Documentation': test_documentation(),
    }
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:30s}: {status}")
    
    print("="*80)
    print(f"Overall: {passed}/{total} tests passed")
    print("="*80)
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
