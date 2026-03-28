"""
文本文件读取器
"""
from pathlib import Path
from typing import Dict, Any
import frontmatter

from core.file_reader import BaseFileReader, FileContent
from config import CHUNK_SIZE, CHUNK_OVERLAP


class TextReader(BaseFileReader):
    """纯文本文件读取器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = [".txt", ".rst"]
    
    def read(self, file_path: Path) -> FileContent:
        """读取文本文件"""
        file_path = Path(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取元数据
        metadata = self.extract_metadata_from_path(file_path)
        
        # 分块
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="text",
            title=file_path.stem,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )


class MarkdownReader(BaseFileReader):
    """Markdown 文件读取器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = [".md", ".markdown"]
    
    def read(self, file_path: Path) -> FileContent:
        """读取 Markdown 文件"""
        file_path = Path(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # 解析 frontmatter
        try:
            post = frontmatter.loads(text)
            content = post.content
            frontmatter_metadata = dict(post.metadata)
        except:
            content = text
            frontmatter_metadata = {}
        
        # 提取标题
        title = frontmatter_metadata.get('title', file_path.stem)
        
        # 提取元数据
        metadata = self.extract_metadata_from_path(file_path)
        metadata.update(frontmatter_metadata)
        
        # 提取标签
        tags = frontmatter_metadata.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        metadata['tags'] = tags
        
        # 分块
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="markdown",
            title=title,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
