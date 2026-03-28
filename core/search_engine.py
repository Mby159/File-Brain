"""
搜索引擎 - 高级搜索功能
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from core.content_indexer import ContentIndexer


@dataclass
class SearchResult:
    """搜索结果"""
    content: str
    source: str
    file_type: str
    title: str
    score: float
    metadata: Dict[str, Any]
    context: str = ""  # 上下文片段


class SearchEngine:
    """搜索引擎"""
    
    def __init__(self):
        self.indexer = ContentIndexer()
    
    def search(self, query: str, top_k: int = 10,
               file_types: Optional[List[str]] = None,
               sources: Optional[List[str]] = None) -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            file_types: 过滤文件类型
            sources: 过滤来源
        """
        # 构建过滤条件
        filter_dict = {}
        
        if file_types:
            if len(file_types) == 1:
                filter_dict["file_type"] = file_types[0]
            else:
                filter_dict["$or"] = [{"file_type": ft} for ft in file_types]
        
        if sources:
            if len(sources) == 1:
                filter_dict["source"] = sources[0]
            else:
                if "$or" in filter_dict:
                    # 复杂过滤条件需要重新构建
                    pass
                else:
                    filter_dict["$or"] = [{"source": s} for s in sources]
        
        # 执行搜索
        results = self.indexer.search(query, top_k=top_k, filter_dict=filter_dict if filter_dict else None)
        
        # 格式化结果
        search_results = []
        for result in results:
            metadata = result.get("metadata", {})
            search_results.append(SearchResult(
                content=result.get("content", ""),
                source=metadata.get("source", ""),
                file_type=metadata.get("file_type", ""),
                title=metadata.get("title", ""),
                score=result.get("score", 0),
                metadata=metadata,
                context=self._extract_context(result.get("content", ""), query)
            ))
        
        return search_results
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """语义搜索（与search相同，用于明确语义搜索）"""
        return self.search(query, top_k=top_k)
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """关键词搜索 - 在语义搜索结果中过滤"""
        results = self.search(query, top_k=top_k * 2)  # 获取更多结果用于过滤
        
        # 关键词过滤
        keywords = query.lower().split()
        filtered_results = []
        
        for result in results:
            content_lower = result.content.lower()
            # 检查是否包含关键词
            if any(kw in content_lower for kw in keywords):
                filtered_results.append(result)
        
        return filtered_results[:top_k]
    
    def hybrid_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """混合搜索 - 结合语义和关键词"""
        semantic_results = self.search(query, top_k=top_k)
        keyword_results = self.keyword_search(query, top_k=top_k)
        
        # 合并结果并去重
        seen_sources = set()
        combined_results = []
        
        # 优先语义搜索结果
        for result in semantic_results:
            key = (result.source, result.content[:100])
            if key not in seen_sources:
                seen_sources.add(key)
                combined_results.append(result)
        
        # 添加关键词搜索结果
        for result in keyword_results:
            key = (result.source, result.content[:100])
            if key not in seen_sources:
                seen_sources.add(key)
                combined_results.append(result)
        
        # 按分数排序
        combined_results.sort(key=lambda x: x.score, reverse=True)
        
        return combined_results[:top_k]
    
    def search_by_source(self, source: str, top_k: int = 100) -> List[SearchResult]:
        """搜索特定来源的所有内容"""
        filter_dict = {"source": source}
        results = self.indexer.search("", top_k=top_k, filter_dict=filter_dict)
        
        search_results = []
        for result in results:
            metadata = result.get("metadata", {})
            search_results.append(SearchResult(
                content=result.get("content", ""),
                source=metadata.get("source", ""),
                file_type=metadata.get("file_type", ""),
                title=metadata.get("title", ""),
                score=1.0,
                metadata=metadata
            ))
        
        return search_results
    
    def get_document_summary(self, source: str) -> Dict[str, Any]:
        """获取文档摘要"""
        results = self.search_by_source(source)
        
        if not results:
            return {"error": "Document not found"}
        
        total_chunks = len(results)
        file_type = results[0].file_type
        title = results[0].title
        
        # 合并内容
        full_content = "\n\n".join([r.content for r in results])
        
        return {
            "source": source,
            "title": title,
            "file_type": file_type,
            "total_chunks": total_chunks,
            "preview": full_content[:1000] + "..." if len(full_content) > 1000 else full_content,
        }
    
    def _extract_context(self, content: str, query: str, window: int = 100) -> str:
        """提取查询关键词周围的上下文"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 查找关键词位置
        pos = content_lower.find(query_lower)
        if pos == -1:
            # 尝试查找单个关键词
            for word in query_lower.split():
                pos = content_lower.find(word)
                if pos != -1:
                    break
        
        if pos == -1:
            # 返回开头
            return content[:window * 2] + "..." if len(content) > window * 2 else content
        
        # 提取上下文
        start = max(0, pos - window)
        end = min(len(content), pos + len(query) + window)
        
        context = content[start:end]
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """获取搜索统计"""
        return self.indexer.get_stats()
    
    def list_all_sources(self) -> List[str]:
        """列出所有来源"""
        return self.indexer.list_sources()
