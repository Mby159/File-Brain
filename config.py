"""
File Brain 配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 基础路径
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_PATH = DATA_DIR / "vector_db"
UPLOAD_DIR = DATA_DIR / "uploads"

# 创建必要的目录
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_PATH.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# API Keys
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

# Obsidian 配置
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")

# NotebookLM (通过 Google AI Studio)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ============================================
# AI 配置（默认：无 AI，完全离线）
# ============================================
# AI_PROVIDER 可选值:
# - "none" : 无 AI（完全离线，默认）
# - "ollama" : 使用 Ollama 本地模型（需安装 Ollama）
# - "lmstudio" : 使用 LM Studio（需启动 LM Studio 服务器）
# - "local" : 使用本地 transformers 小模型（首次需联网下载）
# - "openai" : 使用 OpenAI API（需密钥，数据发送到 OpenAI）
AI_PROVIDER = os.getenv("AI_PROVIDER", "none")

# Ollama 配置
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# LM Studio 配置
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")

# 本地 Transformers 配置
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# ============================================
# 向量模型配置
# ============================================
# 可选值:
# - "tfidf" : 使用 TF-IDF (完全离线，基于关键词)
# - "sentence-transformers" : 使用 AI 嵌入模型 (首次需联网下载)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "tfidf")

# 当使用 sentence-transformers 时的具体模型
SENTENCE_TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# 支持的文件类型
SUPPORTED_EXTENSIONS = {
    # 文本文件
    ".txt": "text",
    ".md": "markdown",
    ".markdown": "markdown",
    ".rst": "text",
    
    # Office 文档
    ".docx": "word",
    ".doc": "word",
    ".pptx": "powerpoint",
    ".ppt": "powerpoint",
    ".xlsx": "excel",
    ".xls": "excel",
    
    # PDF
    ".pdf": "pdf",
    
    # HTML
    ".html": "html",
    ".htm": "html",
    
    # 思维导图
    ".xmind": "mindmap",
    ".mm": "mindmap",
    ".opml": "mindmap",
}

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000
