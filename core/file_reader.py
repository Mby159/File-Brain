"""
文件读取基类
"""
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import hashlib

from .models import FileContent


class BaseFileReader(ABC):
    """文件读取器基类"""
    
    def __init__(self):
        self.supported_extensions = []
    
    @abstractmethod
    def read(self, file_path: Path) -> FileContent:
        """读取文件并返回内容"""
        pass
    
    def can_read(self, file_path: Path) -> bool:
        """检查是否支持该文件类型"""
        return file_path.suffix.lower() in self.supported_extensions
    
    def calculate_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def chunk_content(self, content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """将内容分块"""
        chunks = []
        start = 0
        content_len = len(content)
        
        while start < content_len:
            end = min(start + chunk_size, content_len)
            # 尝试在句子或段落边界处分割
            if end < content_len:
                # 查找最近的句子结束符
                for sep in ['.\n', '。\n', '!\n', '?\n', '\n\n', '. ', '。', '!', '?', ' ']:
                    pos = content.rfind(sep, start, end)
                    if pos != -1:
                        end = pos + len(sep)
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < content_len else content_len
        
        return chunks
    
    def extract_metadata_from_path(self, file_path: Path) -> Dict[str, Any]:
        """从文件路径提取元数据"""
        stat = file_path.stat()
        return {
            "file_name": file_path.name,
            "file_path": str(file_path.absolute()),
            "file_size": stat.st_size,
            "file_extension": file_path.suffix.lower(),
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
        }
