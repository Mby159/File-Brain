"""
标签提取器
"""
import re
from collections import Counter
from typing import List, Set

from core.models import FileContent


class TagExtractor:
    """标签提取器"""
    
    def __init__(self):
        """初始化标签提取器"""
        # 多语言停用词列表
        self.stop_words = {
            'zh': set([
                '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'
            ]),
            'en': set([
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
            ]),
            'ja': set([
                'の', 'に', 'は', 'を', 'た', 'が', 'て', 'と', 'し', 'した', 'な', 'い', 'する', 'して', 'ある', 'いる', 'も', 'この', 'その', 'あの'
            ])
        }
    
    def extract_tags(self, file_content: FileContent, top_n: int = 10) -> List[str]:
        """
        从文件内容中提取标签
        
        Args:
            file_content: 文件内容对象
            top_n: 返回的标签数量
        
        Returns:
            标签列表
        """
        content = file_content.content
        if not content:
            return []
        
        # 检测语言
        language = self._detect_language(content)
        
        # 清理内容
        content = self._clean_content(content)
        
        # 分词
        words = self._tokenize(content, language)
        
        # 过滤停用词
        stop_words = self.stop_words.get(language, set())
        words = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 统计词频
        word_counts = Counter(words)
        
        # 提取 top_n 个词作为标签
        tags = [word for word, _ in word_counts.most_common(top_n)]
        
        return tags
    
    def _clean_content(self, content: str) -> str:
        """
        清理内容
        
        Args:
            content: 原始内容
        
        Returns:
            清理后的内容
        """
        # 移除标点符号和特殊字符
        content = re.sub(r'[\s\W_]+', ' ', content)
        # 转为小写
        content = content.lower()
        return content
    
    def _detect_language(self, content: str) -> str:
        """
        检测文本语言
        
        Args:
            content: 文本内容
        
        Returns:
            语言代码 (zh, en, ja, etc.)
        """
        # 简单的语言检测逻辑
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', content))
        # 统计日文字符
        japanese_chars = len(re.findall(r'[\u3040-\u30ff]', content))
        
        if chinese_chars > len(content) * 0.3:
            return 'zh'
        elif japanese_chars > len(content) * 0.3:
            return 'ja'
        else:
            return 'en'
    
    def _tokenize(self, content: str, language: str) -> List[str]:
        """
        分词
        
        Args:
            content: 内容
            language: 语言代码
        
        Returns:
            词语列表
        """
        # 根据语言选择分词方法
        if language == 'zh':
            # 尝试使用 jieba 分词
            try:
                import jieba
                return list(jieba.cut(content))
            except ImportError:
                # 如果没有安装 jieba，使用简单的空格分词
                return content.split()
        else:
            # 对于其他语言，使用空格分词
            return content.split()
    
    def extract_tags_from_text(self, text: str, top_n: int = 10) -> List[str]:
        """
        从文本中提取标签
        
        Args:
            text: 文本内容
            top_n: 返回的标签数量
        
        Returns:
            标签列表
        """
        # 创建临时 FileContent 对象
        from core.models import FileContent
        temp_content = FileContent(
            source="temp",
            content=text,
            file_type="text"
        )
        return self.extract_tags(temp_content, top_n=top_n)
