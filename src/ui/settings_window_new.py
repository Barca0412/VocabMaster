from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QCheckBox, QFileDialog,
                             QTextEdit, QGroupBox, QRadioButton, QButtonGroup,
                             QMessageBox, QListWidget, QListWidgetItem, QWidget,
                             QScrollArea, QFrame, QSizePolicy, QLineEdit)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QLinearGradient
from pathlib import Path

from ..core.config import Config
from ..core.word_manager import WordManager


class ModernButton(QPushButton):
    """Custom button with modern styling and hover effects"""
    
    def __init__(self, text, accent=False, parent=None):
        super().__init__(text, parent)
        self.accent = accent
        self.setMinimumHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_animation()
    
    def _setup_animation(self):
        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(46)
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(44)
        self.animation.start()
        super().leaveEvent(event)


class WordInputArea(QTextEdit):
    """Modern text input with placeholder animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMaximumHeight(200)
        self.setPlaceholderText("Paste your vocabulary here... (Words can be separated by spaces, commas, or newlines)")
        
        # Custom styling
        font = QFont("SF Mono", 13)
        font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 102)
        self.setFont(font)


class SectionCard(QFrame):
    """Modern card-style section container"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("sectionCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        layout.addLayout(self.content_layout)
        
        # Fade-in animation
        self.opacity_effect = None
    
    def add_widget(self, widget):
        self.content_layout.addWidget(widget)


