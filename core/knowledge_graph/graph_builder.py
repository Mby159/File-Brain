"""
知识图谱构建器
"""
from pathlib import Path
from typing import Dict, List, Set, Tuple
import networkx as nx
import numpy as np

from core.models import FileContent
from core.embedding import BaseEmbedding


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self, embedding_model: BaseEmbedding):
        """初始化知识图谱构建器
        
        Args:
            embedding_model: 嵌入模型，用于计算文件相似度
        """
        self.embedding_model = embedding_model
        self.graph = nx.Graph()
    
    def add_file(self, file_content: FileContent) -> bool:
        """添加文件到知识图谱
        
        Args:
            file_content: 文件内容对象
        
        Returns:
            是否添加成功
        """
        try:
            # 添加节点
            node_id = file_content.source
            self.graph.add_node(node_id, 
                              title=file_content.title,
                              file_type=file_content.file_type,
                              content=file_content.content,
                              metadata=file_content.metadata)
            
            # 计算与现有节点的相似度
            self._calculate_similarities(node_id, file_content)
            
            # 基于文件路径和命名的关系
            self._add_path_relationships(node_id, file_content)
            
            return True
        except Exception as e:
            print(f"添加文件到知识图谱失败: {e}")
            return False
    
    def _calculate_similarities(self, node_id: str, file_content: FileContent):
        """计算文件与现有节点的相似度
        
        Args:
            node_id: 当前文件的节点ID
            file_content: 文件内容对象
        """
        if len(self.graph.nodes) <= 1:
            return
        
        # 获取当前文件的嵌入向量
        current_embedding = self.embedding_model.encode_query(file_content.content)
        
        # 计算与其他节点的相似度
        for other_node_id, data in self.graph.nodes(data=True):
            if other_node_id == node_id:
                continue
            
            # 获取其他文件的内容
            other_content = data.get('content', '')
            if not other_content:
                continue
            
            # 计算相似度
            other_embedding = self.embedding_model.encode_query(other_content)
            similarity = np.dot(current_embedding, other_embedding.T)[0][0]
            
            # 如果相似度大于阈值，添加边
            if similarity > 0.3:
                self.graph.add_edge(node_id, other_node_id, 
                                   weight=similarity,
                                   relationship='content_similarity')
    
    def _add_path_relationships(self, node_id: str, file_content: FileContent):
        """基于文件路径和命名添加关系
        
        Args:
            node_id: 当前文件的节点ID
            file_content: 文件内容对象
        """
        file_path = Path(file_content.source)
        
        # 与同一目录下的文件建立关系
        for other_node_id, data in self.graph.nodes(data=True):
            if other_node_id == node_id:
                continue
            
            other_path = Path(other_node_id)
            
            # 如果在同一目录
            if other_path.parent == file_path.parent:
                self.graph.add_edge(node_id, other_node_id, 
                                   weight=0.5,
                                   relationship='same_directory')
            
            # 如果文件名相似
            if self._filename_similarity(file_path.name, other_path.name) > 0.6:
                self.graph.add_edge(node_id, other_node_id, 
                                   weight=0.4,
                                   relationship='similar_name')
    
    def _filename_similarity(self, name1: str, name2: str) -> float:
        """计算文件名相似度
        
        Args:
            name1: 第一个文件名
            name2: 第二个文件名
        
        Returns:
            相似度分数
        """
        # 简单的字符串相似度计算
        name1 = name1.lower().replace('.', ' ')
        name2 = name2.lower().replace('.', ' ')
        
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 and not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union
    
    def get_graph(self) -> nx.Graph:
        """获取构建的知识图谱
        
        Returns:
            知识图谱对象
        """
        return self.graph
    
    def get_related_files(self, file_path: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """获取与指定文件相关的文件
        
        Args:
            file_path: 文件路径
            top_k: 返回的文件数量
        
        Returns:
            相关文件列表，每个元素包含文件路径和相似度
        """
        if file_path not in self.graph:
            return []
        
        # 获取与该节点相连的所有边
        edges = self.graph.edges(file_path, data=True)
        
        # 按权重排序
        related = [(neighbor, data['weight']) for _, neighbor, data in edges]
        related.sort(key=lambda x: x[1], reverse=True)
        
        return related[:top_k]
    
    def remove_file(self, file_path: str) -> bool:
        """从知识图谱中移除文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否移除成功
        """
        try:
            if file_path in self.graph:
                self.graph.remove_node(file_path)
            return True
        except Exception as e:
            print(f"从知识图谱中移除文件失败: {e}")
            return False
    
    def clear(self):
        """清空知识图谱"""
        self.graph.clear()
    
    def get_stats(self) -> Dict:
        """获取知识图谱统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph)
        }
