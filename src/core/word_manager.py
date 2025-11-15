import json
import re
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime


class Word:
    """Represents a single word with its definitions"""
    
    def __init__(self, word: str, definitions: Optional[Dict] = None):
        self.word = word.strip().lower()
        self.definitions = definitions or {}
        self.learned = False
        self.review_count = 0
        self.last_reviewed = None
    
    def to_dict(self) -> Dict:
        return {
            "word": self.word,
            "definitions": self.definitions,
            "learned": self.learned,
            "review_count": self.review_count,
            "last_reviewed": self.last_reviewed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Word':
        word = cls(data["word"], data.get("definitions", {}))
        word.learned = data.get("learned", False)
        word.review_count = data.get("review_count", 0)
        word.last_reviewed = data.get("last_reviewed")
        return word


class WordList:
    """Manages a collection of words"""
    
    def __init__(self, name: str, words: List[Word] = None):
        self.name = name
        self.words = words or []
        self.current_index = 0
        self.created_at = datetime.now().isoformat()
    
    def add_word(self, word: Word):
        if not any(w.word == word.word for w in self.words):
            self.words.append(word)
    
    def get_current_word(self) -> Optional[Word]:
        if not self.words:
            return None
        return self.words[self.current_index]
    
    def next_word(self) -> Optional[Word]:
        if not self.words:
            return None
        self.current_index = (self.current_index + 1) % len(self.words)
        return self.get_current_word()
    
    def previous_word(self) -> Optional[Word]:
        if not self.words:
            return None
        self.current_index = (self.current_index - 1) % len(self.words)
        return self.get_current_word()
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "words": [w.to_dict() for w in self.words],
            "current_index": self.current_index,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WordList':
        wordlist = cls(
            name=data["name"],
            words=[Word.from_dict(w) for w in data.get("words", [])]
        )
        wordlist.current_index = data.get("current_index", 0)
        wordlist.created_at = data.get("created_at", datetime.now().isoformat())
        return wordlist


class WordManager:
    """Manages word lists and imports"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "words"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_wordlist: Optional[WordList] = None
        self._load_builtin_wordlists()
    
    def import_from_text(self, text: str, list_name: str) -> WordList:
        """Import words from text with various separators"""
        # Split by common separators: newline, comma, space
        raw_words = re.split(r'[\n,\s]+', text)
        words = [Word(w) for w in raw_words if w.strip()]
        
        wordlist = WordList(list_name, words)
        self.save_wordlist(wordlist)
        return wordlist
    
    def import_from_file(self, file_path: Path, list_name: str) -> WordList:
        """Import words from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.import_from_text(text, list_name)
        except IOError as e:
            raise Exception(f"Failed to read file: {e}")
    
    def save_wordlist(self, wordlist: WordList):
        """Save word list to JSON file"""
        filename = self._sanitize_filename(wordlist.name) + ".json"
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(wordlist.to_dict(), f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise Exception(f"Failed to save word list: {e}")
    
    def load_wordlist(self, name: str) -> Optional[WordList]:
        """Load word list from file"""
        filename = self._sanitize_filename(name) + ".json"
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return WordList.from_dict(data)
        except (json.JSONDecodeError, IOError):
            return None
    
    def list_wordlists(self) -> List[str]:
        """Get list of all saved word lists"""
        return [f.stem for f in self.data_dir.glob("*.json")]
    
    def delete_wordlist(self, name: str):
        """Delete a word list"""
        filename = self._sanitize_filename(name) + ".json"
        filepath = self.data_dir / filename
        if filepath.exists():
            filepath.unlink()
    
    def set_current_wordlist(self, wordlist: WordList):
        """Set the active word list"""
        self.current_wordlist = wordlist
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename"""
        return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
    
    def _load_builtin_wordlists(self):
        """Load built-in wordlists from data directory"""
        # Get the project root directory
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        builtin_data = project_root / "data"
        
        # Copy builtin wordlists if they don't exist in user data
        builtin_files = [
            ("builtin_cet4.txt", "CET-4 Words (Built-in)"),
            ("builtin_cet6.txt", "CET-6 Words (Built-in)")
        ]
        
        for filename, list_name in builtin_files:
            source = builtin_data / filename
            if source.exists():
                # Check if this wordlist already exists in user data
                if not self.load_wordlist(list_name):
                    try:
                        self.import_from_file(source, list_name)
                    except Exception as e:
                        print(f"Failed to load builtin wordlist {filename}: {e}")