class SettingsWindow(QDialog):
    """Modern settings dialog with Anthropic-inspired aesthetics"""
    
    def __init__(self, parent, config: Config, word_manager: WordManager):
        super().__init__(parent)
        self.config = config
        self.word_manager = word_manager
        
        self.setWindowTitle("Word Recite — Settings")
        self.setMinimumSize(720, 800)
        self.setModal(True)
        
        self._setup_ui()
        self._load_settings()
        self._apply_styles()
        
        # Staggered reveal animation
        QTimer.singleShot(50, lambda: self._animate_sections(0))
    
    def _setup_ui(self):
        """Setup UI with modern card-based layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with gradient
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(32, 24, 32, 24)
        
        # Word Import Section
        self.import_card = self._create_import_section()
        content_layout.addWidget(self.import_card)
        
        # Learning Goal Section
        self.goal_card = self._create_learning_goal_section()
        content_layout.addWidget(self.goal_card)
        
        # Display Settings Section
        self.display_card = self._create_display_section()
        content_layout.addWidget(self.display_card)
        
        # Appearance Section
        self.appearance_card = self._create_appearance_section()
        content_layout.addWidget(self.appearance_card)
        
        # Learning Statistics Section
        self.stats_card = self._create_statistics_section()
        content_layout.addWidget(self.stats_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Footer with action buttons
        footer = self._create_footer()
        main_layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """Create gradient header"""
        header = QFrame()
        header.setObjectName("header")
        header.setMinimumHeight(80)
        header.setMaximumHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(32, 0, 32, 0)
        
        title_layout = QVBoxLayout()
        title = QLabel("Settings")
        title.setObjectName("headerTitle")
        
        subtitle = QLabel("Customize your learning experience")
        subtitle.setObjectName("headerSubtitle")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        return header
    
    def _create_import_section(self) -> SectionCard:
        """Create word import section with modern UI"""
        card = SectionCard("Word Lists")
        
        # Built-in wordlists info
        info_label = QLabel("Built-in wordlists: CET-4 and CET-6 are pre-loaded for you")
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        card.add_widget(info_label)
        
        # Current wordlist selector
        selector_container = QWidget()
        selector_layout = QHBoxLayout(selector_container)
        selector_layout.setContentsMargins(0, 8, 0, 8)
        
        wordlist_label = QLabel("Active Wordlist:")
        wordlist_label.setObjectName("fieldLabel")
        selector_layout.addWidget(wordlist_label)
        
        self.wordlist_combo = QComboBox()
        self.wordlist_combo.setMinimumHeight(40)
        self.wordlist_combo.currentTextChanged.connect(self._load_selected_wordlist)
        selector_layout.addWidget(self.wordlist_combo, 1)
        
        delete_btn = ModernButton("Delete")
        delete_btn.clicked.connect(self._delete_wordlist)
        delete_btn.setMaximumWidth(100)
        selector_layout.addWidget(delete_btn)
        
        card.add_widget(selector_container)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("divider")
        card.add_widget(divider)
        
        # Import from file
        import_file_label = QLabel("Import from File")
        import_file_label.setObjectName("subsectionLabel")
        card.add_widget(import_file_label)
        
        file_btn = ModernButton("Choose Text File (.txt)", accent=False)
        file_btn.clicked.connect(self._import_from_file)
        card.add_widget(file_btn)
        
        # Import from text
        import_text_label = QLabel("Or Paste Vocabulary")
        import_text_label.setObjectName("subsectionLabel")
        card.add_widget(import_text_label)
        
        self.word_input = WordInputArea()
        card.add_widget(self.word_input)
        
        paste_import_btn = ModernButton("Import Pasted Words", accent=True)
        paste_import_btn.clicked.connect(self._import_from_paste)
        card.add_widget(paste_import_btn)
        
        return card
    
    def _create_learning_goal_section(self) -> SectionCard:
        """Create learning goal section"""
        card = SectionCard("Learning Goal")
        
        # Description
        desc_label = QLabel("设置你的学习目标，我们将为你生成个性化的例句和学习建议")
        desc_label.setObjectName("infoLabel")
        desc_label.setWordWrap(True)
        card.add_widget(desc_label)
        
        # Goal input
        goal_container = QWidget()
        goal_layout = QVBoxLayout(goal_container)
        goal_layout.setContentsMargins(0, 8, 0, 8)
        goal_layout.setSpacing(8)
        
        goal_label = QLabel("我的学习目标：")
        goal_label.setObjectName("fieldLabel")
        goal_layout.addWidget(goal_label)
        
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("例如：准备托福考试、提升商务英语能力、阅读英文技术文档...")
        self.goal_input.setMinimumHeight(40)
        goal_layout.addWidget(self.goal_input)
        
        card.add_widget(goal_container)
        
        return card
    
    def _create_display_section(self) -> SectionCard:
        """Create display settings section"""
        card = SectionCard("Display Settings")
        
        # Display interval
        interval_container = QWidget()
        interval_layout = QHBoxLayout(interval_container)
        interval_layout.setContentsMargins(0, 0, 0, 0)
        
        interval_label = QLabel("Word Display Interval:")
        interval_label.setObjectName("fieldLabel")
        interval_layout.addWidget(interval_label)
        
        self.interval_combo = QComboBox()
        self.interval_combo.setMinimumHeight(40)
        self.interval_combo.addItems(["5 seconds", "10 seconds", "15 seconds", "30 seconds", "60 seconds"])
        interval_layout.addWidget(self.interval_combo, 1)
        
        card.add_widget(interval_container)
        
        # Display options with modern checkboxes
        options_label = QLabel("Content Display Options")
        options_label.setObjectName("subsectionLabel")
        card.add_widget(options_label)
        
        self.show_phonetic_cb = QCheckBox("Show phonetic symbols and pronunciation")
        self.show_phonetic_cb.setMinimumHeight(36)
        card.add_widget(self.show_phonetic_cb)
        
        self.show_definitions_cb = QCheckBox("Show English definitions")
        self.show_definitions_cb.setMinimumHeight(36)
        card.add_widget(self.show_definitions_cb)
        
        self.show_examples_cb = QCheckBox("Show example sentences")
        self.show_examples_cb.setMinimumHeight(36)
        card.add_widget(self.show_examples_cb)
        
        self.auto_start_cb = QCheckBox("Auto-start playback when app launches")
        self.auto_start_cb.setMinimumHeight(36)
        card.add_widget(self.auto_start_cb)
        
        return card
    
    def _create_appearance_section(self) -> SectionCard:
        """Create theme selection section"""
        card = SectionCard("Appearance")
        
        theme_container = QWidget()
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(12)
        
        self.theme_group = QButtonGroup()
        
        self.light_radio = QRadioButton("Light Theme")
        self.light_radio.setMinimumHeight(40)
        self.theme_group.addButton(self.light_radio, 0)
        theme_layout.addWidget(self.light_radio)
        
        self.dark_radio = QRadioButton("Dark Theme")
        self.dark_radio.setMinimumHeight(40)
        self.theme_group.addButton(self.dark_radio, 1)
        theme_layout.addWidget(self.dark_radio)
        
        theme_layout.addStretch()
        
        card.add_widget(theme_container)
        
        return card
    
    def _create_statistics_section(self) -> SectionCard:
        """Create statistics display section"""
        card = SectionCard("Learning Progress")
        
        self.stats_label = QLabel()
        self.stats_label.setObjectName("statsText")
        self.stats_label.setWordWrap(True)
        card.add_widget(self.stats_label)
        
        reset_container = QWidget()
        reset_layout = QHBoxLayout(reset_container)
        reset_layout.setContentsMargins(0, 8, 0, 0)
        
        reset_layout.addStretch()
        reset_btn = ModernButton("Reset Statistics")
        reset_btn.clicked.connect(self._reset_statistics)
        reset_btn.setMaximumWidth(200)
        reset_layout.addWidget(reset_btn)
        
        card.add_widget(reset_container)
        
        return card
    
    def _create_footer(self) -> QWidget:
        """Create footer with action buttons"""
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setMinimumHeight(80)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(32, 16, 32, 16)
        
        layout.addStretch()
        
        cancel_btn = ModernButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumWidth(120)
        layout.addWidget(cancel_btn)
        
        save_btn = ModernButton("Save Changes", accent=True)
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save_and_close)
        save_btn.setMinimumWidth(140)
        layout.addWidget(save_btn)
        
        return footer
    
    def _animate_sections(self, index):
        """Staggered reveal animation for sections"""
        cards = [self.import_card, self.goal_card, self.display_card, self.appearance_card, self.stats_card]
        
        if index < len(cards):
            # Skip animation for now to avoid crash
            QTimer.singleShot(100, lambda: self._animate_sections(index + 1))
    
    def _apply_styles(self):
        """Apply modern Anthropic-inspired styles"""
        # Use a distinctive font combination
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FAFAF8, stop:1 #F5F5F0);
                font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
            }
            
            #header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2D3748, stop:0.5 #4A5568, stop:1 #2D3748);
                border-bottom: 2px solid #E2E8F0;
            }
            
            #headerTitle {
                font-size: 28px;
                font-weight: 600;
                color: white;
                letter-spacing: -0.5px;
            }
            
            #headerSubtitle {
                font-size: 14px;
                color: #CBD5E0;
                letter-spacing: 0.3px;
                margin-top: 2px;
            }
            
            #footer {
                background: #FFFFFF;
                border-top: 1px solid #E2E8F0;
            }
            
            #sectionCard {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            }
            
            #sectionTitle {
                font-size: 18px;
                font-weight: 600;
                color: #1A202C;
                letter-spacing: -0.3px;
            }
            
            #subsectionLabel {
                font-size: 13px;
                font-weight: 500;
                color: #4A5568;
                letter-spacing: 0.2px;
                text-transform: uppercase;
                margin-top: 4px;
            }
            
            #fieldLabel {
                font-size: 14px;
                font-weight: 500;
                color: #2D3748;
            }
            
            #infoLabel {
                font-size: 13px;
                color: #718096;
                background: #EDF2F7;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 3px solid #4299E1;
            }
            
            #statsText {
                font-size: 15px;
                line-height: 1.8;
                color: #2D3748;
                font-family: 'SF Mono', 'Menlo', monospace;
                background: #F7FAFC;
                padding: 16px;
                border-radius: 8px;
            }
            
            #divider {
                background: #E2E8F0;
                max-height: 1px;
            }
            
            QPushButton {
                background: #EDF2F7;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 20px;
                font-size: 14px;
                font-weight: 500;
                letter-spacing: 0.2px;
                transition: all 0.2s ease;
            }
            
            QPushButton:hover {
                background: #E2E8F0;
                border-color: #CBD5E0;
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background: #CBD5E0;
                transform: translateY(0);
            }
            
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3182CE, stop:1 #2C5282);
                color: white;
                border: none;
                font-weight: 600;
            }
            
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2C5282, stop:1 #2A4365);
            }
            
            QComboBox {
                background: #F7FAFC;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }
            
            QComboBox:hover {
                border-color: #CBD5E0;
                background: #EDF2F7;
            }
            
            QComboBox:focus {
                border-color: #3182CE;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 12px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #718096;
                margin-right: 8px;
            }
            
            QComboBox QAbstractItemView {
                background: white;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                selection-background-color: #EBF8FF;
                selection-color: #2C5282;
                padding: 4px;
            }
            
            QTextEdit {
                background: #F7FAFC;
                color: #2D3748;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.6;
            }
            
            QTextEdit:focus {
                border-color: #3182CE;
                background: white;
            }
            
            QCheckBox {
                color: #2D3748;
                spacing: 10px;
                font-size: 14px;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #CBD5E0;
                border-radius: 5px;
                background: #F7FAFC;
            }
            
            QCheckBox::indicator:hover {
                border-color: #3182CE;
                background: #EBF8FF;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3182CE, stop:1 #2C5282);
                border-color: #2C5282;
                image: none;
            }
            
            QCheckBox::indicator:checked:after {
                content: "✓";
            }
            
            QRadioButton {
                color: #2D3748;
                spacing: 10px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
                background: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
            }
            
            QRadioButton:hover {
                background: #EDF2F7;
                border-color: #CBD5E0;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #CBD5E0;
                border-radius: 9px;
                background: white;
            }
            
            QRadioButton::indicator:checked {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5, stop:0 #3182CE, stop:0.6 #3182CE, 
                    stop:0.6 white, stop:1 white);
                border-color: #3182CE;
            }
            
            QRadioButton:checked {
                background: #EBF8FF;
                border-color: #3182CE;
                color: #2C5282;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: #F7FAFC;
                width: 10px;
                border-radius: 5px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: #CBD5E0;
                border-radius: 5px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #A0AEC0;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
    
    def _load_settings(self):
        """Load current settings into UI"""
        # Load wordlists
        self._refresh_wordlist_combo()
        
        # Load learning goal
        learning_goal = self.config.get("learning_goal", "")
        self.goal_input.setText(learning_goal)
        
        # Load display interval
        interval = self.config.get("display_interval", 10)
        interval_map = {5: 0, 10: 1, 15: 2, 30: 3, 60: 4}
        self.interval_combo.setCurrentIndex(interval_map.get(interval, 1))
        
        # Load display options
        self.show_phonetic_cb.setChecked(self.config.get("show_phonetic", True))
        self.show_definitions_cb.setChecked(self.config.get("show_definitions", True))
        self.show_examples_cb.setChecked(self.config.get("show_examples", True))
        self.auto_start_cb.setChecked(self.config.get("auto_start_playback", False))
        
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
        <div style='font-size: 15px; line-height: 2.0;'>
        <b>Total Words Learned:</b> {total_words}<br/>
        <b>Study Sessions:</b> {sessions}<br/>
        <b>Total Study Time:</b> {hours}h {minutes}m
        </div>
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
                    f"Successfully imported {len(wordlist.words)} words into '{list_name}'"
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
                    f"Successfully imported {len(wordlist.words)} words into '{list_name}'"
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
        # Save learning goal
        learning_goal = self.goal_input.text().strip()
        self.config.set("learning_goal", learning_goal)
        
        # Save display interval
        interval_map = {0: 5, 1: 10, 2: 15, 3: 30, 4: 60}
        interval = interval_map.get(self.interval_combo.currentIndex(), 10)
        self.config.set("display_interval", interval)
        
        # Save display options
        self.config.set("show_phonetic", self.show_phonetic_cb.isChecked())
        self.config.set("show_definitions", self.show_definitions_cb.isChecked())
        self.config.set("show_examples", self.show_examples_cb.isChecked())
        self.config.set("auto_start_playback", self.auto_start_cb.isChecked())
        
        # Save theme
        theme = "dark" if self.dark_radio.isChecked() else "light"
        self.config.set("theme", theme)
        
        self.accept()
