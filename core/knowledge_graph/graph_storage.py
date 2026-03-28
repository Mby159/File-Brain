"""
知识图谱存储
"""
import pickle
import json
from pathlib import Path
import networkx as nx

from config import DATA_DIR


class GraphStorage:
    """知识图谱存储"""
    
    def __init__(self, storage_path: Path = None):
        """初始化知识图谱存储
        
        Args:
            storage_path: 存储路径，默认使用 DATA_DIR/knowledge_graph
        """
        if storage_path is None:
            self.storage_path = DATA_DIR / "knowledge_graph"
        else:
            self.storage_path = Path(storage_path)
        
        self.storage_path.mkdir(exist_ok=True)
        self.graph_file = self.storage_path / "graph.pkl"
        self.metadata_file = self.storage_path / "metadata.json"
    
    def save(self, graph: nx.Graph) -> bool:
        """保存知识图谱到磁盘
        
        Args:
            graph: 知识图谱对象
        
        Returns:
            是否保存成功
        """
        try:
            # 保存图结构
            with open(self.graph_file, 'wb') as f:
                pickle.dump(graph, f)
            
            # 保存元数据
            metadata = {
                'nodes': graph.number_of_nodes(),
                'edges': graph.number_of_edges(),
                'density': nx.density(graph)
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存知识图谱失败: {e}")
            return False
    
    def load(self) -> nx.Graph:
        """从磁盘加载知识图谱
        
        Returns:
            知识图谱对象
        """
        try:
            if self.graph_file.exists():
                with open(self.graph_file, 'rb') as f:
                    graph = pickle.load(f)
                print(f"成功加载知识图谱: {graph.number_of_nodes()} 个节点, {graph.number_of_edges()} 条边")
                return graph
            else:
                print("知识图谱文件不存在，创建新的知识图谱")
                return nx.Graph()
        except Exception as e:
            print(f"加载知识图谱失败: {e}")
            return nx.Graph()
    
    def exists(self) -> bool:
        """检查知识图谱文件是否存在
        
        Returns:
            是否存在
        """
        return self.graph_file.exists()
    
    def delete(self) -> bool:
        """删除知识图谱文件
        
        Returns:
            是否删除成功
        """
        try:
            if self.graph_file.exists():
                self.graph_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            return True
        except Exception as e:
            print(f"删除知识图谱文件失败: {e}")
            return False
    
    def get_metadata(self) -> dict:
        """获取知识图谱元数据
        
        Returns:
            元数据字典
        """
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"获取知识图谱元数据失败: {e}")
            return {}
