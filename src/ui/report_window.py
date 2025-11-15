"""
Report Window - 学习报告窗口
展示详细的学习数据和个性化建议
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QWidget, QScrollArea, QFrame, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..core.config import Config
from ..core.learning_tracker import LearningTracker


class ReportWindow(QDialog):
    """学习报告窗口"""
    
    def __init__(self, parent, config: Config, learning_tracker: LearningTracker):
        super().__init__(parent)
        self.config = config
        self.learning_tracker = learning_tracker
        
        self.setWindowTitle("Learning Report - 学习报告")
        self.setMinimumSize(650, 750)
        self.setModal(True)
        
        self._setup_ui()
        self._load_report()
        self._apply_theme()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Report content (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(32, 24, 32, 24)
        content_layout.setSpacing(20)
        
        # Report text
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFrameShape(QFrame.Shape.NoFrame)
        content_layout.addWidget(self.report_text)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Footer
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """创建头部"""
        header = QFrame()
        header.setObjectName("reportHeader")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(32, 0, 32, 0)
        
        title_layout = QVBoxLayout()
        title = QLabel("Learning Report")
        title.setObjectName("reportTitle")
        
        subtitle = QLabel("你的个性化学习分析报告")
        subtitle.setObjectName("reportSubtitle")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        return header
    
    def _create_footer(self) -> QWidget:
        """创建底部"""
        footer = QFrame()
        footer.setObjectName("reportFooter")
        footer.setFixedHeight(70)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(32, 16, 32, 16)
        
        layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("reportButton")
        close_btn.setMinimumWidth(120)
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        return footer
    
    def _load_report(self):
        """加载报告内容"""
        report = self.learning_tracker.generate_learning_report()
        
        # 格式化为富文本
        formatted_report = report.replace('\n', '<br/>')
        formatted_report = formatted_report.replace('━━━━━━━━━━━━━━━━━━━━', '<hr/>')
        
        self.report_text.setHtml(f"""
        <div style='font-family: "SF Mono", "Menlo", monospace; 
                    font-size: 14px; 
                    line-height: 1.8; 
                    color: #2D3748;'>
        {formatted_report}
        </div>
        """)
    
    def _apply_theme(self):
        """应用主题"""
        theme_name = self.config.get("theme", "light")
        from .themes import get_theme
        theme = get_theme(theme_name)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_primary']};
            }}
            
            #reportHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2D3748, stop:0.5 #4A5568, stop:1 #2D3748);
                border-bottom: 2px solid {theme['border']};
            }}
            
            #reportTitle {{
                font-size: 26px;
                font-weight: 600;
                color: white;
                letter-spacing: -0.5px;
            }}
            
            #reportSubtitle {{
                font-size: 14px;
                color: #CBD5E0;
                margin-top: 4px;
            }}
            
            #reportFooter {{
                background: {theme['bg_secondary']};
                border-top: 1px solid {theme['border']};
            }}
            
            QTextEdit {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
                border: none;
                font-family: "SF Mono", "Menlo", monospace;
                font-size: 14px;
                line-height: 1.8;
            }}
            
            QPushButton#reportButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                padding: 0 24px;
            }}
            
            QPushButton#reportButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            QScrollBar:vertical {{
                background-color: {theme['bg_secondary']};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {theme['border']};
                border-radius: 5px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['text_tertiary']};
            }}
        """)
