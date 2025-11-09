"""
LRC sources handlers - supports multiple music platforms
"""

import requests
import json
import re
import time
from typing import Optional, Dict, List
from urllib.parse import quote

class LRCSource:
    """Base class for LRC sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.session.verify = False
        self.timeout = 10
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Download lyrics for artist and title"""
        raise NotImplementedError


class NetEaseSource(LRCSource):
    """NetEase Music LRC source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Search for song
            search_url = "https://music.163.com/api/search/get/web"
            params = {
                's': f"{artist} {title}",
                'type': 1,
                'limit': 10
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data.get('result', {}).get('songs'):
                return None
            
            # Get first matching song
            song = data['result']['songs'][0]
            song_id = song['id']
            
            # Get lyrics
            lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1"
            lyric_response = self.session.get(lyric_url, timeout=self.timeout)
            
            if lyric_response.status_code == 200:
                lyric_data = lyric_response.json()
                if lyric_data.get('lrc', {}).get('lyric'):
                    return lyric_data['lrc']['lyric']
        
        except Exception as e:
            print(f"NetEase error: {e}")
        
        return None


class KuGouSource(LRCSource):
    """KuGou Music LRC source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            search_url = "https://mobilecdn.kugou.com/new/app/i/getLyricNew"
            
            params = {
                'app_id': '1014',
                'clientver': '20000',
                'mid': '0',
                'platid': '4',
                'dfid': '',
                'keyword': f"{artist} {title}",
                'ver': 1,
                'hash': ''
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout, verify=False)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if data.get('status') != 200 or not data.get('data'):
                return None
            
            candidates = data['data']
            if not candidates:
                return None
            
            # Get first match
            candidate = candidates[0]
            lrc_id = candidate.get('id')
            lrc_acc = candidate.get('accesskey')
            
            if not lrc_id or not lrc_acc:
                return None
            
            # Download lyrics
            lyric_url = f"https://lyrics.kugou.com/download"
            lyric_params = {
                'id': lrc_id,
                'accesskey': lrc_acc,
                'fmt': 'lrc',
                'charset': 'utf8'
            }
            
            lyric_response = self.session.get(lyric_url, params=lyric_params, timeout=self.timeout, verify=False)
            if lyric_response.status_code == 200:
                content = lyric_response.text
                # Check if it's valid LRC format
                if content.strip().startswith('['):
                    return content
        
        except Exception as e:
            print(f"KuGou error: {e}")
        
        return None


class TencentQQSource(LRCSource):
    """Tencent QQ Music LRC source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Using a simpler endpoint
            search_url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
            
            params = {
                'aggr': 1,
                'cr': 1,
                'flag_qc': 0,
                'p': 1,
                'n': 10,
                'w': f"{artist} {title}",
                'g_tk': 5381
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            if response.status_code != 200:
                return None
            
            # Parse response
            text = response.text
            # QQ music returns a callback format, use greedy regex to get full JSON
            match = re.search(r'callback\((.*)\)\s*;?\s*$', text, re.DOTALL)
            if not match:
                return None
            
            data = json.loads(match.group(1))
            
            # Look for songs in the response
            if not data.get('data', {}).get('song', {}).get('list'):
                return None
            
            songs = data['data']['song']['list']
            if not songs:
                return None
            
            # Find first song with songmid
            song_mid = None
            for song in songs:
                song_mid = song.get('songmid')
                if song_mid:
                    break
            
            if not song_mid:
                return None
            
            # Get lyrics
            lyric_url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
            lyric_params = {
                'songmid': song_mid,
                'g_tk': 5381,
                'format': 'json'
            }
            
            lyric_response = self.session.get(lyric_url, params=lyric_params, timeout=self.timeout)
            if lyric_response.status_code == 200:
                text = lyric_response.text
                # Handle callback format - use greedy regex for full JSON
                if 'MusicJsonCallback(' in text:
                    try:
                        match = re.search(r'MusicJsonCallback\((.*)\)\s*;?\s*$', text, re.DOTALL)
                        if match:
                            json_str = match.group(1)
                            lyric_data = json.loads(json_str)
                            if lyric_data.get('lyric'):
                                # Decode base64 if needed
                                import base64
                                try:
                                    decoded = base64.b64decode(lyric_data['lyric']).decode('utf-8')
                                    return decoded
                                except:
                                    return lyric_data.get('lyric')
                    except (json.JSONDecodeError, ValueError):
                        pass
        
        except Exception as e:
            print(f"Tencent QQ error: {e}")
        
        return None


class GeniusSource(LRCSource):
    """Genius.com LRC source - English songs"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Genius requires authentication, so we use a limited approach
            search_url = f"https://genius.com/api/search/multi?per_page=5&q={quote(title)}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            if response.status_code != 200:
                return None
            
            data = response.json()
            hits = data.get('response', {}).get('sections', [])
            
            if not hits:
                return None
            
            # Note: Genius doesn't directly provide LRC format
            # This would need additional processing
            return None
        
        except Exception as e:
            print(f"Genius error: {e}")
        
        return None


class LyricistSource(LRCSource):
    """Lyricist.com as fallback source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Simple lyricist search
            search_url = "https://www.lyricist.com/search"
            params = {
                'q': f"{artist} {title}",
                'o': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                # Limited support - needs additional implementation
                pass
        
        except Exception as e:
            print(f"Lyricist error: {e}")
        
        return None


# List of all available sources in order of preference
ALL_SOURCES = [
    NetEaseSource,
    KuGouSource,
    TencentQQSource,
    # GeniusSource,  # Uncomment for English songs
]
