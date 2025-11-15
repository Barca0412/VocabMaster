"""
Learning Tracker - 学习记录追踪系统
追踪用户学习过的单词、测试记录、错题等
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict


class WordRecord:
    """单词学习记录"""
    
    def __init__(self, word: str):
        self.word = word
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.view_count = 0  # 浏览次数
        self.quiz_attempts = 0  # 测试次数
        self.correct_count = 0  # 答对次数
        self.wrong_count = 0  # 答错次数
        self.wrong_history = []  # 错题历史记录
        
    def mark_viewed(self):
        """标记为已浏览"""
        self.view_count += 1
        self.last_seen = datetime.now()
    
    def mark_quiz_correct(self):
        """标记测试答对"""
        self.quiz_attempts += 1
        self.correct_count += 1
        self.last_seen = datetime.now()
    
    def mark_quiz_wrong(self, selected_option: str, correct_option: str):
        """标记测试答错"""
        self.quiz_attempts += 1
        self.wrong_count += 1
        self.last_seen = datetime.now()
        
        # 记录错误详情
        self.wrong_history.append({
            'time': datetime.now().isoformat(),
            'selected': selected_option,
            'correct': correct_option
        })
    
    def get_accuracy(self) -> float:
        """获取测试正确率"""
        if self.quiz_attempts == 0:
            return 0.0
        return (self.correct_count / self.quiz_attempts) * 100
    
    def is_weak(self) -> bool:
        """判断是否为薄弱单词"""
        # 条件：测试超过3次且正确率低于60%
        return self.quiz_attempts >= 3 and self.get_accuracy() < 60
    
    def to_dict(self) -> Dict:
        return {
            'word': self.word,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'view_count': self.view_count,
            'quiz_attempts': self.quiz_attempts,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'wrong_history': self.wrong_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WordRecord':
        record = cls(data['word'])
        record.first_seen = datetime.fromisoformat(data['first_seen'])
        record.last_seen = datetime.fromisoformat(data['last_seen'])
        record.view_count = data['view_count']
        record.quiz_attempts = data['quiz_attempts']
        record.correct_count = data['correct_count']
        record.wrong_count = data['wrong_count']
        record.wrong_history = data.get('wrong_history', [])
        return record


class LearningTracker:
    """学习追踪管理器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records: Dict[str, WordRecord] = {}
        self._load_records()
    
    def _load_records(self):
        """加载学习记录"""
        record_file = self.data_dir / "learning_records.json"
        if record_file.exists():
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for word_data in data:
                        record = WordRecord.from_dict(word_data)
                        self.records[record.word] = record
            except Exception as e:
                print(f"Failed to load learning records: {e}")
    
    def save_records(self):
        """保存学习记录"""
        record_file = self.data_dir / "learning_records.json"
        try:
            data = [record.to_dict() for record in self.records.values()]
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save learning records: {e}")
    
    def track_word_view(self, word: str):
        """记录单词浏览"""
        if word not in self.records:
            self.records[word] = WordRecord(word)
        self.records[word].mark_viewed()
        self.save_records()
    
    def track_quiz_correct(self, word: str):
        """记录测试答对"""
        if word not in self.records:
            self.records[word] = WordRecord(word)
        self.records[word].mark_quiz_correct()
        self.save_records()
    
    def track_quiz_wrong(self, word: str, selected_option: str, correct_option: str):
        """记录测试答错"""
        if word not in self.records:
            self.records[word] = WordRecord(word)
        self.records[word].mark_quiz_wrong(selected_option, correct_option)
        self.save_records()
    
    def get_weak_words(self, limit: int = 20) -> List[WordRecord]:
        """获取薄弱单词列表"""
        weak_words = [record for record in self.records.values() if record.is_weak()]
        # 按错误率排序
        weak_words.sort(key=lambda r: (r.wrong_count / r.quiz_attempts if r.quiz_attempts > 0 else 0), 
                       reverse=True)
        return weak_words[:limit]
    
    def get_recent_mistakes(self, limit: int = 10) -> List[WordRecord]:
        """获取最近的错题"""
        mistakes = [record for record in self.records.values() if record.wrong_count > 0]
        mistakes.sort(key=lambda r: r.last_seen, reverse=True)
        return mistakes[:limit]
    
    def get_statistics(self) -> Dict:
        """获取学习统计"""
        total_words = len(self.records)
        if total_words == 0:
            return {
                'total_words': 0,
                'viewed_words': 0,
                'quizzed_words': 0,
                'weak_words': 0,
                'total_quiz_attempts': 0,
                'total_correct': 0,
                'overall_accuracy': 0,
                'most_viewed': [],
                'most_mistakes': []
            }
        
        viewed_words = sum(1 for r in self.records.values() if r.view_count > 0)
        quizzed_words = sum(1 for r in self.records.values() if r.quiz_attempts > 0)
        weak_words = sum(1 for r in self.records.values() if r.is_weak())
        total_quiz_attempts = sum(r.quiz_attempts for r in self.records.values())
        total_correct = sum(r.correct_count for r in self.records.values())
        overall_accuracy = (total_correct / total_quiz_attempts * 100) if total_quiz_attempts > 0 else 0
        
        # 最常浏览的单词
        most_viewed = sorted(self.records.values(), key=lambda r: r.view_count, reverse=True)[:5]
        most_viewed_list = [(r.word, r.view_count) for r in most_viewed if r.view_count > 0]
        
        # 错误最多的单词
        most_mistakes = sorted(self.records.values(), key=lambda r: r.wrong_count, reverse=True)[:5]
        most_mistakes_list = [(r.word, r.wrong_count, r.get_accuracy()) for r in most_mistakes if r.wrong_count > 0]
        
        return {
            'total_words': total_words,
            'viewed_words': viewed_words,
            'quizzed_words': quizzed_words,
            'weak_words': weak_words,
            'total_quiz_attempts': total_quiz_attempts,
            'total_correct': total_correct,
            'overall_accuracy': overall_accuracy,
            'most_viewed': most_viewed_list,
            'most_mistakes': most_mistakes_list
        }
    
    def generate_learning_report(self) -> str:
        """生成个性化学习报告"""
        stats = self.get_statistics()
        weak_words = self.get_weak_words(10)
        recent_mistakes = self.get_recent_mistakes(5)
        
        report = f"""
📊 学习数据总览
━━━━━━━━━━━━━━━━━━━━
• 累计学习单词：{stats['total_words']} 个
• 已浏览单词：{stats['viewed_words']} 个
• 已测试单词：{stats['quizzed_words']} 个
• 测试总次数：{stats['total_quiz_attempts']} 次
• 总体正确率：{stats['overall_accuracy']:.1f}%

"""
        
        if weak_words:
            report += """
⚠️ 需要重点关注的单词
━━━━━━━━━━━━━━━━━━━━
以下单词测试次数较多但正确率较低，建议加强记忆：

"""
            for i, record in enumerate(weak_words[:5], 1):
                report += f"{i}. {record.word}\n"
                report += f"   测试 {record.quiz_attempts} 次，正确率 {record.get_accuracy():.0f}%\n"
                if record.wrong_history:
                    last_error = record.wrong_history[-1]
                    report += f"   最近错误：选择了「{last_error['selected']}」，正确答案是「{last_error['correct']}」\n"
                report += "\n"
        
        if recent_mistakes:
            report += """
🔍 最近的错题
━━━━━━━━━━━━━━━━━━━━
"""
            for record in recent_mistakes[:5]:
                if record.wrong_history:
                    last_error = record.wrong_history[-1]
                    report += f"• {record.word}\n"
                    report += f"  选择了「{last_error['selected']}」，正确答案是「{last_error['correct']}」\n"
        
        if stats['most_viewed']:
            report += """

📖 学习最多的单词
━━━━━━━━━━━━━━━━━━━━
"""
            for word, count in stats['most_viewed'][:3]:
                report += f"• {word} - 浏览 {count} 次\n"
        
        report += """

💡 学习建议
━━━━━━━━━━━━━━━━━━━━
"""
        if stats['overall_accuracy'] >= 80:
            report += "• 你的正确率很高，继续保持！可以尝试学习更难的单词\n"
        elif stats['overall_accuracy'] >= 60:
            report += "• 正确率不错，但还有提升空间。建议重点复习薄弱单词\n"
        else:
            report += "• 建议降低学习速度，重点巩固基础单词\n"
        
        if weak_words:
            report += f"• 当前有 {len(weak_words)} 个薄弱单词需要重点关注\n"
            report += "• 建议今天优先测试这些薄弱单词\n"
        
        return report
