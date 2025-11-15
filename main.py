#!/usr/bin/env python3
"""
Word Recite - Desktop Vocabulary Learning Tool
A minimalist desktop app for effortless word learning through smart floating windows.
"""

import sys
import os
import asyncio
from pathlib import Path

# Fix Qt plugin path issue - must be set before importing PyQt6
def setup_qt_plugin_path():
    """Set up Qt plugin path for proper initialization"""
    import site
    
    # Try to find PyQt6 installation
    for path in site.getsitepackages() + [site.getusersitepackages()]:
        if path:
            potential_path = os.path.join(path, 'PyQt6', 'Qt6', 'plugins')
            if os.path.exists(potential_path):
                os.environ['QT_PLUGIN_PATH'] = potential_path
                platforms_path = os.path.join(potential_path, 'platforms')
                if os.path.exists(platforms_path):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_path
                return True
    
    # Fallback to conda environment path
    conda_base = os.path.dirname(os.path.dirname(sys.executable))
    plugin_path = os.path.join(conda_base, 'plugins')
    if os.path.exists(plugin_path):
        os.environ['QT_PLUGIN_PATH'] = plugin_path
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(plugin_path, 'platforms')
        return True
    
    return False

setup_qt_plugin_path()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from qasync import QEventLoop

from src.core.config import Config
from src.core.word_manager import WordManager
from src.core.dictionary import DictionaryAPI
from src.core.spaced_repetition import SpacedRepetitionManager
from src.core.learning_tracker import LearningTracker
from src.ui.main_window import MainWindow


class WordReciteApp:
    """Main application controller"""
    
    def __init__(self):
        # Setup Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Word Recite")
        self.app.setOrganizationName("WordRecite")
        
        # Setup async event loop
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        
        # Initialize components
        self.config = Config()
        
        # Setup data directories
        data_dir = Path.home() / ".word_recite" / "data"
        cache_dir = Path.home() / ".word_recite" / "data" / "cache"
        review_dir = Path.home() / ".word_recite" / "data" / "reviews"
        tracker_dir = Path.home() / ".word_recite" / "data" / "tracker"
        data_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        review_dir.mkdir(parents=True, exist_ok=True)
        tracker_dir.mkdir(parents=True, exist_ok=True)
        
        self.word_manager = WordManager(data_dir)
        self.dictionary_api = DictionaryAPI(cache_dir)
        self.sr_manager = SpacedRepetitionManager(review_dir)
        self.learning_tracker = LearningTracker(tracker_dir)
        
        # Create main window
        self.main_window = MainWindow(
            self.config,
            self.word_manager,
            self.dictionary_api,
            self.sr_manager,
            self.learning_tracker
        )
    
    def run(self):
        """Run the application"""
        self.main_window.show()
        
        # Increment study session count
        stats = self.config.get("learning_stats", {})
        sessions = stats.get("study_sessions", 0)
        self.config.update_learning_stats(study_sessions=sessions + 1)
        
        # Run event loop
        with self.loop:
            sys.exit(self.loop.run_forever())
    
    def cleanup(self):
        """Cleanup resources"""
        asyncio.create_task(self.dictionary_api.close())


def main():
    """Application entry point"""
    app = WordReciteApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
