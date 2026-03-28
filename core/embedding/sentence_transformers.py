"""
Sentence Transformers 嵌入模型
"""
from typing import List
import numpy as np

from .base import BaseEmbedding


class SentenceTransformersEmbedding(BaseEmbedding):
    """Sentence Transformers 嵌入模型"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__()
        self.model_name = model_name
        self.embedding_model = None
        self.dimension = 384  # all-MiniLM-L6-v2 的维度
        self._load_model()
    
    def _load_model(self):
        """加载嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.model_name)
            print(f"成功加载 Sentence Transformers 模型: {self.model_name}")
        except Exception as e:
            print(f"加载 Sentence Transformers 模型失败: {e}")
            self.embedding_model = None
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """将文本编码为向量"""
        if not self.embedding_model:
            # 如果模型加载失败，返回零向量
            return np.zeros((len(texts), self.dimension), dtype='float32')
        
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        # 归一化向量
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # 避免除零
        return embeddings / norms
    
    def encode_query(self, query: str) -> np.ndarray:
        """将查询编码为向量"""
        if not self.embedding_model:
            # 如果模型加载失败，返回零向量
            return np.zeros((1, self.dimension), dtype='float32')
        
        embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        # 归一化向量
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
