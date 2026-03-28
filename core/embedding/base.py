"""
嵌入模型基类
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np


class BaseEmbedding(ABC):
    """嵌入模型基类"""
    
    def __init__(self):
        self.dimension = 0
    
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """将文本编码为向量"""
        pass
    
    @abstractmethod
    def encode_query(self, query: str) -> np.ndarray:
        """将查询编码为向量"""
        pass
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
