"""
LRC sources handlers - supports multiple music platforms
"""

import requests
import json
import re
import time
import base64
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
    
    def get_lyrics_candidates(self, artist: str, title: str) -> List[Dict]:
        """
        Get multiple lyrics candidates from this source.
        Returns a list of dicts with: source, artist, title, preview, full_lyrics
        """
        raise NotImplementedError


class NetEaseSource(LRCSource):
    """NetEase Music LRC source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            print(f"\n=== NetEase Music API ===")
            print(f"Original metadata: ARTIST='{artist}' | TITLE='{title}'")
            print(f"Normalized search: '{artist_norm} {title_norm}'")
            
            # Search for song using the working API endpoint
            search_url = "https://music.163.com/api/v1/search/get"
            params = {
                's': f"{artist_norm} {title_norm}",
                'type': 1,
                'limit': 20  # Get more results to find better match
            }
            
            print(f"Search URL: {search_url}")
            print(f"Search params: {params}")
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                print(f"✗ NetEase search failed (status: {response.status_code if response else 'None'})")
                return None
            
            data = response.json()
            if not data.get('result', {}).get('songs'):
                print(f"✗ No songs found in NetEase results")
                return None
            
            # Score all songs and sort by match quality
            songs = data['result']['songs']
            scored_songs = []
            
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
                
                # Exact title match (highest priority)
                if title_norm_lower == song_name:
                    score += 20
                elif title_norm_lower in song_name or song_name in title_norm_lower:
                    score += 10
                elif title_norm_lower in song_full_text:
                    score += 5
                
                # Exact artist match - CRITICAL for correct song
                if artist_norm_lower == song_artist_names:
                    score += 30  # Higher weight for exact artist match
                elif artist_norm_lower in song_artist_names:
                    score += 15
                elif artist_norm_lower in song_full_text:
                    score += 8
                else:
                    # If artist doesn't match at all, heavily penalize
                    score -= 10
                
                # Check if artist mentioned in song name (original singer credits)
                if '原唱' in song_name or '原版' in song_name:
                    # This is often a cover, reduce score
                    if artist_norm_lower not in song_artist_names:
                        score -= 5  # It's a cover version
                    else:
                        score += 3  # It's marked as original
                
                # Penalize covers, remixes, live versions, instrumentals
                penalty_keywords = ['翻唱', '伴奏', '纯音乐', 'cover', 'remix', 'live', 'instrumental', 'karaoke', '卡拉OK', '钢琴版', '吉他版']
                for keyword in penalty_keywords:
                    if keyword in song_name:
                        score -= 8
                
                scored_songs.append((score, song))
            
            # Sort by score descending (highest scores first)
            scored_songs.sort(key=lambda x: x[0], reverse=True)
            
            # Print all scored songs for debugging
            print(f"\nFound {len(scored_songs)} songs, top 10 scores:")
            for i, (score, song) in enumerate(scored_songs[:10]):
                song_name = song.get('name', '')
                song_artists = song.get('artists', [])
                artist_names = ', '.join([a.get('name', '') for a in song_artists])
                print(f"  {i+1}. [{score:3d}] {artist_names} - {song_name}")
            
            # Try songs in order of match quality
            print(f"\nAttempting to get lyrics from top matches:")
            for score, attempt_song in scored_songs[:8]:  # Try top 8 best matches
                # Skip songs with very low scores (likely not relevant)
                if score < 5:
                    continue
                    
                try:
                    song_name = attempt_song.get('name', '')
                    song_artists = attempt_song.get('artists', [])
                    artist_names = ', '.join([a.get('name', '') for a in song_artists])
                    song_id = attempt_song.get('id')
                    print(f"  Trying song #{song_id}: {artist_names} - {song_name} (score: {score})")
                    
                    lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1"
                    print(f"    Lyrics API: {lyric_url}")
                    lyric_response = self._safe_request('GET', lyric_url)
                    
                    if lyric_response and lyric_response.status_code == 200:
                        lyric_data = lyric_response.json()
                        lyric_content = lyric_data.get('lrc', {}).get('lyric', '')
                        if lyric_content and lyric_content.strip():
                            print(f"    ✓ SUCCESS: Found lyrics for: {artist_names} - {song_name}")
                            return lyric_content
                        else:
                            print(f"    ✗ No lyrics available (empty/null)")
                except Exception as e:
                    print(f"    ✗ Error getting lyrics: {e}")
                    continue
        
        except Exception as e:
            print(f"NetEase error: {e}")
        
        return None
    
    def get_lyrics_candidates(self, artist: str, title: str) -> List[Dict]:
        """Get multiple lyrics candidates from NetEase Music"""
        candidates = []
        try:
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            # Search for song using the working API endpoint
            search_url = "https://music.163.com/api/v1/search/get"
            params = {
                's': f"{artist_norm} {title_norm}",
                'type': 1,
                'limit': 20
            }
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                return candidates
            
            data = response.json()
            if not data.get('result', {}).get('songs'):
                return candidates
            
            # Score all songs and sort by match quality
            songs = data['result']['songs']
            scored_songs = []
            
            for song in songs:
                song_name = song.get('name', '').lower()
                song_artists = song.get('artists', [])
                song_artist_names = ' '.join([a.get('name', '').lower() for a in song_artists])
                
                song_full_text = f"{song_name} {song_artist_names}".lower()
                artist_norm_lower = artist_norm.lower()
                title_norm_lower = title_norm.lower()
                
                # Calculate match score
                score = 0
                
                if title_norm_lower == song_name:
                    score += 20
                elif title_norm_lower in song_name or song_name in title_norm_lower:
                    score += 10
                elif title_norm_lower in song_full_text:
                    score += 5
                
                if artist_norm_lower == song_artist_names:
                    score += 30
                elif artist_norm_lower in song_artist_names:
                    score += 15
                elif artist_norm_lower in song_full_text:
                    score += 8
                else:
                    score -= 10
                
                if '原唱' in song_name or '原版' in song_name:
                    if artist_norm_lower not in song_artist_names:
                        score -= 5
                    else:
                        score += 3
                
                penalty_keywords = ['翻唱', '伴奏', '纯音乐', 'cover', 'remix', 'live', 'instrumental', 'karaoke', '卡拉OK', '钢琴版', '吉他版']
                for keyword in penalty_keywords:
                    if keyword in song_name:
                        score -= 8
                
                scored_songs.append((score, song))
            
            scored_songs.sort(key=lambda x: x[0], reverse=True)
            
            # Try top 15 best matches with valid scores
            for score, attempt_song in scored_songs[:15]:
                if score < 5:
                    continue
                
                try:
                    song_name = attempt_song.get('name', '')
                    song_artists = attempt_song.get('artists', [])
                    artist_names = ', '.join([a.get('name', '') for a in song_artists])
                    song_id = attempt_song.get('id')
                    
                    lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1"
                    lyric_response = self._safe_request('GET', lyric_url)
                    
                    if lyric_response and lyric_response.status_code == 200:
                        lyric_data = lyric_response.json()
                        lyric_content = lyric_data.get('lrc', {}).get('lyric', '')
                        if lyric_content and lyric_content.strip():
                            # Extract preview (first 3 lines with timestamps)
                            lines = lyric_content.split('\n')
                            preview_lines = [line for line in lines[:5] if line.strip().startswith('[')]
                            preview = '\n'.join(preview_lines[:3])
                            
                            candidates.append({
                                'source': 'NetEase',
                                'artist': artist_names,
                                'title': song_name,
                                'preview': preview,
                                'full_lyrics': lyric_content,
                                'score': score
                            })
                except Exception:
                    continue
        
        except Exception:
            pass
        
        return candidates


class KuGouSource(LRCSource):
    """KuGou Music LRC source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            print(f"\n=== KuGou Music API ===")
            print(f"Original metadata: ARTIST='{artist}' | TITLE='{title}'")
            print(f"Normalized search: '{artist_norm} {title_norm}'")
            
            # Search for songs first
            search_url = "https://songsearch.kugou.com/song_search_v2"
            params = {
                'keyword': f"{artist_norm} {title_norm}",
                'page': 1,
                'pagesize': 20
            }
            
            print(f"Search URL: {search_url}")
            print(f"Search params: {params}")
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                print(f"✗ KuGou search failed (status: {response.status_code if response else 'None'})")
                return None
            
            data = response.json()
            if not data.get('data') or not data['data'].get('lists'):
                print(f"✗ No songs found in KuGou results")
                return None
            
            songs = data['data']['lists']
            if not songs:
                return None
            
            # Score and sort songs
            scored_songs = []
            artist_norm_lower = artist_norm.lower()
            title_norm_lower = title_norm.lower()
            
            for song in songs:
                song_name = song.get('SongName', '').lower()
                song_artist = song.get('SingerName', '').lower()
                
                score = 0
                
                # Exact matches
                if title_norm_lower == song_name:
                    score += 20
                elif title_norm_lower in song_name or song_name in title_norm_lower:
                    score += 10
                
                if artist_norm_lower == song_artist:
                    score += 20
                elif artist_norm_lower in song_artist or song_artist in artist_norm_lower:
                    score += 10
                
                # Penalize unwanted versions
                penalty_keywords = ['伴奏', '纯音乐', 'cover', 'remix', 'live', 'instrumental']
                for keyword in penalty_keywords:
                    if keyword in song_name:
                        score -= 5
                
                scored_songs.append((score, song))
            
            scored_songs.sort(key=lambda x: x[0], reverse=True)
            
            # Print all scored songs for debugging
            print(f"\nFound {len(scored_songs)} songs, top 5 scores:")
            for i, (score, song) in enumerate(scored_songs[:5]):
                song_name = song.get('SongName', '')
                song_artist = song.get('SingerName', '')
                print(f"  {i+1}. [{score:3d}] {song_artist} - {song_name}")
            
            # Try top matches
            print(f"\nAttempting to get lyrics from top matches:")
            for score, song in scored_songs[:5]:
                if score < 5:
                    continue
                
                try:
                    file_hash = song.get('FileHash') or song.get('Hash')
                    if not file_hash:
                        continue
                    
                    song_name = song.get('SongName', '')
                    song_artist = song.get('SingerName', '')
                    print(f"  Trying: {song_artist} - {song_name} (score: {score})")
                    
                    # Get lyrics using hash
                    lyric_url = "https://www.kugou.com/yy/index.php"
                    lyric_params = {
                        'r': 'play/getdata',
                        'hash': file_hash
                    }
                    
                    print(f"    Lyrics API: {lyric_url}?r={lyric_params['r']}&hash={file_hash[:8]}...")
                    lyric_response = self._safe_request('GET', lyric_url, params=lyric_params)
                    if lyric_response and lyric_response.status_code == 200:
                        lyric_data = lyric_response.json()
                        if lyric_data.get('data') and lyric_data['data'].get('lyrics'):
                            content = lyric_data['data']['lyrics']
                            if content.strip().startswith('['):
                                print(f"    ✓ SUCCESS: Found KuGou lyrics for: {song_artist} - {song_name}")
                                return content
                            else:
                                print(f"    ✗ Not in LRC format")
                        else:
                            print(f"    ✗ No lyrics available")
                except Exception as e:
                    print(f"    ✗ Error: {e}")
                    continue
        
        except Exception as e:
            print(f"KuGou error: {e}")
        
        return None
    
    def get_lyrics_candidates(self, artist: str, title: str) -> List[Dict]:
        """Get multiple lyrics candidates from KuGou Music"""
        candidates = []
        try:
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            # Search for songs
            search_url = "https://songsearch.kugou.com/song_search_v2"
            params = {
                'keyword': f"{artist_norm} {title_norm}",
                'page': 1,
                'pagesize': 20
            }
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                return candidates
            
            data = response.json()
            if not data.get('data') or not data['data'].get('lists'):
                return candidates
            
            songs = data['data']['lists']
            if not songs:
                return candidates
            
            # Score and sort songs
            scored_songs = []
            artist_norm_lower = artist_norm.lower()
            title_norm_lower = title_norm.lower()
            
            for song in songs:
                song_name = song.get('SongName', '').lower()
                song_artist = song.get('SingerName', '').lower()
                
                score = 0
                
                if title_norm_lower == song_name:
                    score += 20
                elif title_norm_lower in song_name or song_name in title_norm_lower:
                    score += 10
                
                if artist_norm_lower == song_artist:
                    score += 20
                elif artist_norm_lower in song_artist or song_artist in artist_norm_lower:
                    score += 10
                
                penalty_keywords = ['伴奏', '纯音乐', 'cover', 'remix', 'live', 'instrumental']
                for keyword in penalty_keywords:
                    if keyword in song_name:
                        score -= 5
                
                scored_songs.append((score, song))
            
            scored_songs.sort(key=lambda x: x[0], reverse=True)
            
            # Try top 10 best matches
            for score, song in scored_songs[:10]:
                if score < 5:
                    continue
                
                try:
                    file_hash = song.get('FileHash') or song.get('Hash')
                    if not file_hash:
                        continue
                    
                    song_name = song.get('SongName', '')
                    song_artist = song.get('SingerName', '')
                    
                    # Get lyrics
                    lyric_url = "https://www.kugou.com/yy/index.php"
                    lyric_params = {
                        'r': 'play/getdata',
                        'hash': file_hash
                    }
                    
                    lyric_response = self._safe_request('GET', lyric_url, params=lyric_params)
                    if lyric_response and lyric_response.status_code == 200:
                        lyric_data = lyric_response.json()
                        if lyric_data.get('data') and lyric_data['data'].get('lyrics'):
                            content = lyric_data['data']['lyrics']
                            if content.strip().startswith('['):
                                # Extract preview
                                lines = content.split('\n')
                                preview_lines = [line for line in lines[:5] if line.strip().startswith('[')]
                                preview = '\n'.join(preview_lines[:3])
                                
                                candidates.append({
                                    'source': 'KuGou',
                                    'artist': song_artist,
                                    'title': song_name,
                                    'preview': preview,
                                    'full_lyrics': content,
                                    'score': score
                                })
                except Exception:
                    continue
        
        except Exception:
            pass
        
        return candidates


