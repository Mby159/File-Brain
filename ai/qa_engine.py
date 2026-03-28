"""
问答引擎 - 结合搜索和 AI
"""
from typing import Optional, List, Dict, Any

from ai.ai_provider import get_ai_provider, AIResponse


class QaEngine:
    """问答引擎"""
    
    def __init__(self, search_func):
        self.search_func = search_func
        self.ai_provider = get_ai_provider()
        self.system_prompt = """你是一个有用的助手，基于提供的参考信息回答用户的问题。
如果参考信息中没有答案，请诚实地说"在我的参考资料中找不到相关内容"。
请用简洁、准确的语言回答问题，并在回答中注明信息来源（如果可能）。
"""
    
    def ask(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        基于索引内容回答问题
        
        Args:
            question: 用户问题
            top_k: 检索的文档数量
        
        Returns:
            包含回答和来源的字典
        """
        # 1. 搜索相关内容
        search_results = self.search_func(question, top_k=top_k)
        
        if not search_results:
            return {
                "answer": "未找到相关内容。请先索引一些文件。",
                "success": False,
                "sources": [],
                "ai_provider": self.ai_provider.get_provider_name(),
            }
        
        # 2. 构建上下文
        context_parts = []
        sources = []
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"[来源 {i}]")
            context_parts.append(f"标题: {result.title}")
            context_parts.append(f"来源: {result.source}")
            context_parts.append(f"内容: {result.content}")
            context_parts.append("")
            
            sources.append({
                "title": result.title,
                "source": result.source,
                "file_type": result.file_type,
                "relevance": result.score,
                "snippet": result.content[:200],
            })
        
        context = "\n".join(context_parts)
        
        # 3. 调用 AI 回答
        user_prompt = f"问题：{question}"
        
        ai_response = self.ai_provider.chat(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            context=context
        )
        
        if ai_response.success:
            return {
                "answer": ai_response.content,
                "success": True,
                "sources": sources,
                "ai_provider": self.ai_provider.get_provider_name(),
                "metadata": ai_response.metadata,
            }
        else:
            # AI 失败时，返回搜索结果
            fallback_answer = "找到以下相关内容（AI 功能未启用或失败）：\n\n"
            for i, source in enumerate(sources, 1):
                fallback_answer += f"{i}. {source['title']}\n"
                fallback_answer += f"   来源: {source['source']}\n"
                fallback_answer += f"   相关度: {source['relevance']:.2%}\n"
                fallback_answer += f"   预览: {source['snippet']}...\n\n"
            
            return {
                "answer": fallback_answer,
                "success": False,
                "sources": sources,
                "ai_provider": self.ai_provider.get_provider_name(),
                "error": ai_response.error,
            }
    
    def get_ai_status(self) -> Dict[str, Any]:
        """获取 AI 状态"""
        provider_name = self.ai_provider.get_provider_name()
        is_available = self.ai_provider.is_available()
        
        return {
            "provider": provider_name,
            "available": is_available,
            "ai_enabled": provider_name != "none",
        }
