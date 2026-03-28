"""
File Brain - 主控制器
整合所有功能的核心模块
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import os

from core.content_indexer import ContentIndexer
from core.search_engine import SearchEngine, SearchResult
from core.file_reader import FileContent
from core.knowledge_graph import KnowledgeGraphBuilder, GraphStorage, GraphVisualizer
from core.file_organizer import FileNamer, TagExtractor
from core.logger import log_info, log_error, log_debug, log_warning
from readers import get_reader_for_file
from readers.external import NotionReader, ObsidianReader
from ai.qa_engine import QaEngine
from monitor.file_monitor import FileMonitor, WatchEvent, EventType
from config import SUPPORTED_EXTENSIONS, UPLOAD_DIR


class FileBrain:
    """
    File Brain 主类
    提供统一的文件读取、索引和搜索接口
    """
    
    def __init__(self):
        self.indexer = ContentIndexer()
        self.search_engine = SearchEngine()
        self.notion_reader = None
        self.obsidian_reader = None
        self.qa_engine = None
        self.file_monitor = None
        self.knowledge_graph = None
        self.graph_storage = GraphStorage()
        self.file_namer = FileNamer()
        self.tag_extractor = TagExtractor()
        self._init_knowledge_graph()
    
    def _get_qa_engine(self):
        """获取问答引擎（延迟初始化）"""
        if self.qa_engine is None:
            self.qa_engine = QaEngine(self.search)
        return self.qa_engine
    
    def _get_file_monitor(self):
        """获取文件监控器（延迟初始化）"""
        if self.file_monitor is None:
            self.file_monitor = FileMonitor()
            self.file_monitor.add_handler(self._handle_monitor_event)
        return self.file_monitor
    
    def _init_knowledge_graph(self):
        """初始化知识图谱"""
        # 确保索引器已初始化
        if not self.indexer._initialized:
            self.indexer.initialize()
        # 从存储加载知识图谱
        graph = self.graph_storage.load()
        # 初始化知识图谱构建器
        self.knowledge_graph = KnowledgeGraphBuilder(self.indexer.embedding_model)
        # 加载现有图结构
        self.knowledge_graph.graph = graph
    
    def _handle_monitor_event(self, event: WatchEvent):
        """处理监控事件"""
        if event.event_type in [EventType.CREATED, EventType.MODIFIED]:
            if event.path.is_file():
                log_info(f"自动索引: {event.path}")
                self.add_file(event.path)
        elif event.event_type == EventType.DELETED:
            log_info(f"自动删除: {event.path}")
            self.delete_source(str(event.path.absolute()))
    
    # ==================== 文件处理 ====================
    
    def add_file(self, file_path: Union[str, Path]) -> bool:
        """
        添加单个文件到索引
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否成功
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            log_warning(f"文件不存在: {file_path}")
            return False
        
        # 获取对应的读取器
        reader = get_reader_for_file(file_path)
        if not reader:
            log_warning(f"不支持的文件类型: {file_path.suffix}")
            return False
        
        try:
            # 读取文件
            content = reader.read(file_path)
            
            # 索引内容
            if self.indexer.index_content(content):
                # 更新知识图谱
                if self.knowledge_graph:
                    self.knowledge_graph.add_file(content)
                    # 保存知识图谱
                    self.graph_storage.save(self.knowledge_graph.get_graph())
                return True
            return False
        
        except Exception as e:
            log_error(f"处理文件失败 {file_path}", error=e)
            return False
    
    def add_directory(self, directory: Union[str, Path], 
                      recursive: bool = True,
                      file_types: Optional[List[str]] = None) -> Dict[str, int]:
        """
        添加整个目录到索引
        
        Args:
            directory: 目录路径
            recursive: 是否递归子目录
            file_types: 指定文件类型（如 ['.md', '.txt']）
        
        Returns:
            统计信息
        """
        directory = Path(directory)
        
        if not directory.exists():
            log_warning(f"目录不存在: {directory}")
            return {"success": 0, "failed": 0}
        
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        # 确定文件模式
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        # 遍历文件
        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue
            
            # 检查文件类型
            if file_types and file_path.suffix.lower() not in file_types:
                stats["skipped"] += 1
                continue
            
            # 检查是否支持
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                stats["skipped"] += 1
                continue
            
            # 添加文件
            if self.add_file(file_path):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        log_info(f"目录处理完成: {stats}")
        return stats
    
    def upload_and_index(self, file_content: bytes, filename: str) -> bool:
        """
        上传文件并索引
        
        Args:
            file_content: 文件二进制内容
            filename: 文件名
        
        Returns:
            是否成功
        """
        # 保存上传的文件
        upload_path = UPLOAD_DIR / filename
        
        try:
            with open(upload_path, 'wb') as f:
                f.write(file_content)
            
            # 添加到索引
            return self.add_file(upload_path)
        
        except Exception as e:
            log_error(f"上传文件失败", error=e)
            return False
    
    # ==================== Notion 集成 ====================
    
    def connect_notion(self, api_key: str = None) -> bool:
        """连接 Notion"""
        try:
            self.notion_reader = NotionReader(api_key)
            return self.notion_reader.client is not None
        except Exception as e:
            log_error(f"连接 Notion 失败", error=e)
            return False
    
    def index_notion_page(self, page_id: str) -> bool:
        """索引 Notion 页面"""
        if not self.notion_reader:
            log_warning("Notion 未连接")
            return False
        
        try:
            content = self.notion_reader.read(page_id=page_id)
            return self.indexer.index_content(content)
        except Exception as e:
            log_error(f"索引 Notion 页面失败", error=e)
            return False
    
    def index_notion_database(self, database_id: str) -> Dict[str, int]:
        """索引 Notion 数据库"""
        if not self.notion_reader:
            log_warning("Notion 未连接")
            return {"success": 0, "failed": 0}
        
        stats = {"success": 0, "failed": 0}
        
        try:
            contents = self.notion_reader.read(database_id=database_id)
            for content in contents:
                if self.indexer.index_content(content):
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
        except Exception as e:
            log_error(f"索引 Notion 数据库失败", error=e)
        
        return stats
    
    def list_notion_databases(self) -> List[Dict]:
        """列出 Notion 数据库"""
        if not self.notion_reader:
            return []
        return self.notion_reader.list_databases()
    
    # ==================== Obsidian 集成 ====================
    
    def connect_obsidian(self, vault_path: str) -> bool:
        """连接 Obsidian 知识库"""
        try:
            self.obsidian_reader = ObsidianReader(vault_path)
            return self.obsidian_reader.vault_path is not None
        except Exception as e:
            log_error(f"连接 Obsidian 失败", error=e)
            return False
    
    def index_obsidian_vault(self) -> Dict[str, int]:
        """索引整个 Obsidian 知识库"""
        if not self.obsidian_reader:
            log_warning("Obsidian 未连接")
            return {"success": 0, "failed": 0}
        
        stats = {"success": 0, "failed": 0}
        
        try:
            for content in self.obsidian_reader.read_vault():
                if self.indexer.index_content(content):
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
        except Exception as e:
            log_error(f"索引 Obsidian 知识库失败", error=e)
        
        return stats
    
    def get_obsidian_graph(self) -> Dict[str, Any]:
        """获取 Obsidian 知识图谱"""
        if not self.obsidian_reader:
            log_warning("Obsidian 未连接")
            return {"nodes": [], "links": []}
        return self.obsidian_reader.get_graph_data()
    
    # ==================== 搜索功能 ====================
    
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """
        搜索内容
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        return self.search_engine.search(query, top_k=top_k)
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """语义搜索"""
        return self.search_engine.semantic_search(query, top_k=top_k)
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """关键词搜索"""
        return self.search_engine.keyword_search(query, top_k=top_k)
    
    def hybrid_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """混合搜索"""
        return self.search_engine.hybrid_search(query, top_k=top_k)
    
    def search_by_type(self, query: str, file_type: str, top_k: int = 10) -> List[SearchResult]:
        """按文件类型搜索"""
        return self.search_engine.search(query, top_k=top_k, file_types=[file_type])
    
    # ==================== 管理功能 ====================
    
    def delete_source(self, source: str) -> bool:
        """删除指定来源的所有内容"""
        if self.indexer.delete_by_source(source):
            # 从知识图谱中移除
            if self.knowledge_graph:
                self.knowledge_graph.remove_file(source)
                # 保存知识图谱
                self.graph_storage.save(self.knowledge_graph.get_graph())
            return True
        return False
    
    def list_sources(self) -> List[str]:
        """列出所有已索引的来源"""
        return self.indexer.list_sources()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.indexer.get_stats()
    
    def clear_all(self) -> bool:
        """清空所有索引"""
        if self.indexer.clear_all():
            # 清空知识图谱
            if self.knowledge_graph:
                self.knowledge_graph.clear()
                # 删除知识图谱存储
                self.graph_storage.delete()
            return True
        return False
    
    def get_document_summary(self, source: str) -> Dict[str, Any]:
        """获取文档摘要"""
        return self.search_engine.get_document_summary(source)
    
    # ==================== AI 问答功能 ====================
    
    def ask(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        基于索引内容回答问题
        
        Args:
            question: 用户问题
            top_k: 检索的文档数量
        
        Returns:
            包含回答和来源的字典
        """
        qa_engine = self._get_qa_engine()
        return qa_engine.ask(question, top_k=top_k)
    
    def get_ai_status(self) -> Dict[str, Any]:
        """获取 AI 状态"""
        qa_engine = self._get_qa_engine()
        return qa_engine.get_ai_status()
    
    # ==================== 文件夹监控功能 ====================
    
    def watch_path(self, path: Union[str, Path]) -> bool:
        """
        开始监控路径
        
        Args:
            path: 要监控的文件或目录路径
        
        Returns:
            是否成功
        """
        monitor = self._get_file_monitor()
        return monitor.add_path(path)
    
    def unwatch_path(self, path: Union[str, Path]) -> bool:
        """
        停止监控路径
        
        Args:
            path: 要停止监控的路径
        
        Returns:
            是否成功
        """
        monitor = self._get_file_monitor()
        return monitor.remove_path(path)
    
    def start_watching(self):
        """启动文件监控"""
        monitor = self._get_file_monitor()
        if not monitor.is_running:
            monitor.start()
    
    def stop_watching(self):
        """停止文件监控"""
        monitor = self._get_file_monitor()
        if monitor.is_running:
            monitor.stop()
    
    def get_watched_paths(self) -> List[Path]:
        """获取正在监控的路径列表"""
        monitor = self._get_file_monitor()
        return monitor.get_watched_paths()
    
    def is_watching(self) -> bool:
        """检查是否正在监控"""
        monitor = self._get_file_monitor()
        return monitor.is_running
    
    # ==================== 知识图谱功能 ====================
    
    def get_related_files(self, file_path: Union[str, Path], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        获取与指定文件相关的文件
        
        Args:
            file_path: 文件路径
            top_k: 返回的文件数量
        
        Returns:
            相关文件列表
        """
        if not self.knowledge_graph:
            return []
        
        file_path_str = str(Path(file_path).absolute())
        related = self.knowledge_graph.get_related_files(file_path_str, top_k=top_k)
        
        # 转换为更友好的格式
        result = []
        for file_path, similarity in related:
            result.append({
                'file_path': file_path,
                'similarity': similarity
            })
        
        return result
    
    def get_knowledge_graph(self) -> Dict[str, Any]:
        """
        获取知识图谱数据
        
        Returns:
            知识图谱的字典表示
        """
        if not self.knowledge_graph:
            return {'nodes': [], 'edges': []}
        
        return GraphVisualizer.to_dict(self.knowledge_graph.get_graph())
    
    def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """
        获取知识图谱统计信息
        
        Returns:
            统计信息字典
        """
        if not self.knowledge_graph:
            return {'nodes': 0, 'edges': 0, 'density': 0}
        
        return self.knowledge_graph.get_stats()
    
    def get_central_files(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        获取知识图谱中最中心的文件
        
        Args:
            top_k: 返回的文件数量
        
        Returns:
            中心文件列表
        """
        if not self.knowledge_graph:
            return []
        
        central_nodes = GraphVisualizer.get_central_nodes(self.knowledge_graph.get_graph(), top_k=top_k)
        
        # 转换为更友好的格式
        result = []
        for file_path, centrality in central_nodes:
            result.append({
                'file_path': file_path,
                'centrality': centrality
            })
        
        return result
    
    # ==================== 文件组织功能 ====================
    
    def generate_filename(self, file_path: Union[str, Path]) -> str:
        """
        为文件生成智能文件名
        
        Args:
            file_path: 文件路径
        
        Returns:
            生成的文件名
        """
        file_path = Path(file_path)
        
        # 获取文件读取器
        reader = get_reader_for_file(file_path)
        if not reader:
            return file_path.name
        
        # 读取文件内容
        try:
            content = reader.read(file_path)
            return self.file_namer.generate_filename(content)
        except Exception as e:
            log_error(f"生成文件名失败", error=e)
            return file_path.name
    
    def rename_file(self, file_path: Union[str, Path]) -> str:
        """
        智能重命名文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            新的文件路径
        """
        file_path = Path(file_path)
        
        # 获取文件读取器
        reader = get_reader_for_file(file_path)
        if not reader:
            return str(file_path)
        
        # 读取文件内容
        try:
            content = reader.read(file_path)
            return self.file_namer.rename_file(str(file_path), content)
        except Exception as e:
            log_error(f"重命名文件失败", error=e)
            return str(file_path)
    
    def extract_tags(self, file_path: Union[str, Path], top_n: int = 10) -> List[str]:
        """
        从文件中提取标签
        
        Args:
            file_path: 文件路径
            top_n: 返回的标签数量
        
        Returns:
            标签列表
        """
        file_path = Path(file_path)
        
        # 获取文件读取器
        reader = get_reader_for_file(file_path)
        if not reader:
            return []
        
        # 读取文件内容
        try:
            content = reader.read(file_path)
            return self.tag_extractor.extract_tags(content, top_n=top_n)
        except Exception as e:
            log_error(f"提取标签失败", error=e)
            return []
    
    def organize_files(self, directory: Union[str, Path], recursive: bool = True) -> Dict[str, Any]:
        """
        智能组织目录中的文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归处理子目录
        
        Returns:
            组织结果统计
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return {"success": 0, "failed": 0, "skipped": 0}
        
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        # 确定文件模式
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        # 遍历文件
        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue
            
            # 检查是否支持
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                stats["skipped"] += 1
                continue
            
            # 重命名文件
            try:
                new_path = self.rename_file(file_path)
                if new_path != str(file_path):
                    stats["success"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                log_error(f"组织文件失败 {file_path}", error=e)
                stats["failed"] += 1
        
        return stats
