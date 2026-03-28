"""
PDF 文件读取器
"""
from pathlib import Path

from core.file_reader import BaseFileReader, FileContent
from config import CHUNK_SIZE, CHUNK_OVERLAP


class PdfReader(BaseFileReader):
    """PDF 文件读取器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = [".pdf"]
    
    def read(self, file_path: Path) -> FileContent:
        """读取 PDF 文件"""
        file_path = Path(file_path)
        
        content = ""
        metadata = {}
        
        # 尝试使用 pdfplumber（效果更好）
        try:
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                pages_text = []
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_text.append(f"=== 第 {i} 页 ===\n{text}")
                
                content = "\n\n".join(pages_text)
                
                # 提取元数据
                if pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get("Title", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "subject": pdf.metadata.get("Subject", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                        "page_count": len(pdf.pages),
                    }
        
        except Exception as e1:
            # 回退到 PyPDF2
            try:
                from PyPDF2 import PdfReader as PyPdfReader
                
                reader = PyPdfReader(file_path)
                pages_text = []
                
                for i, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_text.append(f"=== 第 {i} 页 ===\n{text}")
                
                content = "\n\n".join(pages_text)
                
                # 提取元数据
                if reader.metadata:
                    metadata = {
                        "title": reader.metadata.get("/Title", ""),
                        "author": reader.metadata.get("/Author", ""),
                        "subject": reader.metadata.get("/Subject", ""),
                        "creator": reader.metadata.get("/Creator", ""),
                        "page_count": len(reader.pages),
                    }
            
            except Exception as e2:
                content = f"[Error reading PDF: pdfplumber: {e1}, PyPDF2: {e2}]"
        
        # 提取文件元数据
        file_metadata = self.extract_metadata_from_path(file_path)
        file_metadata.update(metadata)
        
        # 确定标题
        title = metadata.get("title", "") or file_path.stem
        
        # 分块
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="pdf",
            title=title,
            metadata=file_metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
