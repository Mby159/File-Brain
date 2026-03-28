"""
HTML 文件读取器
"""
from pathlib import Path
from typing import Optional

from core.file_reader import BaseFileReader, FileContent
from config import CHUNK_SIZE, CHUNK_OVERLAP


class HtmlReader(BaseFileReader):
    """HTML 文件读取器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = [".html", ".htm"]
    
    def read(self, file_path: Path) -> FileContent:
        """读取 HTML 文件"""
        file_path = Path(file_path)
        
        from bs4 import BeautifulSoup
        
        # 读取 HTML 内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # 解析 HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 提取标题
        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)
        elif soup.h1:
            title = soup.h1.get_text(strip=True)
        else:
            title = file_path.stem
        
        # 移除脚本和样式
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 提取正文
        # 优先提取 article 或 main 内容
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        
        if main_content:
            content = main_content.get_text(separator='\n', strip=True)
        else:
            # 获取 body 或整个文档的文本
            body = soup.find('body') or soup
            content = body.get_text(separator='\n', strip=True)
        
        # 清理文本
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        content = '\n\n'.join(lines)
        
        # 提取元数据
        metadata = self.extract_metadata_from_path(file_path)
        
        # 提取 meta 标签
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content_val = meta.get('content', '')
            if name and content_val:
                meta_tags[name] = content_val
        
        metadata['html_meta'] = meta_tags
        metadata['description'] = meta_tags.get('description', '')
        metadata['keywords'] = meta_tags.get('keywords', '')
        
        # 提取链接
        links = [a.get('href', '') for a in soup.find_all('a', href=True)]
        metadata['links'] = links[:20]  # 限制链接数量
        
        # 分块
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="html",
            title=title,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
    
    def read_from_url(self, url: str) -> FileContent:
        """从 URL 读取 HTML"""
        import requests
        from bs4 import BeautifulSoup
        
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # 提取标题
        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)
        elif soup.h1:
            title = soup.h1.get_text(strip=True)
        else:
            title = url
        
        # 移除脚本和样式
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 提取正文
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        
        if main_content:
            content = main_content.get_text(separator='\n', strip=True)
        else:
            body = soup.find('body') or soup
            content = body.get_text(separator='\n', strip=True)
        
        # 清理文本
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        content = '\n\n'.join(lines)
        
        # 元数据
        metadata = {
            "url": url,
            "title": title,
            "content_type": response.headers.get('Content-Type', ''),
        }
        
        # 分块
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=url,
            content=content,
            file_type="html",
            title=title,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
