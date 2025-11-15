"""
LLM-based Quiz Option Generator
使用LLM生成高质量的测试选项
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMOptionGenerator:
    """使用LLM生成测试选项"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.model_name = os.getenv("OPENAI_MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
        
        if not self.api_key or not self.base_url:
            raise ValueError("OPENAI_API_KEY and OPENAI_BASE_URL must be set in .env file")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_personalized_example(self, word: str, definition: str, 
                                     learning_goal: str = "") -> str:
        """
        生成个性化例句
        
        Args:
            word: 英文单词
            definition: 单词释义
            learning_goal: 用户的学习目标
        
        Returns:
            str: 个性化例句
        """
        if not learning_goal:
            learning_goal = "日常英语学习"
        
        prompt = f"""请为以下英语单词生成1个例句。

单词：{word}
释义：{definition}
用户学习目标：{learning_goal}

要求：
1. 例句要贴合用户的学习目标场景
2. 例句难度适中，便于理解
3. 例句要自然、地道
4. 不要超过20个单词

请直接输出例句，不要额外解释："""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的英语教学助手，擅长生成贴合实际场景的例句。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            example = response.choices[0].message.content.strip()
            # 移除可能的引号
            example = example.strip('"\'')
            return example
            
        except Exception as e:
            print(f"LLM example generation failed: {e}")
            return f"I need to learn this {word}."
    
    def generate_distractors(self, word: str, correct_answer: str, 
                            definitions: Optional[Dict] = None) -> List[str]:
        """
        生成3个干扰项
        
        Args:
            word: 英文单词
            correct_answer: 正确的中文释义
            definitions: 单词的完整定义（可选，用于提供更多上下文）
        
        Returns:
            List[str]: 3个干扰项
        """
        # 构建prompt
        prompt = self._build_prompt(word, correct_answer, definitions)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的英语教学助手，擅长生成高质量的单词测试题干扰项。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            # 解析返回结果
            content = response.choices[0].message.content.strip()
            distractors = self._parse_response(content)
            
            # 确保有3个干扰项
            if len(distractors) < 3:
                distractors.extend(self._fallback_distractors(word, correct_answer))
                distractors = distractors[:3]
            
            return distractors
            
        except Exception as e:
            print(f"LLM generation failed: {e}")
            # 降级到简单生成
            return self._fallback_distractors(word, correct_answer)
    
    def _build_prompt(self, word: str, correct_answer: str, 
                     definitions: Optional[Dict] = None) -> str:
        """构建LLM prompt"""
        
        context = ""
        if definitions:
            # 添加英文释义作为上下文
            mw_defs = definitions.get("merriam_webster", {}).get("definitions", [])
            if mw_defs:
                context = f"\n英文释义：{mw_defs[0]}"
        
        prompt = f"""请为以下英语单词的测试题生成3个干扰项（错误选项）。

单词：{word}
正确答案：{correct_answer}{context}

要求：
1. 生成3个看似合理但错误的中文释义
2. 干扰项应该与正确答案有一定相似性（如相关领域、词性相同等）
3. 干扰项不能是正确答案的同义词
4. 每个干扰项应该简洁（不超过15个字）
5. 每行一个选项，不要编号

请直接输出3个干扰项，每行一个："""
        
        return prompt
    
    def _parse_response(self, content: str) -> List[str]:
        """解析LLM返回的内容"""
        lines = content.strip().split('\n')
        distractors = []
        
        for line in lines:
            line = line.strip()
            # 移除可能的编号（1. 2. 3. 或 1) 2) 3)）
            line = line.lstrip('123456789.)、 ')
            
            if line and len(line) <= 50:  # 过滤太长的行
                distractors.append(line)
        
        return distractors[:3]
    
    def _fallback_distractors(self, word: str, correct_answer: str) -> List[str]:
        """降级方案：生成简单的干扰项"""
        # 通用干扰词库
        generic_words = [
            "动物", "植物", "工具", "食物", "颜色", "数字",
            "方向", "天气", "时间", "地点", "人物", "行为",
            "状态", "情感", "特征", "材料", "形状", "大小",
            "声音", "味道", "触感", "视觉", "嗅觉", "听觉"
        ]
        
        # 常见词性变化
        word_variations = [
            f"{word}的名词形式",
            f"{word}的动词形式",
            f"{word}的形容词形式"
        ]
        
        # 组合返回
        fallback = generic_words + word_variations
        
        # 过滤掉可能包含正确答案的选项
        result = []
        for item in fallback:
            if item != correct_answer and correct_answer not in item:
                result.append(item)
                if len(result) >= 3:
                    break
        
        # 如果还不够，添加通用选项
        while len(result) < 3:
            result.append(f"选项 {len(result) + 1}")
        
        return result[:3]