class TencentQQSource(LRCSource):
    """Tencent QQ Music LRC source"""
    
    def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        try:
            # Normalize search terms
            artist_norm = self._normalize_search_term(artist)
            title_norm = self._normalize_search_term(title)
            
            print(f"\n=== QQ Music API ===")
            print(f"Original metadata: ARTIST='{artist}' | TITLE='{title}'")
            print(f"Normalized search: '{artist_norm} {title_norm}'")
            
            # Using the JSON format endpoint
            search_url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
            
            params = {
                'aggr': 1,
                'cr': 1,
                'flag_qc': 0,
                'p': 1,
                'n': 20,
                'w': f"{artist_norm} {title_norm}",
                'g_tk': 5381,
                'format': 'json'
            }
            
            print(f"Search URL: {search_url}")
            print(f"Search params: {params}")
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                print(f"✗ QQ Music search failed (status: {response.status_code if response else 'None'})")
                return None
            
            data = response.json()
            
            if not data.get('data', {}).get('song', {}).get('list'):
                print(f"✗ No songs found in QQ Music results")
                return None
            
            songs = data['data']['song']['list']
            if not songs:
                return None
            
            # Score and sort songs
            scored_songs = []
            artist_norm_lower = artist_norm.lower()
            title_norm_lower = title_norm.lower()
            
            for song in songs:
                song_name = song.get('songname', '').lower()
                song_artists = song.get('singer', [])
                
                # Build artist string
                if isinstance(song_artists, list):
                    song_artist = ' '.join([s.get('name', '').lower() for s in song_artists])
                else:
                    song_artist = str(song_artists).lower()
                
                score = 0
                
                # Exact matches
                if title_norm_lower == song_name:
                    score += 20
                elif title_norm_lower in song_name or song_name in title_norm_lower:
                    score += 10
                
                if artist_norm_lower == song_artist:
                    score += 20
                elif artist_norm_lower in song_artist or song_artist in artist_norm_lower:
                    score += 10
                
                # Penalize unwanted versions
                penalty_keywords = ['伴奏', '纯音乐', 'cover', 'remix', 'live', 'instrumental']
                for keyword in penalty_keywords:
                    if keyword in song_name:
                        score -= 5
                
                scored_songs.append((score, song))
            
            scored_songs.sort(key=lambda x: x[0], reverse=True)
            
            # Print all scored songs for debugging
            print(f"\nFound {len(scored_songs)} songs, top 5 scores:")
            for i, (score, song) in enumerate(scored_songs[:5]):
                song_name = song.get('songname', '')
                song_artists = song.get('singer', [])
                if isinstance(song_artists, list):
                    artist_str = ', '.join([s.get('name', '') for s in song_artists])
                else:
                    artist_str = str(song_artists)
                print(f"  {i+1}. [{score:3d}] {artist_str} - {song_name}")
            
            # Try top matches
            print(f"\nAttempting to get lyrics from top matches:")
            for score, song in scored_songs[:5]:
                if score < 5:
                    continue
                
                song_mid = song.get('songmid')
                if not song_mid:
                    continue
                
                try:
                    song_name = song.get('songname', '')
                    song_artists = song.get('singer', [])
                    if isinstance(song_artists, list):
                        artist_str = ', '.join([s.get('name', '') for s in song_artists])
                    else:
                        artist_str = str(song_artists)
                    
                    print(f"  Trying: {artist_str} - {song_name} (score: {score})")
                    
                    # Get lyrics
                    lyric_url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
                    lyric_params = {
                        'songmid': song_mid,
                        'g_tk': 5381,
                        'format': 'json'
                    }
                    
                    print(f"    Lyrics API: {lyric_url}?songmid={song_mid}")
                    lyric_response = self._safe_request('GET', lyric_url, params=lyric_params)
                    if lyric_response and lyric_response.status_code == 200:
                        lyric_data = lyric_response.json()
                        if lyric_data.get('lyric'):
                            try:
                                decoded = base64.b64decode(lyric_data['lyric']).decode('utf-8')
                                if decoded.strip():
                                    print(f"    ✓ SUCCESS: Found QQ Music lyrics for: {artist_str} - {song_name}")
                                    return decoded
                            except:
                                if lyric_data.get('lyric').strip():
                                    print(f"    ✓ SUCCESS: Found QQ Music lyrics for: {artist_str} - {song_name}")
                                    return lyric_data.get('lyric')
                        else:
                            print(f"    ✗ No lyrics available")
                except Exception as e:
                    print(f"    ✗ Error: {e}")
                    continue
        
        except Exception as e:
            print(f"Tencent QQ error: {e}")
        
        return None
    
    def get_lyrics_candidates(self, artist: str, title: str) -> List[Dict]:
        """Get multiple lyrics candidates from QQ Music"""
        candidates = []
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
                'n': 20,
                'w': f"{artist_norm} {title_norm}",
                'g_tk': 5381,
                'format': 'json'
            }
            
            response = self._safe_request('GET', search_url, params=params)
            if not response or response.status_code != 200:
                return candidates
            
            data = response.json()
            
            if not data.get('data', {}).get('song', {}).get('list'):
                return candidates
            
            songs = data['data']['song']['list']
            if not songs:
                return candidates
            
            # Score and sort songs
            scored_songs = []
            artist_norm_lower = artist_norm.lower()
            title_norm_lower = title_norm.lower()
            
            for song in songs:
                song_name = song.get('songname', '').lower()
                song_artists = song.get('singer', [])
                
                if isinstance(song_artists, list):
                    song_artist = ' '.join([s.get('name', '').lower() for s in song_artists])
                else:
                    song_artist = str(song_artists).lower()
                
                score = 0
                
                if title_norm_lower == song_name:
                    score += 20
                elif title_norm_lower in song_name or song_name in title_norm_lower:
                    score += 10
                
                if artist_norm_lower == song_artist:
                    score += 20
                elif artist_norm_lower in song_artist or song_artist in artist_norm_lower:
                    score += 10
                
                penalty_keywords = ['伴奏', '纯音乐', 'cover', 'remix', 'live', 'instrumental']
                for keyword in penalty_keywords:
                    if keyword in song_name:
                        score -= 5
                
                scored_songs.append((score, song))
            
            scored_songs.sort(key=lambda x: x[0], reverse=True)
            
            # Try top 10 best matches
            for score, song in scored_songs[:10]:
                if score < 5:
                    continue
                
                song_mid = song.get('songmid')
                if not song_mid:
                    continue
                
                try:
                    song_name = song.get('songname', '')
                    song_artists = song.get('singer', [])
                    if isinstance(song_artists, list):
                        artist_str = ', '.join([s.get('name', '') for s in song_artists])
                    else:
                        artist_str = str(song_artists)
                    
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
                            try:
                                decoded = base64.b64decode(lyric_data['lyric']).decode('utf-8')
                                if decoded.strip():
                                    lines = decoded.split('\n')
                                    preview_lines = [line for line in lines[:5] if line.strip().startswith('[')]
                                    preview = '\n'.join(preview_lines[:3])
                                    
                                    candidates.append({
                                        'source': 'QQ Music',
                                        'artist': artist_str,
                                        'title': song_name,
                                        'preview': preview,
                                        'full_lyrics': decoded,
                                        'score': score
                                    })
                            except:
                                if lyric_data.get('lyric').strip():
                                    lines = lyric_data.get('lyric').split('\n')
                                    preview_lines = [line for line in lines[:5] if line.strip().startswith('[')]
                                    preview = '\n'.join(preview_lines[:3])
                                    
                                    candidates.append({
                                        'source': 'QQ Music',
                                        'artist': artist_str,
                                        'title': song_name,
                                        'preview': preview,
                                        'full_lyrics': lyric_data.get('lyric'),
                                        'score': score
                                    })
                except Exception:
                    continue
        
        except Exception:
            pass
        
        return candidates


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
