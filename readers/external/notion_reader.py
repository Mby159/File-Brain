"""
Notion 读取器 - 通过 Notion API 读取内容
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.file_reader import BaseFileReader, FileContent
from config import CHUNK_SIZE, CHUNK_OVERLAP, NOTION_API_KEY, NOTION_DATABASE_ID


class NotionReader(BaseFileReader):
    """Notion API 读取器"""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or NOTION_API_KEY
        self.client = None
        
        if self.api_key:
            try:
                from notion_client import Client
                self.client = Client(auth=self.api_key)
            except Exception as e:
                print(f"Notion 客户端初始化失败: {e}")
    
    def read(self, file_path: Path = None, page_id: str = None, database_id: str = None) -> FileContent:
        """
        读取 Notion 页面或数据库
        
        Args:
            file_path: 不使用，保持接口一致
            page_id: Notion 页面 ID
            database_id: Notion 数据库 ID
        """
        if not self.client:
            raise ValueError("Notion API Key 未配置")
        
        if page_id:
            return self._read_page(page_id)
        elif database_id:
            return self._read_database(database_id)
        elif NOTION_DATABASE_ID:
            return self._read_database(NOTION_DATABASE_ID)
        else:
            raise ValueError("需要提供 page_id 或 database_id")
    
    def _read_page(self, page_id: str) -> FileContent:
        """读取单个页面"""
        # 获取页面信息
        page = self.client.pages.retrieve(page_id=page_id)
        
        # 获取页面标题
        title = self._extract_title(page)
        
        # 获取页面内容
        blocks = self._get_all_blocks(page_id)
        content = self._blocks_to_text(blocks)
        
        # 元数据
        metadata = {
            "page_id": page_id,
            "object": page.get('object'),
            "created_time": page.get('created_time'),
            "last_edited_time": page.get('last_edited_time'),
            "url": page.get('url'),
        }
        
        # 分块
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=f"notion://{page_id}",
            content=content,
            file_type="notion",
            title=title,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
    
    def _read_database(self, database_id: str) -> List[FileContent]:
        """读取数据库中的所有页面"""
        results = []
        
        # 查询数据库
        pages = self.client.databases.query(database_id=database_id)
        
        for page in pages.get('results', []):
            page_id = page.get('id')
            try:
                content = self._read_page(page_id)
                results.append(content)
            except Exception as e:
                print(f"读取页面失败 {page_id}: {e}")
        
        return results
    
    def _get_all_blocks(self, block_id: str) -> List[Dict]:
        """获取所有块（包括嵌套）"""
        blocks = []
        cursor = None
        
        while True:
            response = self.client.blocks.children.list(
                block_id=block_id,
                start_cursor=cursor
            )
            
            for block in response.get('results', []):
                blocks.append(block)
                
                # 递归获取嵌套块
                if block.get('has_children'):
                    nested_blocks = self._get_all_blocks(block.get('id'))
                    block['children'] = nested_blocks
            
            if not response.get('has_more'):
                break
            cursor = response.get('next_cursor')
        
        return blocks
    
    def _blocks_to_text(self, blocks: List[Dict], depth: int = 0) -> str:
        """将块转换为文本"""
        texts = []
        indent = "  " * depth
        
        for block in blocks:
            block_type = block.get('type')
            block_data = block.get(block_type, {})
            
            text = self._extract_text_from_rich_text(block_data.get('rich_text', []))
            
            if block_type == 'paragraph':
                if text:
                    texts.append(f"{indent}{text}")
            
            elif block_type == 'heading_1':
                texts.append(f"{indent}# {text}")
            elif block_type == 'heading_2':
                texts.append(f"{indent}## {text}")
            elif block_type == 'heading_3':
                texts.append(f"{indent}### {text}")
            
            elif block_type == 'bulleted_list_item':
                texts.append(f"{indent}- {text}")
            elif block_type == 'numbered_list_item':
                texts.append(f"{indent}1. {text}")
            
            elif block_type == 'to_do':
                checked = "[x]" if block_data.get('checked') else "[ ]"
                texts.append(f"{indent}- {checked} {text}")
            
            elif block_type == 'code':
                language = block_data.get('language', '')
                texts.append(f"{indent}```{language}\n{text}\n{indent}```")
            
            elif block_type == 'quote':
                texts.append(f"{indent}> {text}")
            
            elif block_type == 'divider':
                texts.append(f"{indent}---")
            
            elif block_type == 'image':
                caption = self._extract_text_from_rich_text(block_data.get('caption', []))
                texts.append(f"{indent}[图片: {caption}]")
            
            # 处理子块
            if 'children' in block:
                child_text = self._blocks_to_text(block['children'], depth + 1)
                if child_text:
                    texts.append(child_text)
        
        return "\n".join(texts)
    
    def _extract_text_from_rich_text(self, rich_text: List[Dict]) -> str:
        """从 rich_text 中提取纯文本"""
        return "".join([t.get('plain_text', '') for t in rich_text])
    
    def _extract_title(self, page: Dict) -> str:
        """提取页面标题"""
        properties = page.get('properties', {})
        
        # 查找标题属性
        for prop_name, prop_data in properties.items():
            if prop_data.get('type') == 'title':
                title_items = prop_data.get('title', [])
                return "".join([t.get('plain_text', '') for t in title_items])
        
        return "Untitled"
    
    def list_databases(self) -> List[Dict]:
        """列出所有可访问的数据库"""
        if not self.client:
            return []
        
        try:
            response = self.client.search(
                filter={"value": "database", "property": "object"}
            )
            return response.get('results', [])
        except Exception as e:
            print(f"列出数据库失败: {e}")
            return []
    
    def list_pages(self, database_id: str = None) -> List[Dict]:
        """列出页面"""
        if not self.client:
            return []
        
        try:
            if database_id:
                response = self.client.databases.query(database_id=database_id)
            else:
                response = self.client.search(
                    filter={"value": "page", "property": "object"}
                )
            return response.get('results', [])
        except Exception as e:
            print(f"列出页面失败: {e}")
            return []
