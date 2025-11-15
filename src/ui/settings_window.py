from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QCheckBox, QFileDialog,
                             QTextEdit, QGroupBox, QRadioButton, QButtonGroup,
                             QMessageBox, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from pathlib import Path

from ..core.config import Config
from ..core.word_manager import WordManager


class SettingsWindow(QDialog):
    """Settings dialog for configuration"""
    
    def __init__(self, parent, config: Config, word_manager: WordManager):
        super().__init__(parent)
        self.config = config
        self.word_manager = word_manager
        
        self.setWindowTitle("Settings")
        self.setFixedSize(600, 700)
        self.setModal(True)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Word Import Section
        import_group = self._create_import_section()
        layout.addWidget(import_group)
        
        # Display Settings Section
        display_group = self._create_display_section()
        layout.addWidget(display_group)
        
        # Theme Section
        theme_group = self._create_theme_section()
        layout.addWidget(theme_group)
        
        # Statistics Section
        stats_group = self._create_statistics_section()
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("accentButton")
        save_btn.clicked.connect(self._save_and_close)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_import_section(self) -> QGroupBox:
        """Create word import section"""
        group = QGroupBox("Word Import")
        layout = QVBoxLayout(group)
        
        # Import from file button
        file_btn = QPushButton("Import from File (.txt)")
        file_btn.clicked.connect(self._import_from_file)
        layout.addWidget(file_btn)
        
        # Or label
        or_label = QLabel("or paste words below:")
        or_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(or_label)
        
        # Text input for pasting
        self.word_input = QTextEdit()
        self.word_input.setPlaceholderText("Paste words here (separated by space, comma, or newline)")
        self.word_input.setMaximumHeight(100)
        layout.addWidget(self.word_input)
        
        # Import button for pasted text
        paste_import_btn = QPushButton("Import Pasted Words")
        paste_import_btn.clicked.connect(self._import_from_paste)
        layout.addWidget(paste_import_btn)
        
        # Current wordlist selector
        wordlist_layout = QHBoxLayout()
        wordlist_layout.addWidget(QLabel("Current Wordlist:"))
        
        self.wordlist_combo = QComboBox()
        self.wordlist_combo.currentTextChanged.connect(self._load_selected_wordlist)
        wordlist_layout.addWidget(self.wordlist_combo)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_wordlist)
        wordlist_layout.addWidget(delete_btn)
        
        layout.addLayout(wordlist_layout)
        
        return group
    
    def _create_display_section(self) -> QGroupBox:
        """Create display settings section"""
        group = QGroupBox("Display Settings")
        layout = QVBoxLayout(group)
        
        # Display interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Word Display Interval:"))
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["5 seconds", "10 seconds", "15 seconds", "30 seconds"])
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addStretch()
        
        layout.addLayout(interval_layout)
        
        # Display options
        self.show_phonetic_cb = QCheckBox("Show Phonetic Symbols")
        layout.addWidget(self.show_phonetic_cb)
        
        self.show_definitions_cb = QCheckBox("Show English Definitions")
        layout.addWidget(self.show_definitions_cb)
        
        self.show_examples_cb = QCheckBox("Show Example Sentences")
        layout.addWidget(self.show_examples_cb)
        
        return group
    
    def _create_theme_section(self) -> QGroupBox:
        """Create theme selection section"""
        group = QGroupBox("Appearance")
        layout = QVBoxLayout(group)
        
        theme_layout = QHBoxLayout()
        
        self.theme_group = QButtonGroup()
        
        self.light_radio = QRadioButton("Light Theme")
        self.theme_group.addButton(self.light_radio, 0)
        theme_layout.addWidget(self.light_radio)
        
        self.dark_radio = QRadioButton("Dark Theme")
        self.theme_group.addButton(self.dark_radio, 1)
        theme_layout.addWidget(self.dark_radio)
        
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout)
        
        return group
    
    def _create_statistics_section(self) -> QGroupBox:
        """Create statistics display section"""
        group = QGroupBox("Learning Statistics")
        layout = QVBoxLayout(group)
        
        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)
        
        reset_btn = QPushButton("Reset Statistics")
        reset_btn.clicked.connect(self._reset_statistics)
        layout.addWidget(reset_btn)
        
        return group
    
    def _load_settings(self):
        """Load current settings into UI"""
        # Load wordlists
        self._refresh_wordlist_combo()
        
        # Load display interval
        interval = self.config.get("display_interval", 10)
        interval_map = {5: 0, 10: 1, 15: 2, 30: 3}
        self.interval_combo.setCurrentIndex(interval_map.get(interval, 1))
        
        # Load display options
        self.show_phonetic_cb.setChecked(self.config.get("show_phonetic", True))
        self.show_definitions_cb.setChecked(self.config.get("show_definitions", True))
        self.show_examples_cb.setChecked(self.config.get("show_examples", True))
        
        # Load theme
        theme = self.config.get("theme", "light")
        if theme == "dark":
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
        
        # Load statistics
        self._update_statistics()
    
    def _refresh_wordlist_combo(self):
        """Refresh wordlist dropdown"""
        self.wordlist_combo.clear()
        wordlists = self.word_manager.list_wordlists()
        self.wordlist_combo.addItems(wordlists)
        
        # Select current wordlist
        current = self.config.get("current_wordlist")
        if current and current in wordlists:
            self.wordlist_combo.setCurrentText(current)
    
    def _update_statistics(self):
        """Update statistics display"""
        stats = self.config.get("learning_stats", {})
        total_words = stats.get("total_words_learned", 0)
        sessions = stats.get("study_sessions", 0)
        total_time = stats.get("total_study_time", 0)
        
        # Format time
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        
        stats_text = f"""
        Total Words Learned: {total_words}
        Study Sessions: {sessions}
        Total Study Time: {hours}h {minutes}m
        """
        
        self.stats_label.setText(stats_text.strip())
    
    def _import_from_file(self):
        """Import words from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Word List File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                # Get list name
                list_name = Path(file_path).stem
                wordlist = self.word_manager.import_from_file(Path(file_path), list_name)
                
                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Imported {len(wordlist.words)} words into '{list_name}'"
                )
                
                self._refresh_wordlist_combo()
                self.wordlist_combo.setCurrentText(list_name)
                
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", str(e))
    
    def _import_from_paste(self):
        """Import words from pasted text"""
        text = self.word_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "No Input", "Please paste words first")
            return
        
        # Ask for list name
        from PyQt6.QtWidgets import QInputDialog
        list_name, ok = QInputDialog.getText(
            self,
            "Word List Name",
            "Enter a name for this word list:"
        )
        
        if ok and list_name:
            try:
                wordlist = self.word_manager.import_from_text(text, list_name)
                
                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Imported {len(wordlist.words)} words into '{list_name}'"
                )
                
                self.word_input.clear()
                self._refresh_wordlist_combo()
                self.wordlist_combo.setCurrentText(list_name)
                
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", str(e))
    
    def _load_selected_wordlist(self, name: str):
        """Load selected wordlist"""
        if not name:
            return
        
        wordlist = self.word_manager.load_wordlist(name)
        if wordlist:
            self.word_manager.set_current_wordlist(wordlist)
            self.config.set("current_wordlist", name)
    
    def _delete_wordlist(self):
        """Delete current wordlist"""
        current = self.wordlist_combo.currentText()
        if not current:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{current}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.word_manager.delete_wordlist(current)
            self._refresh_wordlist_combo()
            
            if self.config.get("current_wordlist") == current:
                self.config.set("current_wordlist", None)
                self.word_manager.set_current_wordlist(None)
    
    def _reset_statistics(self):
        """Reset learning statistics"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all statistics?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.update_learning_stats(
                total_words_learned=0,
                study_sessions=0,
                total_study_time=0
            )
            self._update_statistics()
    
    def _save_and_close(self):
        """Save settings and close"""
        # Save display interval
        interval_map = {0: 5, 1: 10, 2: 15, 3: 30}
        interval = interval_map.get(self.interval_combo.currentIndex(), 10)
        self.config.set("display_interval", interval)
        
        # Save display options
        self.config.set("show_phonetic", self.show_phonetic_cb.isChecked())
        self.config.set("show_definitions", self.show_definitions_cb.isChecked())
        self.config.set("show_examples", self.show_examples_cb.isChecked())
        
        # Save theme
        theme = "dark" if self.dark_radio.isChecked() else "light"
        self.config.set("theme", theme)
        
        self.accept()
