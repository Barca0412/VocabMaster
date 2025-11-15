"""
Quiz Window - 单词测试窗口
基于艾宾浩斯遗忘曲线的智能复习测试
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QWidget, QProgressBar, QFrame,
                             QRadioButton, QButtonGroup, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import random
from typing import List, Optional

from ..core.config import Config
from ..core.word_manager import WordManager, Word
from ..core.dictionary import DictionaryAPI
from ..core.spaced_repetition import SpacedRepetitionManager, WordReview
from ..core.learning_tracker import LearningTracker
from ..core.llm_generator import LLMOptionGenerator
import asyncio


class QuizWindow(QDialog):
    """单词测试窗口"""
    
    quiz_finished = pyqtSignal()
    
    def __init__(self, parent, config: Config, word_manager: WordManager, 
                 dictionary_api: DictionaryAPI, sr_manager: SpacedRepetitionManager,
                 learning_tracker: LearningTracker):
        super().__init__(parent)
        self.config = config
        self.word_manager = word_manager
        self.dictionary_api = dictionary_api
        self.sr_manager = sr_manager
        self.learning_tracker = learning_tracker
        
        # 初始化LLM生成器
        try:
            self.llm_generator = LLMOptionGenerator()
        except Exception as e:
            print(f"Failed to initialize LLM generator: {e}")
            self.llm_generator = None
        
        self.current_review: Optional[WordReview] = None
        self.current_word: Optional[Word] = None
        self.due_reviews: List[WordReview] = []
        self.quiz_count = 0
        self.correct_count = 0
        self.options = []
        self.correct_answer = ""
        
        self.setWindowTitle("Word Quiz - 单词测试")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        self._setup_ui()
        self._apply_theme()
        self._load_quiz()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header with progress
        header = self._create_header()
        layout.addWidget(header)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(12)
        self.progress_bar.setMaximum(20)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v / %m")
        layout.addWidget(self.progress_bar)
        
        # Question area
        self.question_label = QLabel()
        self.question_label.setObjectName("quizQuestion")
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setWordWrap(True)
        self.question_label.setMinimumHeight(100)
        layout.addWidget(self.question_label)
        
        # Hint area
        self.hint_label = QLabel()
        self.hint_label.setObjectName("quizHint")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)
        
        layout.addSpacing(16)
        
        # Options area
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        self.options_layout.setSpacing(12)
        layout.addWidget(self.options_widget)
        
        self.option_group = QButtonGroup()
        
        layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.submit_btn = QPushButton("提交答案")
        self.submit_btn.setObjectName("quizSubmitButton")
        self.submit_btn.setMinimumWidth(120)
        self.submit_btn.setMinimumHeight(44)
        self.submit_btn.clicked.connect(self._submit_answer)
        self.submit_btn.setEnabled(False)
        button_layout.addWidget(self.submit_btn)
        
        self.next_btn = QPushButton("下一题")
        self.next_btn.setObjectName("quizNextButton")
        self.next_btn.setMinimumWidth(120)
        self.next_btn.setMinimumHeight(44)
        self.next_btn.clicked.connect(self._next_question)
        self.next_btn.hide()
        button_layout.addWidget(self.next_btn)
        
        layout.addLayout(button_layout)
    
    def _create_header(self) -> QWidget:
        """创建头部"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("单词复习测试")
        title.setObjectName("quizTitle")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Score
        self.score_label = QLabel("0 / 0")
        self.score_label.setObjectName("quizScore")
        layout.addWidget(self.score_label)
        
        return header
    
    def _apply_theme(self):
        """应用主题"""
        theme_name = self.config.get("theme", "light")
        from .themes import get_theme
        theme = get_theme(theme_name)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_primary']};
            }}
            
            #quizTitle {{
                font-size: 20px;
                font-weight: 600;
                color: {theme['text_primary']};
            }}
            
            #quizScore {{
                font-size: 16px;
                font-weight: 500;
                color: {theme['accent']};
            }}
            
            QProgressBar {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                text-align: center;
                color: {theme['text_primary']};
                font-weight: 500;
                font-size: 13px;
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['accent']};
                border-radius: 5px;
            }}
            
            #quizQuestion {{
                font-size: 32px;
                font-weight: 600;
                color: {theme['text_primary']};
                padding: 20px;
                background-color: {theme['bg_secondary']};
                border-radius: 12px;
            }}
            
            #quizHint {{
                font-size: 14px;
                color: {theme['text_secondary']};
                font-style: italic;
            }}
            
            QRadioButton {{
                font-size: 15px;
                color: {theme['text_primary']};
                padding: 16px 20px;
                background-color: {theme['bg_secondary']};
                border: 2px solid {theme['border']};
                border-radius: 12px;
                min-height: 60px;
                line-height: 1.5;
            }}
            
            QRadioButton:hover {{
                background-color: {theme['button_hover']};
                border-color: {theme['text_secondary']};
                transform: translateY(-1px);
            }}
            
            QRadioButton:checked {{
                background-color: {theme['bg_primary']};
                border-color: {theme['accent']};
                border-width: 2px;
                font-weight: 500;
            }}
            
            QRadioButton::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid {theme['border']};
                border-radius: 11px;
                background-color: {theme['bg_primary']};
                margin-right: 14px;
            }}
            
            QRadioButton::indicator:hover {{
                border-color: {theme['accent']};
            }}
            
            QRadioButton::indicator:checked {{
                border-color: {theme['accent']};
                border-width: 6px;
                background-color: {theme['bg_primary']};
            }}
            
            QRadioButton[correct="true"] {{
                background-color: #D1FAE5;
                border-color: #059669;
                color: #065F46;
            }}
            
            QRadioButton[wrong="true"] {{
                background-color: #FEE2E2;
                border-color: #DC2626;
                color: #991B1B;
            }}
            
            QPushButton#quizSubmitButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['accent']}, stop:1 {theme['accent_hover']});
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }}
            
            QPushButton#quizSubmitButton:hover {{
                background: {theme['accent_hover']};
            }}
            
            QPushButton#quizSubmitButton:disabled {{
                background: {theme['border']};
                color: {theme['text_tertiary']};
            }}
            
            QPushButton#quizNextButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }}
            
            QPushButton#quizNextButton:hover {{
                background-color: {theme['button_hover']};
            }}
        """)
    
    def _load_quiz(self):
        """加载测试"""
        # 获取需要复习的单词
        self.due_reviews = self.sr_manager.get_due_words(limit=20)
        
        if not self.due_reviews:
            QMessageBox.information(
                self,
                "没有待复习单词",
                "太棒了！目前没有需要复习的单词。\n继续学习新单词，或稍后再来复习。"
            )
            self.reject()
            return
        
        self.quiz_count = 0
        self.correct_count = 0
        self.progress_bar.setMaximum(len(self.due_reviews))
        self._load_next_word()
    
    def _load_next_word(self):
        """加载下一个单词"""
        if self.quiz_count >= len(self.due_reviews):
            self._show_results()
            return
        
        self.current_review = self.due_reviews[self.quiz_count]
        
        # 从word_manager中查找对应的Word对象
        current_word_text = self.current_review.word
        
        # 尝试从当前wordlist中找到这个单词
        if self.word_manager.current_wordlist:
            for word in self.word_manager.current_wordlist.words:
                if word.word == current_word_text:
                    self.current_word = word
                    break
        
        # 如果没找到，创建一个临时Word对象
        if self.current_word is None:
            self.current_word = Word(current_word_text)
        
        # 异步获取定义
        asyncio.ensure_future(self._fetch_and_show_question())
    
    async def _fetch_and_show_question(self):
        """获取定义并显示问题"""
        try:
            # 如果还没有定义，获取之
            if not self.current_word.definitions:
                definitions = await self.dictionary_api.lookup(self.current_word.word)
                self.current_word.definitions = definitions
            
            self._show_question()
        except Exception as e:
            print(f"Failed to fetch definitions: {e}")
            self._show_question()
    
    def _show_question(self):
        """显示问题"""
        # 清空之前的选项
        for i in reversed(range(self.options_layout.count())): 
            self.options_layout.itemAt(i).widget().setParent(None)
        
        # 显示单词
        self.question_label.setText(self.current_word.word.upper())
        
        # 显示提示（音标）
        hint = ""
        if self.current_word.definitions:
            mw = self.current_word.definitions.get("merriam_webster", {})
            yd = self.current_word.definitions.get("youdao", {})
            phonetic = mw.get("phonetic") or yd.get("phonetic", "")
            if phonetic:
                hint = f"/{phonetic}/"
        self.hint_label.setText(hint)
        
        # 生成选项
        self._generate_options()
        
        # 更新进度
        self.quiz_count += 1
        self.progress_bar.setValue(self.quiz_count - 1)  # 显示已完成的题目数
        if self.quiz_count > 1:
            self.score_label.setText(f"{self.correct_count} / {self.quiz_count - 1}")
        else:
            self.score_label.setText("0 / 0")
        
        # 重置按钮状态
        self.submit_btn.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.hide()
    
    def _generate_options(self):
        """生成4个选项（1个正确答案 + 3个干扰项）"""
        # 获取正确答案
        correct_translations = []
        if self.current_word.definitions:
            yd = self.current_word.definitions.get("youdao", {})
            correct_translations = yd.get("translations", [])
            
            if not correct_translations:
                mw = self.current_word.definitions.get("merriam_webster", {})
                correct_translations = mw.get("definitions", [])
        
        if correct_translations:
            self.correct_answer = correct_translations[0]
        else:
            self.correct_answer = "（释义获取中...）"
        
        # 使用LLM生成干扰项
        if self.llm_generator:
            try:
                distractors = self.llm_generator.generate_distractors(
                    self.current_word.word,
                    self.correct_answer,
                    self.current_word.definitions
                )
            except Exception as e:
                print(f"LLM generation error: {e}")
                distractors = self._fallback_distractors()
        else:
            distractors = self._fallback_distractors()
        
        # 组合所有选项并打乱
        self.options = [self.correct_answer] + distractors[:3]
        random.shuffle(self.options)
        
        # 创建单选按钮
        for i, option in enumerate(self.options):
            radio = QRadioButton(option)
            radio.toggled.connect(lambda checked: self.submit_btn.setEnabled(True))
            self.option_group.addButton(radio, i)
            self.options_layout.addWidget(radio)
    
    def _fallback_distractors(self) -> List[str]:
        """降级方案：从其他单词中随机选择干扰项"""
        distractors = []
        all_words = list(self.sr_manager.reviews.keys())
        random.shuffle(all_words)
        
        for word_text in all_words:
            if word_text == self.current_word.word:
                continue
            if len(distractors) >= 3:
                break
            
            # 简单的干扰项
            distractor = f"{word_text}的相关含义"
            distractors.append(distractor)
        
        # 如果干扰项不够，添加通用干扰项
        while len(distractors) < 3:
            distractors.append(f"选项 {len(distractors) + 1}")
        
        return distractors
    
    def _submit_answer(self):
        """提交答案"""
        selected_id = self.option_group.checkedId()
        if selected_id == -1:
            return
        
        selected_option = self.options[selected_id]
        is_correct = (selected_option == self.correct_answer)
        
        # 更新复习记录
        if is_correct:
            self.current_review.mark_correct()
            self.correct_count += 1
            # 记录到学习追踪器
            self.learning_tracker.track_quiz_correct(self.current_word.word)
        else:
            self.current_review.mark_wrong()
            # 记录错题到学习追踪器
            self.learning_tracker.track_quiz_wrong(
                self.current_word.word,
                selected_option,
                self.correct_answer
            )
        
        self.sr_manager.save_reviews()
        
        # 显示答案反馈
        for i in range(self.options_layout.count()):
            radio = self.options_layout.itemAt(i).widget()
            radio.setEnabled(False)
            
            option_text = self.options[i]
            if option_text == self.correct_answer:
                radio.setProperty("correct", "true")
            elif i == selected_id and not is_correct:
                radio.setProperty("wrong", "true")
            
            radio.style().unpolish(radio)
            radio.style().polish(radio)
        
        # 更新得分
        self.score_label.setText(f"{self.correct_count} / {self.quiz_count}")
        
        # 切换按钮
        self.submit_btn.hide()
        self.next_btn.show()
    
    def _next_question(self):
        """下一题"""
        self._load_next_word()
    
    def _show_results(self):
        """显示测试结果"""
        accuracy = int((self.correct_count / self.quiz_count) * 100) if self.quiz_count > 0 else 0
        
        result_text = f"""
        <div style='text-align: center; line-height: 1.8;'>
        <h2>测试完成！</h2>
        <p style='font-size: 18px; margin: 20px 0;'>
        答对题数: <b>{self.correct_count}</b> / {self.quiz_count}<br/>
        正确率: <b>{accuracy}%</b>
        </p>
        <p style='font-size: 14px; color: #666;'>
        继续保持，每天坚持复习！
        </p>
        </div>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("测试结果")
        msg.setText(result_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        self.quiz_finished.emit()
        self.accept()
