"""
文件内容数据结构
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class FileContent:
    """文件内容数据结构"""
    source: str                          # 文件路径或来源
    content: str                         # 文本内容
    file_type: str                       # 文件类型
    title: Optional[str] = None          # 标题
    metadata: Dict[str, Any] = None      # 元数据
    chunks: List[str] = None             # 分块内容
    created_at: datetime = None          # 创建时间
    modified_at: datetime = None         # 修改时间
    file_hash: str = None                # 文件哈希（用于去重）
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.chunks is None:
            self.chunks = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.modified_at is None:
            self.modified_at = datetime.now()
