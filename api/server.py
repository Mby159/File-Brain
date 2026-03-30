"""
FastAPI 服务器
提供 RESTful API 接口
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from file_brain import FileBrain
from config import HOST, PORT

# 创建 FastAPI 应用
app = FastAPI(
    title="File Brain API",
    description="本地文件系统智能搜索和管理 API",
    version="1.0.0"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 FileBrain 实例
file_brain = FileBrain()


# ==================== 数据模型 ====================

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    search_type: str = "semantic"  # semantic, keyword, hybrid


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    query: str


class DirectoryIndexRequest(BaseModel):
    path: str
    recursive: bool = True
    file_types: Optional[List[str]] = None


class NotionConnectRequest(BaseModel):
    api_key: str


class NotionIndexRequest(BaseModel):
    page_id: Optional[str] = None
    database_id: Optional[str] = None


class ObsidianConnectRequest(BaseModel):
    vault_path: str


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


class FileOrganizeRequest(BaseModel):
    path: str
    recursive: bool = True


class FileRenameRequest(BaseModel):
    path: str


class TagExtractRequest(BaseModel):
    path: str
    top_n: int = 10


class SmartMonitorConfigRequest(BaseModel):
    mode: Optional[str] = None
    monitor_searched_files: Optional[bool] = None
    monitor_custom_dirs: Optional[List[str]] = None
    active_file_interval: Optional[int] = None
    inactive_file_interval: Optional[int] = None
    whitelist: Optional[List[str]] = None
    blacklist: Optional[List[str]] = None


# ==================== API 路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "File Brain API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    return file_brain.get_stats()


@app.get("/ai/status")
async def get_ai_status():
    """获取 AI 状态"""
    try:
        return file_brain.get_ai_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/ask")
async def ask(request: AskRequest):
    """AI 问答"""
    try:
        return file_brain.ask(request.question, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 文件管理 ====================

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传并索引文件"""
    try:
        content = await file.read()
        success = file_brain.upload_and_index(content, file.filename)
        
        if success:
            return {"success": True, "message": f"文件 {file.filename} 已上传并索引"}
        else:
            raise HTTPException(status_code=400, detail="文件索引失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/files/index-directory")
async def index_directory(request: DirectoryIndexRequest):
    """索引整个目录"""
    try:
        stats = file_brain.add_directory(
            request.path,
            recursive=request.recursive,
            file_types=request.file_types
        )
        return {"success": True, "stats": stats}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/files/index")
