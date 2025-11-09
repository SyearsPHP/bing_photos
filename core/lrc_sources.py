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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate'
        })
        # Enable SSL verification but will fallback to disabled if needed
        self.session.verify = True
        self.timeout = 15
    
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
        """Make a request with SSL fallback and retry logic"""
        max_retries = 2
        retry_delay = 1.0
        
        for attempt in range(max_retries):
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
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                # Retry on timeout/connection errors
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
            except Exception:
                return None
        
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
                'limit': 20  # Get more results to find better match
            }
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                return None
            
            data = response.json()
            if not data.get('result', {}).get('songs'):
                return None
            
            # Try to find the best matching song
            songs = data['result']['songs']
            best_song = None
            best_score = -1
            
            for song in songs:
                # Check if artist and title match
                song_name = song.get('name', '').lower()
                song_artists = song.get('artists', [])
                song_artist_names = ' '.join([a.get('name', '').lower() for a in song_artists])
                
                # Combine song name and artist for better matching
                song_full_text = f"{song_name} {song_artist_names}".lower()
                artist_norm_lower = artist_norm.lower()
                title_norm_lower = title_norm.lower()
                
                # Calculate match score
                score = 0
                
                # Title match
                if title_norm_lower in song_name or song_name in title_norm_lower:
                    score += 10
                elif title_norm_lower in song_full_text:
                    score += 5
                
                # Artist match
                if artist_norm_lower in song_artist_names:
                    score += 10
                elif artist_norm_lower in song_full_text:
                    score += 5
                
                # Prefer exact artist matches and original versions
                if song_artist_names and artist_norm_lower in song_artist_names:
                    score += 5
                if '原唱' in song_name or '原版' in song_name:
                    score += 3
                
                if score > best_score:
                    best_score = score
                    best_song = song
            
            # If no match found, use first result as fallback
            if best_song is None:
                best_song = songs[0]
            
            song_id = best_song['id']
            
            # Get lyrics - try multiple times with different songs if needed
            for attempt_song in songs[:5]:  # Try top 5 matches
                try:
                    lyric_url = f"https://music.163.com/api/song/lyric?id={attempt_song['id']}&lv=1"
                    lyric_response = self._safe_request('GET', lyric_url)
                    
                    if lyric_response and lyric_response.status_code == 200:
                        lyric_data = lyric_response.json()
                        lyric_content = lyric_data.get('lrc', {}).get('lyric', '')
                        if lyric_content and lyric_content.strip():
                            return lyric_content
                except:
                    continue
        
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
