import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Optional
import json
import hashlib
from pathlib import Path


class DictionaryCache:
    """Cache for dictionary lookups"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, word: str) -> Path:
        word_hash = hashlib.md5(word.encode()).hexdigest()
        return self.cache_dir / f"{word_hash}.json"
    
    def get(self, word: str) -> Optional[Dict]:
        cache_path = self._get_cache_path(word)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    def set(self, word: str, data: Dict):
        cache_path = self._get_cache_path(word)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass


class DictionaryAPI:
    """Async dictionary lookup from multiple sources"""
    
    def __init__(self, cache_dir: Path):
        self.cache = DictionaryCache(cache_dir)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
    
    async def lookup(self, word: str) -> Dict:
        """Lookup word from multiple dictionaries concurrently"""
        # Check cache first
        cached = self.cache.get(word)
        if cached:
            return cached
        
        await self._ensure_session()
        
        # Fetch from both sources concurrently
        results = await asyncio.gather(
            self._fetch_merriam_webster(word),
            self._fetch_youdao(word),
            return_exceptions=True
        )
        
        merriam_result = results[0] if not isinstance(results[0], Exception) else {}
        youdao_result = results[1] if not isinstance(results[1], Exception) else {}
        
        combined = {
            "word": word,
            "merriam_webster": merriam_result,
            "youdao": youdao_result
        }
        
        # Cache the result
        self.cache.set(word, combined)
        return combined
    
    async def _fetch_merriam_webster(self, word: str) -> Dict:
        """Fetch definition from Merriam-Webster"""
        try:
            url = f"https://www.merriam-webster.com/dictionary/{word}"
            async with self.session.get(url, timeout=5) as response:
                if response.status != 200:
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                result = {
                    "phonetic": "",
                    "definitions": [],
                    "examples": []
                }
                
                # Extract phonetic
                pron = soup.select_one('.prons-entries-list-inline .mw')
                if pron:
                    result["phonetic"] = pron.get_text(strip=True)
                
                # Extract definitions
                definitions = soup.select('.dtText')
                for defn in definitions[:3]:  # Limit to 3 definitions
                    text = defn.get_text(strip=True)
                    if text.startswith(':'):
                        text = text[1:].strip()
                    result["definitions"].append(text)
                
                # Extract examples
                examples = soup.select('.t.has-aq')
                for ex in examples[:2]:  # Limit to 2 examples
                    result["examples"].append(ex.get_text(strip=True))
                
                return result
        except Exception as e:
            print(f"Merriam-Webster lookup failed for '{word}': {e}")
            return {}
    
    async def _fetch_youdao(self, word: str) -> Dict:
        """Fetch Chinese translation from Youdao"""
        try:
            url = f"https://dict.youdao.com/w/eng/{word}"
            async with self.session.get(url, timeout=5) as response:
                if response.status != 200:
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                result = {
                    "phonetic": "",
                    "translations": []
                }
                
                # Extract phonetic
                phonetic_uk = soup.select_one('.phonetic')
                if phonetic_uk:
                    result["phonetic"] = phonetic_uk.get_text(strip=True)
                
                # Extract Chinese translations
                trans_list = soup.select('.trans-container ul li')
                for trans in trans_list[:5]:  # Limit to 5 translations
                    text = trans.get_text(strip=True)
                    if text:
                        result["translations"].append(text)
                
                return result
        except Exception as e:
            print(f"Youdao lookup failed for '{word}': {e}")
            return {}
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.session and not self.session.closed:
            try:
                asyncio.get_event_loop().run_until_complete(self.session.close())
            except:
                pass
