"""
知识图谱可视化
"""
import json
from typing import Dict, List, Tuple
import networkx as nx


class GraphVisualizer:
    """知识图谱可视化"""
    
    @staticmethod
    def to_dict(graph: nx.Graph) -> Dict:
        """将知识图谱转换为字典格式，便于前端可视化
        
        Args:
            graph: 知识图谱对象
        
        Returns:
            知识图谱的字典表示
        """
        nodes = []
        edges = []
        
        # 处理节点
        for node_id, data in graph.nodes(data=True):
            node = {
                'id': node_id,
                'title': data.get('title', ''),
                'file_type': data.get('file_type', ''),
                'metadata': data.get('metadata', {})
            }
            nodes.append(node)
        
        # 处理边
        for u, v, data in graph.edges(data=True):
            edge = {
                'source': u,
                'target': v,
                'weight': float(data.get('weight', 0)),
                'relationship': data.get('relationship', 'related')
            }
            edges.append(edge)
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    @staticmethod
    def to_json(graph: nx.Graph) -> str:
        """将知识图谱转换为 JSON 字符串
        
        Args:
            graph: 知识图谱对象
        
        Returns:
            JSON 字符串
        """
        graph_dict = GraphVisualizer.to_dict(graph)
        return json.dumps(graph_dict, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_subgraph(graph: nx.Graph, center_node: str, radius: int = 2) -> nx.Graph:
        """获取以指定节点为中心的子图
        
        Args:
            graph: 知识图谱对象
            center_node: 中心节点 ID
            radius: 半径，默认 2
        
        Returns:
            子图对象
        """
        if center_node not in graph:
            return nx.Graph()
        
        # 获取指定半径内的所有节点
        nodes = set()
        nodes.add(center_node)
        
        for i in range(radius):
            new_nodes = set()
            for node in nodes:
                neighbors = list(graph.neighbors(node))
                new_nodes.update(neighbors)
            nodes.update(new_nodes)
        
        # 创建子图
        return graph.subgraph(nodes)
    
    @staticmethod
    def get_central_nodes(graph: nx.Graph, top_k: int = 5) -> List[Tuple[str, float]]:
        """获取图中最中心的节点
        
        Args:
            graph: 知识图谱对象
            top_k: 返回的节点数量
        
        Returns:
            中心节点列表，每个元素包含节点 ID 和中心度
        """
        if not graph.nodes:
            return []
        
        # 使用度中心性
        centrality = nx.degree_centrality(graph)
        
        # 按中心度排序
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_nodes[:top_k]
    
    @staticmethod
    def get_clusters(graph: nx.Graph) -> List[List[str]]:
        """获取图中的聚类
        
        Args:
            graph: 知识图谱对象
        
        Returns:
            聚类列表，每个聚类是节点 ID 的列表
        """
        if not graph.nodes:
            return []
        
        # 使用连通分量作为聚类
        clusters = list(nx.connected_components(graph))
        return [list(cluster) for cluster in clusters]