async def index_file(path: str = Form(...)):
    """索引单个文件"""
    try:
        success = file_brain.add_file(path)
        
        if success:
            return {"success": True, "message": f"文件 {path} 已索引"}
        else:
            raise HTTPException(status_code=400, detail="文件索引失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 搜索功能 ====================

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """搜索内容"""
    try:
        if request.search_type == "keyword":
            results = file_brain.keyword_search(request.query, request.top_k)
        elif request.search_type == "hybrid":
            results = file_brain.hybrid_search(request.query, request.top_k)
        else:
            results = file_brain.search(request.query, request.top_k)
        
        # 转换为字典
        results_dict = []
        for r in results:
            results_dict.append({
                "content": r.content,
                "source": r.source,
                "file_type": r.file_type,
                "title": r.title,
                "score": r.score,
                "metadata": r.metadata,
                "context": r.context,
            })
        
        return SearchResponse(
            results=results_dict,
            total=len(results_dict),
            query=request.query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_get(q: str, top_k: int = 10, search_type: str = "semantic"):
    """搜索内容 (GET 方法)"""
    request = SearchRequest(query=q, top_k=top_k, search_type=search_type)
    return await search(request)


# ==================== Notion 集成 ====================

@app.post("/notion/connect")
async def connect_notion(request: NotionConnectRequest):
    """连接 Notion"""
    try:
        success = file_brain.connect_notion(request.api_key)
        
        if success:
            return {"success": True, "message": "Notion 连接成功"}
        else:
            raise HTTPException(status_code=400, detail="Notion 连接失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notion/index")
async def index_notion(request: NotionIndexRequest):
    """索引 Notion 内容"""
    try:
        if request.page_id:
            success = file_brain.index_notion_page(request.page_id)
            if success:
                return {"success": True, "message": f"页面 {request.page_id} 已索引"}
        
        elif request.database_id:
            stats = file_brain.index_notion_database(request.database_id)
            return {"success": True, "stats": stats}
        
        else:
            raise HTTPException(status_code=400, detail="需要提供 page_id 或 database_id")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notion/databases")
async def list_notion_databases():
    """列出 Notion 数据库"""
    try:
        databases = file_brain.list_notion_databases()
        return {"databases": databases}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Obsidian 集成 ====================

@app.post("/obsidian/connect")
async def connect_obsidian(request: ObsidianConnectRequest):
    """连接 Obsidian"""
    try:
        success = file_brain.connect_obsidian(request.vault_path)
        
        if success:
            return {"success": True, "message": "Obsidian 连接成功"}
        else:
            raise HTTPException(status_code=400, detail="Obsidian 连接失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/obsidian/index")
async def index_obsidian():
    """索引 Obsidian 知识库"""
    try:
        stats = file_brain.index_obsidian_vault()
        return {"success": True, "stats": stats}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/obsidian/graph")
async def get_obsidian_graph():
    """获取 Obsidian 知识图谱"""
    try:
        graph = file_brain.get_obsidian_graph()
        return graph
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 管理功能 ====================

@app.get("/sources")
async def list_sources():
    """列出所有已索引的来源"""
    try:
        sources = file_brain.list_sources()
        return {"sources": sources}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sources/{source:path}")
async def delete_source(source: str):
    """删除指定来源"""
    try:
        success = file_brain.delete_source(source)
        
        if success:
            return {"success": True, "message": f"来源 {source} 已删除"}
        else:
            raise HTTPException(status_code=404, detail="来源未找到")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sources/{source:path}/summary")
async def get_document_summary(source: str):
    """获取文档摘要"""
    try:
        summary = file_brain.get_document_summary(source)
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear-all")
async def clear_all():
    """清空所有索引"""
    try:
        success = file_brain.clear_all()
        
        if success:
            return {"success": True, "message": "所有索引已清空"}
        else:
            raise HTTPException(status_code=500, detail="清空失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 文件组织功能 ====================

@app.post("/organize/generate-filename")
async def generate_filename(request: FileRenameRequest):
    """为文件生成智能文件名"""
    try:
        filename = file_brain.generate_filename(request.path)
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/organize/rename")
async def rename_file(request: FileRenameRequest):
    """智能重命名文件"""
    try:
        new_path = file_brain.rename_file(request.path)
        return {"success": True, "new_path": new_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/organize/extract-tags")
async def extract_tags(request: TagExtractRequest):
    """从文件中提取标签"""
    try:
        tags = file_brain.extract_tags(request.path, top_n=request.top_n)
        return {"success": True, "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/organize/directory")
async def organize_directory(request: FileOrganizeRequest):
    """智能组织目录中的文件"""
    try:
        stats = file_brain.organize_files(request.path, recursive=request.recursive)
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 智能监控功能 ====================

@app.get("/smart-monitor/status")
async def get_smart_monitor_status():
    """获取智能监控状态"""
    try:
        return file_brain.get_smart_monitor_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/smart-monitor/search-history")
async def get_search_history(limit: int = 10):
    """获取搜索历史"""
    try:
        history = file_brain.get_search_history(limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/smart-monitor/monitored-files")
async def get_monitored_files():
    """获取监控文件"""
    try:
        files = file_brain.get_monitored_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/smart-monitor/config")
async def update_smart_monitor_config(request: SmartMonitorConfigRequest):
    """更新智能监控配置"""
    try:
        config_dict = request.model_dump(exclude_unset=True)
        success = file_brain.update_smart_monitor_config(config_dict)
        if success:
            return {"success": True, "message": "配置更新成功"}
        else:
            raise HTTPException(status_code=400, detail="配置更新失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 启动函数 ====================

def start_server():
    """启动服务器"""
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    start_server()
