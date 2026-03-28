"""
思维导图读取器
支持 XMind, FreeMind (.mm), OPML 格式
"""
from pathlib import Path
from typing import Dict, Any, List
import json
import xml.etree.ElementTree as ET

from core.file_reader import BaseFileReader, FileContent
from config import CHUNK_SIZE, CHUNK_OVERLAP


class MindmapReader(BaseFileReader):
    """思维导图读取器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = [".xmind", ".mm", ".opml"]
    
    def read(self, file_path: Path) -> FileContent:
        """读取思维导图文件"""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        if ext == ".xmind":
            return self._read_xmind(file_path)
        elif ext == ".mm":
            return self._read_freemind(file_path)
        elif ext == ".opml":
            return self._read_opml(file_path)
        else:
            raise ValueError(f"不支持的思维导图格式: {ext}")
    
    def _read_xmind(self, file_path: Path) -> FileContent:
        """读取 XMind 文件"""
        try:
            import zipfile
            
            # XMind 是 ZIP 格式
            with zipfile.ZipFile(file_path, 'r') as zf:
                # 读取 content.json
                if 'content.json' in zf.namelist():
                    with zf.open('content.json') as f:
                        data = json.load(f)
                elif 'content.xml' in zf.namelist():
                    # 旧版 XMind 使用 XML
                    with zf.open('content.xml') as f:
                        content = f.read()
                        return self._parse_xmind_xml(content, file_path)
                else:
                    raise ValueError("无法找到 XMind 内容文件")
            
            # 解析 JSON 内容
            content, structure = self._parse_xmind_json(data)
            
        except Exception as e:
            # 尝试使用 xmindparser
            try:
                from xmindparser import xmind_to_dict
                data = xmind_to_dict(file_path)
                content, structure = self._parse_xmind_dict(data)
            except Exception as e2:
                content = f"[Error reading XMind: {e}, {e2}]"
                structure = {}
        
        # 提取元数据
        metadata = self.extract_metadata_from_path(file_path)
        metadata['structure'] = structure
        
        # 分块
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="mindmap",
            title=structure.get('title', file_path.stem),
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
    
    def _parse_xmind_json(self, data: List[Dict]) -> tuple:
        """解析 XMind JSON 格式"""
        lines = []
        structure = {"title": "", "children": []}
        
        def traverse(node, depth=0):
            title = node.get('title', '')
            if title:
                lines.append("  " * depth + title)
            
            children = node.get('children', {}).get('attached', [])
            for child in children:
                traverse(child, depth + 1)
        
        if data and len(data) > 0:
            root_sheet = data[0]
            root_topic = root_sheet.get('rootTopic', {})
            structure['title'] = root_topic.get('title', '')
            traverse(root_topic)
        
        content = "\n".join(lines)
        return content, structure
    
    def _parse_xmind_dict(self, data: List[Dict]) -> tuple:
        """解析 xmindparser 输出"""
        lines = []
        structure = {"title": "", "children": []}
        
        def traverse(node, depth=0):
            title = node.get('title', '')
            if title:
                lines.append("  " * depth + "- " + title)
            
            children = node.get('topics', [])
            for child in children:
                traverse(child, depth + 1)
        
        if data and len(data) > 0:
            root = data[0]
            structure['title'] = root.get('title', '')
            traverse(root)
        
        content = "\n".join(lines)
        return content, structure
    
    def _parse_xmind_xml(self, content: bytes, file_path: Path) -> FileContent:
        """解析 XMind XML 格式（旧版）"""
        root = ET.fromstring(content)
        lines = []
        structure = {"title": "", "children": []}
        
        def traverse(element, depth=0):
            title = element.get('title', '')
            if title:
                lines.append("  " * depth + title)
            
            for child in element.findall('.//topic'):
                traverse(child, depth + 1)
        
        traverse(root)
        content = "\n".join(lines)
        
        metadata = self.extract_metadata_from_path(file_path)
        metadata['structure'] = structure
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="mindmap",
            title=file_path.stem,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
    
    def _read_freemind(self, file_path: Path) -> FileContent:
        """读取 FreeMind (.mm) 文件"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        lines = []
        structure = {"title": "", "children": []}
        
        def traverse(node, depth=0):
            text = node.get('TEXT', '')
            if text:
                lines.append("  " * depth + "- " + text)
            
            for child in node.findall('node'):
                traverse(child, depth + 1)
        
        # 从 map 节点的第一个 node 开始
        map_node = root.find('node')
        if map_node is not None:
            structure['title'] = map_node.get('TEXT', file_path.stem)
            traverse(map_node)
        
        content = "\n".join(lines)
        
        metadata = self.extract_metadata_from_path(file_path)
        metadata['structure'] = structure
        
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="mindmap",
            title=structure['title'] or file_path.stem,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
    
    def _read_opml(self, file_path: Path) -> FileContent:
        """读取 OPML 文件"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        lines = []
        structure = {"title": "", "children": []}
        
        # 获取标题
        head = root.find('head')
        if head is not None:
            title_elem = head.find('title')
            if title_elem is not None and title_elem.text:
                structure['title'] = title_elem.text
        
        def traverse(node, depth=0):
            text = node.get('text', '')
            if text:
                lines.append("  " * depth + "- " + text)
            
            for child in node.findall('outline'):
                traverse(child, depth + 1)
        
        # 从 body 开始
        body = root.find('body')
        if body is not None:
            for outline in body.findall('outline'):
                traverse(outline)
        
        content = "\n".join(lines)
        
        metadata = self.extract_metadata_from_path(file_path)
        metadata['structure'] = structure
        
        chunks = self.chunk_content(content, CHUNK_SIZE, CHUNK_OVERLAP)
        
        return FileContent(
            source=str(file_path.absolute()),
            content=content,
            file_type="mindmap",
            title=structure['title'] or file_path.stem,
            metadata=metadata,
            chunks=chunks,
            file_hash=self.calculate_hash(content)
        )
