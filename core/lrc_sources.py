"""
LRC sources handlers - supports multiple music platforms
"""

import requests
import json
import re
import time
from typing import Optional, Dict, List
from urllib.parse import quote
import unicodedata

class LRCSource:
    """Base class for LRC sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })
        # Enable SSL verification but will fallback to disabled if needed
        self.session.verify = True
        self.timeout = 10
    
    @staticmethod
    def _normalize_search_term(text: str) -> str:
        """Normalize search term for API queries"""
        if not text:
            return ""
        
        try:
            # Normalize unicode characters (e.g., convert composed characters to decomposed)
            normalized = unicodedata.normalize('NFKD', text)
            # Remove null characters
            normalized = normalized.replace('\x00', '').strip()
            # Remove multiple spaces
            normalized = ' '.join(normalized.split())
            return normalized
        except Exception:
            return text
    
    def _safe_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a request with SSL fallback"""
        try:
            return self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.exceptions.SSLError:
            # Fallback to disabled SSL verification if SSL fails
            old_verify = self.session.verify
            self.session.verify = False
            try:
                return self.session.request(method, url, timeout=self.timeout, **kwargs)
            finally:
                self.session.verify = old_verify
        except Exception:
            return None
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Download lyrics for artist and title"""
        raise NotImplementedError


class NetEaseSource(LRCSource):
    """NetEase Music LRC source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            # Search for song using the working API endpoint
            search_url = "https://music.163.com/api/v1/search/get"
            params = {
                's': f"{artist_norm} {title_norm}",
                'type': 1,
                'limit': 10
            }
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                return None
            
            data = response.json()
            if not data.get('result', {}).get('songs'):
                return None
            
            # Get first matching song
            song = data['result']['songs'][0]
            song_id = song['id']
            
            # Get lyrics
            lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1"
            lyric_response = self._safe_request('GET', lyric_url)
            
            if lyric_response and lyric_response.status_code == 200:
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
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            # Try alternative KuGou endpoint
            search_url = "https://www.kugou.com/yy/index.php"
            
            params = {
                'r': 'play/getdata',
                'hash': '',
                'album_id': '',
                'mid': '',
                'keyword': f"{artist_norm} {title_norm}"
            }
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                return None
            
            data = response.json()
            if not data.get('data') or not data['data'].get('play_url'):
                return None
            
            # Try lyrics download endpoint
            lyric_url = "https://www.kugou.com/yy/index.php"
            lyric_params = {
                'r': 'lyric/get',
                'hash': data['data'].get('hash', ''),
                'album_id': data['data'].get('album_id', '')
            }
            
            lyric_response = self._safe_request('GET', lyric_url, params=lyric_params)
            if lyric_response and lyric_response.status_code == 200:
                lyric_data = lyric_response.json()
                if lyric_data.get('data') and lyric_data['data'].get('content'):
                    content = lyric_data['data']['content']
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
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            # Using the JSON format endpoint
            search_url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
            
            params = {
                'aggr': 1,
                'cr': 1,
                'flag_qc': 0,
                'p': 1,
                'n': 10,
                'w': f"{artist_norm} {title_norm}",
                'g_tk': 5381,
                'format': 'json'  # Request JSON format directly
            }
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                return None
            
            # Parse JSON response directly
            data = response.json()
            
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
            
            lyric_response = self._safe_request('GET', lyric_url, params=lyric_params)
            if lyric_response and lyric_response.status_code == 200:
                lyric_data = lyric_response.json()
                if lyric_data.get('lyric'):
                    # Decode base64 if needed
                    import base64
                    try:
                        decoded = base64.b64decode(lyric_data['lyric']).decode('utf-8')
                        return decoded
                    except:
                        return lyric_data.get('lyric')
        
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
