"""
文件读取器模块
"""
from .text import TextReader, MarkdownReader
from .office import WordReader, PptReader, ExcelReader
from .others import PdfReader, HtmlReader, MindmapReader
from .external import NotionReader, ObsidianReader

__all__ = [
    "TextReader",
    "MarkdownReader", 
    "WordReader",
    "PptReader",
    "ExcelReader",
    "PdfReader",
    "HtmlReader",
    "MindmapReader",
    "NotionReader",
    "ObsidianReader",
]

# 文件类型到读取器的映射
READER_MAP = {
    "text": TextReader,
    "markdown": MarkdownReader,
    "word": WordReader,
    "powerpoint": PptReader,
    "excel": ExcelReader,
    "pdf": PdfReader,
    "html": HtmlReader,
    "mindmap": MindmapReader,
}


def get_reader_for_file(file_path):
    """根据文件路径获取对应的读取器"""
    from pathlib import Path
    from config import SUPPORTED_EXTENSIONS
    
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        return None
    
    file_type = SUPPORTED_EXTENSIONS[ext]
    reader_class = READER_MAP.get(file_type)
    
    if reader_class:
        return reader_class()
    return None
