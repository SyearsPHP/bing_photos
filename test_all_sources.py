#!/usr/bin/env python3
"""
Test all sources individually for 周杰伦 - 青花瓷
"""

from core.lrc_sources import NetEaseSource, KuGouSource, TencentQQSource

def test_source(source_name, source_class):
    print("\n" + "="*80)
    print(f"Testing {source_name}")
    print("="*80)
    
    source = source_class()
    result = source.get_lyrics('周杰伦', '青花瓷')
    
    if result:
        lines = result.split('\n')
        print(f"\n✓ Found lyrics! Preview (first 10 lines):")
        for line in lines[:10]:
            print(f"  {line}")
    else:
        print(f"\n✗ No lyrics found")
    
    return result is not None

if __name__ == "__main__":
    results = {}
    
    print("Testing all sources for: 周杰伦 - 青花瓷")
    
    results['NetEase'] = test_source('NetEase Music', NetEaseSource)
    results['KuGou'] = test_source('KuGou Music', KuGouSource)
    results['QQ Music'] = test_source('Tencent QQ Music', TencentQQSource)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for source, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{source:20s}: {status}")
    print("="*80)
