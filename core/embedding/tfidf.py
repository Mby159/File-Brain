"""
TF-IDF 嵌入模型
"""
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .base import BaseEmbedding


class TfidfEmbedding(BaseEmbedding):
    """TF-IDF 嵌入模型"""
    
    def __init__(self):
        super().__init__()
        self.vectorizer = None
        self.dimension = 5000  # 最大特征数
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """将文本编码为向量"""
        if not self.vectorizer:
            self.vectorizer = TfidfVectorizer(
                max_features=self.dimension,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.vectorizer.fit(texts)
        
        embeddings = self.vectorizer.transform(texts).toarray()
        # 归一化向量
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # 避免除零
        return embeddings / norms
    
    def encode_with_fit(self, texts: List[str]) -> np.ndarray:
        """强制重新训练向量器并编码文本"""
        self.vectorizer = TfidfVectorizer(
            max_features=self.dimension,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.vectorizer.fit(texts)
        
        embeddings = self.vectorizer.transform(texts).toarray()
        # 归一化向量
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # 避免除零
        return embeddings / norms
    
    def encode_query(self, query: str) -> np.ndarray:
        """将查询编码为向量"""
        if not self.vectorizer:
            # 如果还没有拟合，返回零向量
            return np.zeros((1, self.dimension), dtype='float32')
        
        embedding = self.vectorizer.transform([query]).toarray()
        # 归一化向量
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
