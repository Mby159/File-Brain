"""
文本文件读取器
"""
from pathlib import Path

from core.file_reader import BaseFileReader, FileContent


class TextReader(BaseFileReader):
    """文本文件读取器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.txt', '.rst']
    
    def read(self, file_path: Path) -> FileContent:
        """读取文本文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取元数据
            metadata = self.extract_metadata_from_path(file_path)
            
            # 分块内容
            chunks = self.chunk_content(content)
            
            # 计算哈希
            file_hash = self.calculate_hash(content)
            
            return FileContent(
                source=str(file_path.absolute()),
                content=content,
                file_type='text',
                title=file_path.name,
                metadata=metadata,
                chunks=chunks,
                file_hash=file_hash
            )
        except Exception as e:
            print(f"读取文本文件失败 {file_path}: {e}")
            return FileContent(
                source=str(file_path.absolute()),
                content='',
                file_type='text',
                title=file_path.name
            )
