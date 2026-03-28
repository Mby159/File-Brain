"""
Obsidian 读取器 - 读取 Obsidian 知识库
"""
from pathlib import Path
from typing import List, Dict, Any, Generator
import json

from core.file_reader import BaseFileReader, FileContent
from readers.text_reader import MarkdownReader
from config import CHUNK_SIZE, CHUNK_OVERLAP, OBSIDIAN_VAULT_PATH


class ObsidianReader:
    """Obsidian 知识库读取器"""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else None
        if not self.vault_path and OBSIDIAN_VAULT_PATH:
            self.vault_path = Path(OBSIDIAN_VAULT_PATH)
        
        self.markdown_reader = MarkdownReader()
    
    def read_vault(self, include_attachments: bool = False) -> Generator[FileContent, None, None]:
        """
        读取整个 Obsidian 知识库
        
        Args:
            include_attachments: 是否包含附件（图片、PDF等）
        """
        if not self.vault_path or not self.vault_path.exists():
            raise ValueError(f"Obsidian 知识库路径无效: {self.vault_path}")
        
        # 遍历所有 Markdown 文件
        for md_file in self.vault_path.rglob("*.md"):
            # 跳过隐藏文件夹（如 .obsidian）
            if any(part.startswith('.') for part in md_file.relative_to(self.vault_path).parts):
                continue
            
            try:
                content = self.markdown_reader.read(md_file)
                # 添加 Obsidian 特定元数据
                content.metadata['vault_path'] = str(self.vault_path)
                content.metadata['relative_path'] = str(md_file.relative_to(self.vault_path))
                content.file_type = "obsidian"
                content.source = f"obsidian://{md_file.relative_to(self.vault_path)}"
                yield content
            except Exception as e:
                print(f"读取文件失败 {md_file}: {e}")
    
    def read_file(self, relative_path: str) -> FileContent:
        """读取单个文件"""
        if not self.vault_path:
            raise ValueError("Obsidian 知识库路径未配置")
        
        file_path = self.vault_path / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        content = self.markdown_reader.read(file_path)
        content.metadata['vault_path'] = str(self.vault_path)
        content.metadata['relative_path'] = relative_path
        content.file_type = "obsidian"
        content.source = f"obsidian://{relative_path}"
        
        return content
    
    def get_all_notes(self) -> List[Dict[str, Any]]:
        """获取所有笔记的列表"""
        if not self.vault_path or not self.vault_path.exists():
            return []
        
        notes = []
        for md_file in self.vault_path.rglob("*.md"):
            if any(part.startswith('.') for part in md_file.relative_to(self.vault_path).parts):
                continue
            
            relative_path = str(md_file.relative_to(self.vault_path))
            stat = md_file.stat()
            
            notes.append({
                "path": relative_path,
                "name": md_file.stem,
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })
        
        return notes
    
    def get_graph_data(self) -> Dict[str, Any]:
        """
        获取知识图谱数据（节点和链接）
        """
        nodes = []
        links = []
        node_map = {}
        
        for note in self.get_all_notes():
            note_path = note['path']
            node_id = len(nodes)
            node_map[note_path] = node_id
            nodes.append({
                "id": node_id,
                "path": note_path,
                "name": note['name'],
            })
        
        # 查找链接
        for md_file in self.vault_path.rglob("*.md"):
            if any(part.startswith('.') for part in md_file.relative_to(self.vault_path).parts):
                continue
            
            relative_path = str(md_file.relative_to(self.vault_path))
            source_id = node_map.get(relative_path)
            
            if source_id is None:
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 查找 Wiki 链接 [[...]]
                import re
                wiki_links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', content)
                
                for link in wiki_links:
                    # 处理链接（可能包含别名）
                    link_path = link.strip()
                    
                    # 查找目标节点
                    for note_path, target_id in node_map.items():
                        if link_path in note_path or note_path.endswith(f"{link_path}.md"):
                            links.append({
                                "source": source_id,
                                "target": target_id,
                            })
                            break
            
            except Exception as e:
                print(f"解析链接失败 {md_file}: {e}")
        
        return {
            "nodes": nodes,
            "links": links,
        }
    
    def search_in_vault(self, query: str) -> List[Dict[str, Any]]:
        """在知识库中搜索"""
        results = []
        query_lower = query.lower()
        
        for md_file in self.vault_path.rglob("*.md"):
            if any(part.startswith('.') for part in md_file.relative_to(self.vault_path).parts):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if query_lower in content.lower():
                    # 找到匹配的上下文
                    lines = content.split('\n')
                    matching_lines = []
                    
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            # 获取上下文
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            context = '\n'.join(lines[start:end])
                            matching_lines.append({
                                "line_number": i + 1,
                                "context": context,
                            })
                    
                    results.append({
                        "path": str(md_file.relative_to(self.vault_path)),
                        "name": md_file.stem,
                        "matches": matching_lines[:5],  # 限制匹配数量
                    })
            
            except Exception as e:
                print(f"搜索失败 {md_file}: {e}")
        
        return results
    
    def get_tags(self) -> Dict[str, List[str]]:
        """获取所有标签及其对应的文件"""
        tags = {}
        
        for md_file in self.vault_path.rglob("*.md"):
            if any(part.startswith('.') for part in md_file.relative_to(self.vault_path).parts):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 查找标签 #tag
                import re
                file_tags = re.findall(r'#([a-zA-Z0-9_\-\u4e00-\u9fff]+)', content)
                
                relative_path = str(md_file.relative_to(self.vault_path))
                
                for tag in file_tags:
                    if tag not in tags:
                        tags[tag] = []
                    tags[tag].append(relative_path)
            
            except Exception as e:
                print(f"解析标签失败 {md_file}: {e}")
        
        return tags
