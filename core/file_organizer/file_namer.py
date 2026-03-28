"""
智能文件命名器
"""
import re
from pathlib import Path
from typing import Optional

from core.models import FileContent
from .tag_extractor import TagExtractor


class FileNamer:
    """智能文件命名器"""
    
    def __init__(self):
        """初始化文件命名器"""
        self.tag_extractor = TagExtractor()
    
    def generate_filename(self, file_content: FileContent) -> str:
        """
        为文件生成智能文件名
        
        Args:
            file_content: 文件内容对象
        
        Returns:
            生成的文件名
        """
        # 提取标签
        tags = self.tag_extractor.extract_tags(file_content, top_n=5)
        
        # 生成文件名
        if tags:
            # 使用前3个标签作为文件名
            filename = "_".join(tags[:3])
        else:
            # 如果没有标签，使用文件类型和时间戳
            import time
            filename = f"{file_content.file_type}_{int(time.time())}"
        
        # 清理文件名中的非法字符
        filename = self._clean_filename(filename)
        
        # 添加文件扩展名
        extension = Path(file_content.source).suffix
        if extension:
            filename += extension
        
        return filename
    
    def _clean_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符
        
        Args:
            filename: 原始文件名
        
        Returns:
            清理后的文件名
        """
        # 移除非法字符
        illegal_chars = '[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 移除多余的下划线
        filename = re.sub(r'_+', '_', filename)
        
        # 移除首尾下划线
        filename = filename.strip('_')
        
        # 限制文件名长度
        max_length = 255
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename
    
    def rename_file(self, file_path: str, file_content: FileContent) -> str:
        """
        重命名文件
        
        Args:
            file_path: 文件路径
            file_content: 文件内容对象
        
        Returns:
            新的文件路径
        """
        file_path = Path(file_path)
        new_filename = self.generate_filename(file_content)
        new_path = file_path.parent / new_filename
        
        # 如果文件已存在，添加数字后缀
        counter = 1
        while new_path.exists():
            base_name = new_path.stem
            extension = new_path.suffix
            new_path = file_path.parent / f"{base_name}_{counter}{extension}"
            counter += 1
        
        # 重命名文件
        try:
            file_path.rename(new_path)
            return str(new_path)
        except Exception as e:
            print(f"重命名文件失败: {e}")
            return str(file_path)