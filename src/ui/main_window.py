from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
import asyncio
from pathlib import Path
from typing import Optional
from qasync import asyncSlot

from ..core.config import Config
from ..core.word_manager import WordManager, WordList, Word
from ..core.dictionary import DictionaryAPI
from ..core.spaced_repetition import SpacedRepetitionManager
from ..core.learning_tracker import LearningTracker
from ..core.llm_generator import LLMOptionGenerator
from .themes import get_theme, get_stylesheet


class MainWindow(QMainWindow):
    """Main floating window for word display"""
    
    def __init__(self, config: Config, word_manager: WordManager, dictionary_api: DictionaryAPI, 
                 sr_manager: SpacedRepetitionManager, learning_tracker: LearningTracker):
        super().__init__()
        self.config = config
        self.word_manager = word_manager
        self.dictionary_api = dictionary_api
        self.sr_manager = sr_manager
        self.learning_tracker = learning_tracker
        
        self.is_playing = False
        self.drag_position = None
        
        # Initialize LLM generator for personalized examples
        try:
            self.llm_generator = LLMOptionGenerator()
        except Exception as e:
            print(f"Failed to initialize LLM generator: {e}")
            self.llm_generator = None
        
        self._setup_ui()
        self._setup_timer()
        self._apply_theme()
        self._restore_position()
        
        # Load last used wordlist
        last_wordlist = self.config.get("current_wordlist")
        if last_wordlist:
            wordlist = self.word_manager.load_wordlist(last_wordlist)
            if wordlist:
                self.word_manager.set_current_wordlist(wordlist)
                self._load_current_word()
        
        # Auto-start playback if configured
        if self.config.get("auto_start_playback", False) and self.word_manager.current_wordlist:
            self._toggle_playback()
    
    def _setup_ui(self):
        """Setup the UI components"""
        self.setWindowTitle("Word Recite")
        self.setFixedSize(400, 500)
        
        # Window flags for always-on-top
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - no margins to make toolbar full width
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Content area container (with padding)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)
        
        # Word display area (no title bar)
        self.word_label = QLabel("Import words to start")
        self.word_label.setObjectName("wordLabel")
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setWordWrap(True)
        content_layout.addWidget(self.word_label)
        
        # Phonetic
        self.phonetic_label = QLabel("")
        self.phonetic_label.setObjectName("phoneticLabel")
        self.phonetic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.phonetic_label)
        
        # Definitions
        self.definition_label = QLabel("")
        self.definition_label.setObjectName("definitionLabel")
        self.definition_label.setWordWrap(True)
        self.definition_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(self.definition_label)
        
        # Chinese translations
        self.translation_label = QLabel("")
        self.translation_label.setObjectName("translationLabel")
        self.translation_label.setWordWrap(True)
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(self.translation_label)
        
        # Examples
        self.example_label = QLabel("")
        self.example_label.setObjectName("exampleLabel")
        self.example_label.setWordWrap(True)
        self.example_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(self.example_label)
        
        content_layout.addStretch()
        
        # Bottom controls (inside content area)
        control_layout = self._create_controls()
        content_layout.addLayout(control_layout)
        
        # Add content area to main layout (takes ~90% of space)
        layout.addWidget(content_widget, 9)
        
        # Bottom navbar with settings and theme toggle (takes ~10% of space)
        navbar = self._create_bottom_navbar()
        layout.addWidget(navbar, 1)
    
    def _create_bottom_navbar(self) -> QWidget:
        """Create bottom navbar with settings and theme toggle - takes full width and ~10% height"""
        from PyQt6.QtWidgets import QFrame
        
        navbar = QFrame()
        navbar.setObjectName("bottomNavbar")
        # No fixed height - will be sized by layout stretch factor (1 out of 10 total)
        
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(16, 0, 16, 0)
        navbar_layout.setSpacing(12)
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setObjectName("navbarButton")
        settings_btn.clicked.connect(self._open_settings)
        navbar_layout.addWidget(settings_btn)
        
        # Quiz button
        quiz_btn = QPushButton("Quiz")
        quiz_btn.setObjectName("navbarButton")
        quiz_btn.clicked.connect(self._open_quiz)
        navbar_layout.addWidget(quiz_btn)
        
        # Report button
        report_btn = QPushButton("Report")
        report_btn.setObjectName("navbarButton")
        report_btn.clicked.connect(self._show_report)
        navbar_layout.addWidget(report_btn)
        
        navbar_layout.addStretch()
        
        # Theme toggle button
        current_theme = self.config.get("theme", "light")
        theme_text = "Dark" if current_theme == "light" else "Light"
        self.theme_btn = QPushButton(f"→ {theme_text}")
        self.theme_btn.setObjectName("navbarButton")
        self.theme_btn.clicked.connect(self._toggle_theme)
        navbar_layout.addWidget(self.theme_btn)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setObjectName("navbarButton")
        close_btn.setFixedWidth(40)
        close_btn.clicked.connect(self.close)
        navbar_layout.addWidget(close_btn)
        
        return navbar
    
    def _create_controls(self) -> QHBoxLayout:
        """Create control buttons"""
        control_layout = QHBoxLayout()
        
        # Import button
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self._import_words)
        control_layout.addWidget(import_btn)
        
        # Previous button
        prev_btn = QPushButton("◀")
        prev_btn.clicked.connect(self._previous_word)
        control_layout.addWidget(prev_btn)
        
        # Play/Pause button
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("accentButton")
        self.play_btn.clicked.connect(self._toggle_playback)
        control_layout.addWidget(self.play_btn)
        
        # Next button
        next_btn = QPushButton("▶")
        next_btn.clicked.connect(self._next_word)
        control_layout.addWidget(next_btn)
        
        return control_layout
    
    def _setup_timer(self):
        """Setup auto-advance timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._next_word)
    
    def _apply_theme(self):
        """Apply current theme"""
        theme_name = self.config.get("theme", "light")
        theme = get_theme(theme_name)
        stylesheet = get_stylesheet(theme)
        self.setStyleSheet(stylesheet)
    
    def _restore_position(self):
        """Restore window position from config"""
        pos = self.config.get("window_position", {})
        x = pos.get("x")
        y = pos.get("y")
        
        if x is not None and y is not None:
            self.move(x, y)
        else:
            # Default to bottom-right corner
            screen = self.screen().geometry()
            self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 60)
    
    def _save_position(self):
        """Save window position to config"""
        pos = self.pos()
        self.config.set("window_position", {"x": pos.x(), "y": pos.y()})
    
    def _import_words(self):
        """Import words from file or show settings"""
        from .settings_window_new import SettingsWindow
        settings = SettingsWindow(self, self.config, self.word_manager)
        settings.exec()
        
        # Reload if wordlist changed
        if self.word_manager.current_wordlist:
            self._load_current_word()
    
    def _load_current_word(self):
        """Load and display current word with definitions"""
        if not self.word_manager.current_wordlist:
            return
        
        word = self.word_manager.current_wordlist.get_current_word()
        if not word:
            return
        
        # 记录单词浏览
        self.learning_tracker.track_word_view(word.word)
        
        # Display word immediately
        self.word_label.setText(word.word)
        self.phonetic_label.setText("Loading...")
        self.definition_label.setText("")
        self.translation_label.setText("")
        self.example_label.setText("")
        
        # Fetch definitions asynchronously using QTimer
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._fetch_and_display_definitions(word))
            else:
                # Schedule for later when loop is running
                QTimer.singleShot(0, lambda: asyncio.ensure_future(self._fetch_and_display_definitions(word)))
        except RuntimeError:
            # No event loop yet, schedule for later
            QTimer.singleShot(0, lambda: asyncio.ensure_future(self._fetch_and_display_definitions(word)))
    
    async def _fetch_and_display_definitions(self, word: Word):
        """Fetch and display word definitions"""
        try:
            definitions = await self.dictionary_api.lookup(word.word)
            word.definitions = definitions
            
            # Update display
            self._display_word(word)
        except Exception as e:
            print(f"Failed to fetch definitions: {e}")
            self.phonetic_label.setText("")
    
    def _display_word(self, word: Word):
        """Display word with all information"""
        self.word_label.setText(word.word.capitalize())
        
        # Phonetic
        phonetic = ""
        if word.definitions:
            mw = word.definitions.get("merriam_webster", {})
            yd = word.definitions.get("youdao", {})
            phonetic = mw.get("phonetic") or yd.get("phonetic", "")
        
        if phonetic and self.config.get("show_phonetic", True):
            self.phonetic_label.setText(f"/{phonetic}/")
        else:
            self.phonetic_label.setText("")
        
        # Definitions (English)
        if word.definitions and self.config.get("show_definitions", True):
            mw = word.definitions.get("merriam_webster", {})
            definitions = mw.get("definitions", [])
            if definitions:
                def_text = "\n".join([f"• {d}" for d in definitions[:3]])
                self.definition_label.setText(def_text)
            else:
                self.definition_label.setText("")
        else:
            self.definition_label.setText("")
        
        # Chinese translations
        if word.definitions:
            yd = word.definitions.get("youdao", {})
            translations = yd.get("translations", [])
            if translations:
                trans_text = "中文: " + "; ".join(translations[:3])
                self.translation_label.setText(trans_text)
            else:
                self.translation_label.setText("")
        else:
            self.translation_label.setText("")
        
        # Examples - use LLM for personalized examples if available
        if word.definitions and self.config.get("show_examples", True):
            learning_goal = self.config.get("learning_goal", "")
            
            if self.llm_generator and learning_goal:
                # Use LLM to generate personalized example
                try:
                    # Get definition for context
                    definition = ""
                    if word.definitions:
                        yd = word.definitions.get("youdao", {})
                        translations = yd.get("translations", [])
                        if translations:
                            definition = translations[0]
                    
                    if definition:
                        personalized_example = self.llm_generator.generate_personalized_example(
                            word.word, definition, learning_goal
                        )
                        self.example_label.setText(f'"{personalized_example}"')
                    else:
                        self._set_default_examples(word)
                except Exception as e:
                    print(f"Failed to generate personalized example: {e}")
                    self._set_default_examples(word)
            else:
                self._set_default_examples(word)
        else:
            self.example_label.setText("")
    
    def _set_default_examples(self, word: Word):
        """Set default examples from dictionary"""
        mw = word.definitions.get("merriam_webster", {})
        examples = mw.get("examples", [])
        if examples:
            ex_text = "\n".join([f'"{ex}"' for ex in examples[:2]])
            self.example_label.setText(ex_text)
        else:
            self.example_label.setText("")
    
    def _next_word(self):
        """Go to next word"""
        if not self.word_manager.current_wordlist:
            return
        
        self.word_manager.current_wordlist.next_word()
        self._load_current_word()
    
    def _previous_word(self):
        """Go to previous word"""
        if not self.word_manager.current_wordlist:
            return
        
        self.word_manager.current_wordlist.previous_word()
        self._load_current_word()
    
    def _toggle_playback(self):
        """Toggle auto-advance playback"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            interval = self.config.get("display_interval", 10) * 1000
            self.timer.start(interval)
            self.play_btn.setText("⏸")
        else:
            self.timer.stop()
            self.play_btn.setText("▶")
    
    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.config.get("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.config.set("theme", new_theme)
        self._apply_theme()
        
        # Update button text
        theme_text = "Dark" if new_theme == "light" else "Light"
        self.theme_btn.setText(f"→ {theme_text}")
    
    def _show_report(self):
        """Show learning report"""
        from .report_window import ReportWindow
        report = ReportWindow(self, self.config, self.learning_tracker)
        report.exec()
    
    def _open_quiz(self):
        """Open quiz window"""
        from .quiz_window import QuizWindow
        
        # 确保有当前词汇表
        if not self.word_manager.current_wordlist:
            QMessageBox.warning(
                self,
                "没有词汇表",
                "请先导入或选择一个词汇表"
            )
            return
        
        # 导入当前词汇表的单词到复习系统
        words = [word.word for word in self.word_manager.current_wordlist.words]
        self.sr_manager.import_words(words)
        
        quiz = QuizWindow(self, self.config, self.word_manager, 
                         self.dictionary_api, self.sr_manager, self.learning_tracker)
        quiz.exec()
    
    def _open_settings(self):
        """Open settings window"""
        from .settings_window_new import SettingsWindow
        settings = SettingsWindow(self, self.config, self.word_manager)
        if settings.exec():
            self._apply_theme()
            
            # Update theme button text
            current_theme = self.config.get("theme", "light")
            theme_text = "Dark" if current_theme == "light" else "Light"
            self.theme_btn.setText(f"→ {theme_text}")
            
            # Update timer interval if playing
            if self.is_playing:
                interval = self.config.get("display_interval", 10) * 1000
                self.timer.setInterval(interval)
    
    # Mouse event handlers for dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            self._save_position()
            event.accept()
    
    def closeEvent(self, event):
        """Handle window close"""
        self._save_position()
        
        # Save current wordlist state
        if self.word_manager.current_wordlist:
            self.word_manager.save_wordlist(self.word_manager.current_wordlist)
        
        event.accept()
