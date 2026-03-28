"""
Markdown 文件读取器
"""
from pathlib import Path
import re

from core.file_reader import BaseFileReader, FileContent


class MarkdownReader(BaseFileReader):
    """Markdown 文件读取器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.md', '.markdown']
    
    def read(self, file_path: Path) -> FileContent:
        """读取 Markdown 文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title = self._extract_title(content, file_path.name)
            
            # 提取元数据
            metadata = self.extract_metadata_from_path(file_path)
            
            # 分块内容
            chunks = self.chunk_content(content)
            
            # 计算哈希
            file_hash = self.calculate_hash(content)
            
            return FileContent(
                source=str(file_path.absolute()),
                content=content,
                file_type='markdown',
                title=title,
                metadata=metadata,
                chunks=chunks,
                file_hash=file_hash
            )
        except Exception as e:
            print(f"读取 Markdown 文件失败 {file_path}: {e}")
            return FileContent(
                source=str(file_path.absolute()),
                content='',
                file_type='markdown',
                title=file_path.name
            )
    
    def _extract_title(self, content: str, filename: str) -> str:
        """从 Markdown 内容中提取标题"""
        # 查找一级标题
        match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 如果没有一级标题，使用文件名
        return filename.rsplit('.', 1)[0]
