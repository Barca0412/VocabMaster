"""
Spaced Repetition System based on Ebbinghaus Forgetting Curve
艾宾浩斯遗忘曲线复习系统
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
import json


class ReviewLevel(Enum):
    """复习等级 - 根据艾宾浩斯遗忘曲线"""
    NEW = 0           # 新单词
    LEARNING = 1      # 学习中（需要短期复习）
    YOUNG = 2         # 初步掌握（1天后复习）
    MATURE = 3        # 已掌握（3天后复习）
    MASTERED = 4      # 精通（7天后复习）
    PERFECT = 5       # 完美掌握（30天后复习）


class WordReview:
    """单词复习记录"""
    
    # 艾宾浩斯遗忘曲线间隔：5分钟、30分钟、12小时、1天、3天、7天、30天
    INTERVALS = {
        ReviewLevel.NEW: timedelta(minutes=5),       # 第一次：5分钟后
        ReviewLevel.LEARNING: timedelta(minutes=30), # 第二次：30分钟后
        ReviewLevel.YOUNG: timedelta(days=1),        # 第三次：1天后
        ReviewLevel.MATURE: timedelta(days=3),       # 第四次：3天后
        ReviewLevel.MASTERED: timedelta(days=7),     # 第五次：7天后
        ReviewLevel.PERFECT: timedelta(days=30),     # 第六次：30天后
    }
    
    def __init__(self, word: str):
        self.word = word
        self.level = ReviewLevel.NEW
        self.correct_count = 0        # 连续答对次数
        self.wrong_count = 0          # 答错总次数
        self.last_review = None       # 上次复习时间
        self.next_review = None       # 下次复习时间
        self.review_history = []      # 复习历史记录
        self.created_at = datetime.now()
    
    def mark_correct(self):
        """标记答对"""
        self.correct_count += 1
        self.last_review = datetime.now()
        
        # 连续答对3次，升级
        if self.correct_count >= 3:
            self._level_up()
            self.correct_count = 0
        
        # 计算下次复习时间
        self._schedule_next_review()
        
        # 记录历史
        self.review_history.append({
            'time': self.last_review.isoformat(),
            'result': 'correct',
            'level': self.level.name
        })
    
    def mark_wrong(self):
        """标记答错 - 重置到较低级别"""
        self.wrong_count += 1
        self.last_review = datetime.now()
        self.correct_count = 0
        
        # 答错则降级
        self._level_down()
        
        # 立即安排下次复习（5分钟后）
        self.next_review = self.last_review + timedelta(minutes=5)
        
        # 记录历史
        self.review_history.append({
            'time': self.last_review.isoformat(),
            'result': 'wrong',
            'level': self.level.name
        })
    
    def _level_up(self):
        """升级"""
        if self.level.value < ReviewLevel.PERFECT.value:
            self.level = ReviewLevel(self.level.value + 1)
    
    def _level_down(self):
        """降级 - 但不低于LEARNING"""
        if self.level.value > ReviewLevel.LEARNING.value:
            self.level = ReviewLevel(self.level.value - 1)
        else:
            self.level = ReviewLevel.LEARNING
    
    def _schedule_next_review(self):
        """根据当前级别安排下次复习时间"""
        interval = self.INTERVALS.get(self.level, timedelta(days=1))
        self.next_review = self.last_review + interval
    
    def needs_review(self) -> bool:
        """是否需要复习"""
        if self.next_review is None:
            return True  # 新单词总是需要复习
        return datetime.now() >= self.next_review
    
    def get_mastery_percentage(self) -> int:
        """获取掌握度百分比 (0-100)"""
        return int((self.level.value / ReviewLevel.PERFECT.value) * 100)
    
    def to_dict(self) -> Dict:
        """转为字典"""
        return {
            'word': self.word,
            'level': self.level.value,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'last_review': self.last_review.isoformat() if self.last_review else None,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'review_history': self.review_history,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WordReview':
        """从字典创建"""
        review = cls(data['word'])
        review.level = ReviewLevel(data['level'])
        review.correct_count = data['correct_count']
        review.wrong_count = data['wrong_count']
        review.last_review = datetime.fromisoformat(data['last_review']) if data['last_review'] else None
        review.next_review = datetime.fromisoformat(data['next_review']) if data['next_review'] else None
        review.review_history = data.get('review_history', [])
        review.created_at = datetime.fromisoformat(data['created_at'])
        return review


class SpacedRepetitionManager:
    """间隔重复学习管理器"""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reviews: Dict[str, WordReview] = {}
        self._load_reviews()
    
    def _load_reviews(self):
        """加载复习记录"""
        review_file = self.data_dir / "reviews.json"
        if review_file.exists():
            try:
                with open(review_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for word_data in data:
                        review = WordReview.from_dict(word_data)
                        self.reviews[review.word] = review
            except Exception as e:
                print(f"Failed to load reviews: {e}")
    
    def save_reviews(self):
        """保存复习记录"""
        review_file = self.data_dir / "reviews.json"
        try:
            data = [review.to_dict() for review in self.reviews.values()]
            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save reviews: {e}")
    
    def get_or_create_review(self, word: str) -> WordReview:
        """获取或创建单词复习记录"""
        if word not in self.reviews:
            self.reviews[word] = WordReview(word)
        return self.reviews[word]
    
    def get_due_words(self, limit: int = 20) -> List[WordReview]:
        """获取需要复习的单词（按优先级排序）"""
        due_reviews = [
            review for review in self.reviews.values()
            if review.needs_review()
        ]
        
        # 排序：先按级别（低级别优先），再按到期时间
        due_reviews.sort(key=lambda r: (
            r.level.value,
            r.next_review if r.next_review else datetime.min
        ))
        
        return due_reviews[:limit]
    
    def get_stats(self) -> Dict:
        """获取学习统计"""
        total = len(self.reviews)
        if total == 0:
            return {
                'total_words': 0,
                'new': 0,
                'learning': 0,
                'young': 0,
                'mature': 0,
                'mastered': 0,
                'perfect': 0,
                'due_count': 0,
                'average_mastery': 0
            }
        
        level_counts = {level: 0 for level in ReviewLevel}
        total_mastery = 0
        due_count = 0
        
        for review in self.reviews.values():
            level_counts[review.level] += 1
            total_mastery += review.get_mastery_percentage()
            if review.needs_review():
                due_count += 1
        
        return {
            'total_words': total,
            'new': level_counts[ReviewLevel.NEW],
            'learning': level_counts[ReviewLevel.LEARNING],
            'young': level_counts[ReviewLevel.YOUNG],
            'mature': level_counts[ReviewLevel.MATURE],
            'mastered': level_counts[ReviewLevel.MASTERED],
            'perfect': level_counts[ReviewLevel.PERFECT],
            'due_count': due_count,
            'average_mastery': int(total_mastery / total)
        }
    
    def import_words(self, words: List[str]):
        """批量导入新单词"""
        for word in words:
            if word not in self.reviews:
                self.reviews[word] = WordReview(word)
        self.save_reviews()
