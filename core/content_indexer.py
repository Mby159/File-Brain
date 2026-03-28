"""
内容索引器 - 管理向量数据库
使用 scikit-learn 进行向量相似度计算
"""
import json
import pickle
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from config import VECTOR_DB_PATH, EMBEDDING_MODEL, SENTENCE_TRANSFORMER_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from .models import FileContent
from .embedding import TfidfEmbedding, SentenceTransformersEmbedding


class ContentIndexer:
    """内容索引管理器 - 使用 scikit-learn"""
    
    def __init__(self, collection_name: str = "file_brain"):
        self.collection_name = collection_name
        self.metadata_path = VECTOR_DB_PATH / f"{collection_name}_metadata.pkl"
        self.embeddings_path = VECTOR_DB_PATH / f"{collection_name}_embeddings.npy"
        
        self.embeddings = None  # numpy array of embeddings
        self.documents = []
        self.metadatas = []
        self.embedding_model = None
        self.use_tfidf = False
        self._initialized = False
        self.dimension = 384  # 默认维度
    
    def initialize(self):
        """初始化索引器"""
        if self._initialized:
            return
        
        # 根据配置决定使用哪种模型
        use_ai_model = EMBEDDING_MODEL.lower() not in ['tfidf', 'tf-idf', 'none']
        
        # 加载现有数据
        if self.metadata_path.exists() and self.embeddings_path.exists():
            try:
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadatas = data.get('metadatas', [])
                    self.use_tfidf = data.get('use_tfidf', not use_ai_model)
                
                self.embeddings = np.load(self.embeddings_path)
                model_type = "TF-IDF" if self.use_tfidf else "AI嵌入模型"
                print(f"已加载现有索引: {len(self.documents)} 条文档 ({model_type})")
            except Exception as e:
                print(f"加载索引失败: {e}，创建新索引")
                self.embeddings = np.empty((0, self.dimension), dtype='float32')
                self.documents = []
                self.metadatas = []
                self.use_tfidf = not use_ai_model
        else:
            print("创建新索引")
            self.embeddings = np.empty((0, self.dimension), dtype='float32')
            self.documents = []
            self.metadatas = []
            self.use_tfidf = not use_ai_model
        
        # 加载嵌入模型
        if use_ai_model:
            try:
                model_name = SENTENCE_TRANSFORMER_MODEL
                print(f"正在加载 AI 嵌入模型: {model_name}...")
                print("(首次使用需要联网下载模型，约80-100MB)")
                self.embedding_model = SentenceTransformersEmbedding(model_name)
                self.dimension = self.embedding_model.get_dimension()
                print("AI 嵌入模型加载完成")
                self.use_tfidf = False
            except Exception as e:
                print(f"AI 嵌入模型加载失败: {e}")
                print("将使用 TF-IDF 作为降级方案")
                self.embedding_model = TfidfEmbedding()
                self.dimension = self.embedding_model.get_dimension()
                self.use_tfidf = True
        else:
            print("使用 TF-IDF 模式 (完全离线)")
            self.embedding_model = TfidfEmbedding()
            self.dimension = self.embedding_model.get_dimension()
            self.use_tfidf = True
        
        self._initialized = True
    
    def _get_embedding(self, texts: List[str]) -> np.ndarray:
        """获取文本的嵌入向量"""
        if self.embedding_model:
            if self.use_tfidf and len(self.documents) == 0:
                # 第一次使用 TF-IDF，需要训练向量器
                return self.embedding_model.encode_with_fit(texts).astype('float32')
            else:
                return self.embedding_model.encode(texts).astype('float32')
        else:
            # 如果没有模型，返回零向量
            return np.zeros((len(texts), self.dimension), dtype='float32')
    

    
    def index_content(self, content: FileContent) -> bool:
        """索引文件内容"""
        if not self._initialized:
            self.initialize()
        
        try:
            # 如果内容已分块，使用分块；否则对整个内容编码
            texts_to_index = content.chunks if content.chunks else [content.content]
            
            if not texts_to_index or not any(texts_to_index):
                print(f"警告: 内容为空，跳过索引: {content.source}")
                return False
            
            # 保存文档和元数据
            start_idx = len(self.documents)
            for i, chunk in enumerate(texts_to_index):
                self.documents.append(chunk)
                
                metadata = {
                    "source": content.source,
                    "file_type": content.file_type,
                    "title": content.title or "",
                    "chunk_index": i,
                    "total_chunks": len(texts_to_index),
                    "indexed_at": datetime.now().isoformat(),
                }
                # 添加原始元数据
                if content.metadata:
                    for key, value in content.metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            metadata[f"meta_{key}"] = value
                
                self.metadatas.append(metadata)
            
            # 生成嵌入向量
            if self.use_tfidf and len(self.documents) > 0:
                # 对于 TF-IDF，需要重新训练整个向量器
                all_texts = self.documents + texts_to_index
                self.embeddings = self.embedding_model.encode_with_fit(all_texts)
            else:
                # 对于 AI 嵌入模型，直接添加新向量
                new_embeddings = self._get_embedding(texts_to_index)
                if self.embeddings.shape[0] == 0:
                    self.embeddings = new_embeddings
                else:
                    self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
            # 保存索引
            self._save_index()
            
            print(f"已索引: {content.source} ({len(texts_to_index)} 块)")
            return True
            
        except Exception as e:
            print(f"索引失败 {content.source}: {e}")
            return False
    
    def _save_index(self):
        """保存索引到磁盘"""
        try:
            # 保存嵌入向量
            np.save(self.embeddings_path, self.embeddings)
            
            # 保存元数据
            data = {
                'documents': self.documents,
                'metadatas': self.metadatas,
                'use_tfidf': self.use_tfidf
            }
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"保存索引失败: {e}")
    
    def delete_by_source(self, source: str) -> bool:
        """删除指定来源的所有文档"""
        if not self._initialized:
            self.initialize()
        
        try:
            # 找到要删除的索引
            indices_to_delete = []
            for i, metadata in enumerate(self.metadatas):
                if metadata.get('source') == source:
                    indices_to_delete.append(i)
            
            if not indices_to_delete:
                return False
            
            # 保留不需要删除的文档
            keep_indices = [i for i in range(len(self.documents)) if i not in indices_to_delete]
            
            self.documents = [self.documents[i] for i in keep_indices]
            self.metadatas = [self.metadatas[i] for i in keep_indices]
            
            # 重建索引
            if self.use_tfidf:
                self._build_tfidf()
            elif len(keep_indices) > 0:
                self.embeddings = self.embeddings[keep_indices]
            else:
                self.embeddings = np.empty((0, self.dimension), dtype='float32')
            
            self._save_index()
            print(f"已删除: {source} ({len(indices_to_delete)} 条)")
            return True
            
        except Exception as e:
            print(f"删除失败 {source}: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5, 
               filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """搜索相似内容"""
        if not self._initialized:
            self.initialize()
        
        try:
            if len(self.documents) == 0:
                return []
            
            # 编码查询
            query_embedding = self.embedding_model.encode_query(query)
            
            # 计算余弦相似度
            from sklearn.metrics.pairwise import cosine_similarity
            
            # 检查维度是否匹配
            if query_embedding.shape[1] != self.embeddings.shape[1]:
                print("维度不匹配，无法搜索")
                return []
            
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # 获取 top-k 结果
            top_indices = np.argsort(similarities)[::-1]
            
            # 格式化结果
            formatted_results = []
            for idx in top_indices:
                metadata = self.metadatas[idx]
                score = float(similarities[idx])
                
                # 过滤掉分数为0的结果（TF-IDF中不相关的结果）
                if score <= 0:
                    continue
                
                # 应用过滤
                if filter_dict:
                    skip = False
                    for key, value in filter_dict.items():
                        if metadata.get(key) != value:
                            skip = True
                            break
                    if skip:
                        continue
                
                formatted_results.append({
                    "id": str(idx),
                    "content": self.documents[idx],
                    "metadata": metadata,
                    "score": score,
                })
                
                if len(formatted_results) >= top_k:
                    break
            
            return formatted_results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        if not self._initialized:
            self.initialize()
        
        model_info = "TF-IDF (完全离线)" if self.use_tfidf else f"AI嵌入模型 ({SENTENCE_TRANSFORMER_MODEL})"
        
        return {
            "total_documents": len(self.documents),
            "collection_name": self.collection_name,
            "embedding_model": model_info,
            "model_type": "tfidf" if self.use_tfidf else "ai",
        }
    
    def list_sources(self) -> List[str]:
        """列出所有已索引的来源"""
        if not self._initialized:
            self.initialize()
        
        sources = set()
        for metadata in self.metadatas:
            if 'source' in metadata:
                sources.add(metadata['source'])
        return sorted(list(sources))
    
    def clear_all(self) -> bool:
        """清空所有索引"""
        if not self._initialized:
            self.initialize()
        
        try:
            self.embeddings = np.empty((0, self.dimension), dtype='float32')
            self.documents = []
            self.metadatas = []
            
            # 重新初始化嵌入模型
            use_ai_model = EMBEDDING_MODEL.lower() not in ['tfidf', 'tf-idf', 'none']
            if use_ai_model:
                self.embedding_model = SentenceTransformersEmbedding(SENTENCE_TRANSFORMER_MODEL)
            else:
                self.embedding_model = TfidfEmbedding()
            self.dimension = self.embedding_model.get_dimension()
            self.use_tfidf = not use_ai_model
            
            # 删除文件
            if self.embeddings_path.exists():
                self.embeddings_path.unlink()
            if self.metadata_path.exists():
                self.metadata_path.unlink()
            
            print("已清空所有索引")
            return True
        except Exception as e:
            print(f"清空索引失败: {e}")
            return False
