# 🧠 File Brain - 本地文件系统智能管理工具

File Brain 是一个强大的本地文件系统管理工具，可以读取、索引、智能搜索和组织各种类型的文件内容，支持知识图谱构建和多语言处理。

## ✨ 功能特性

### 📄 支持的文件类型

| 类型 | 格式 | 说明 |
|------|------|------|
| **文本文件** | `.txt`, `.md`, `.rst` | 纯文本、Markdown |
| **Office 文档** | `.docx`, `.pptx`, `.xlsx` | Word、PowerPoint、Excel |
| **PDF** | `.pdf` | PDF 文档 |
| **网页** | `.html`, `.htm` | HTML 文件 |
| **思维导图** | `.xmind`, `.mm`, `.opml` | XMind、FreeMind、OPML |

### 🔍 搜索功能

- **语义搜索** - 基于 AI 嵌入向量的智能搜索
- **关键词搜索** - 传统的关键词匹配
- **混合搜索** - 结合语义和关键词的优势
- **按类型过滤** - 只搜索特定类型的文件

### 📁 智能文件组织

- **多语言标签提取** - 从文件内容中智能提取标签，支持中文、英文、日文等
- **智能文件名生成** - 基于文件内容生成有意义的文件名
- **文件自动重命名** - 自动重命名文件以提高可搜索性
- **目录文件组织** - 批量组织目录中的文件

### 🕸️ 知识图谱

- **文件关联分析** - 自动识别文件间的关联关系
- **中心文件识别** - 找出知识图谱中的核心文件
- **相关文件推荐** - 基于相似度推荐相关文件
- **可视化支持** - 提供知识图谱数据，支持前端可视化

### 🔄 文件监控

- **实时监控** - 监控文件系统变化
- **自动索引** - 新文件或修改文件自动索引
- **多种监控模式** - 支持 watchdog 和 polling 模式

### 🌐 API 服务

- **RESTful API** - 基于 FastAPI 的 RESTful 接口
- **自动文档** - 自动生成 API 文档
- **文件上传** - 支持文件上传和索引
- **批量操作** - 支持批量文件处理

### 🖥️ Web 界面

- **交互式界面** - 基于 Streamlit 的可视化界面
- **文件管理** - 直观的文件管理功能
- **搜索界面** - 友好的搜索体验
- **知识图谱可视化** - 交互式知识图谱展示

### 🐳 容器化部署

- **Docker 支持** - 提供 Dockerfile 和 docker-compose 配置
- **一键启动** - 简化部署和启动过程
- **环境隔离** - 容器化运行，避免依赖冲突

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

创建 `.env` 文件：

```env
# Notion API
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id

# Obsidian
OBSIDIAN_VAULT_PATH=C:\Users\YourName\Documents\Obsidian Vault

# Google API (for NotebookLM)
GOOGLE_API_KEY=your_google_api_key
```

### 3. 启动交互模式

```bash
python main.py
```

### 4. 启动 API 服务器和 Web 界面

```bash
python main.py --server
```

- **Web 界面**：http://localhost:8501
- **API 文档**：http://localhost:8000/docs

### 5. Docker 部署

```bash
# 使用启动脚本
bash start.sh

# 或直接使用 docker-compose
docker-compose up -d --build
```

## 📖 使用指南

### 交互模式命令

```
file-brain> index <路径>        # 索引文件或目录
file-brain> search <查询>       # 搜索内容
file-brain> stats               # 显示统计信息
file-brain> sources             # 列出所有来源
file-brain> clear               # 清空所有索引
file-brain> help                # 显示帮助
file-brain> quit                # 退出
```

### 命令行使用

```bash
# 索引文件
python main.py --index ./my-document.docx

# 索引目录
python main.py --index ./my-documents/

# 搜索
python main.py --search "人工智能"

# 显示统计
python main.py --stats

# 启动服务器
python main.py --server
```

### API 使用示例

```python
import requests

# 上传并索引文件
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/files/upload',
        files={'file': f}
    )

# 搜索
response = requests.post(
    'http://localhost:8000/search',
    json={'query': '人工智能', 'limit': 5}
)
results = response.json()

# 提取文件标签
response = requests.post(
    'http://localhost:8000/organize/extract-tags',
    json={'content': 'Python是一种高级编程语言'}
)
tags = response.json()['tags']

# 生成文件名
response = requests.post(
    'http://localhost:8000/organize/generate-filename',
    json={'content': 'Python是一种高级编程语言'}
)
filename = response.json()['filename']

# 组织目录
response = requests.post(
    'http://localhost:8000/organize/directory',
    json={'directory': './my-documents/'}
)
result = response.json()

# 获取知识图谱
response = requests.get('http://localhost:8000/knowledge-graph')
graph = response.json()
```

## 🏗️ 项目结构

```
file-brain/
├── ai/                      # AI 相关模块
│   ├── ai_provider.py       # AI 服务提供者
│   └── qa_engine.py         # 问答引擎
├── api/                     # API 接口
│   └── server.py            # FastAPI 服务
├── core/                    # 核心模块
│   ├── embedding/           # 嵌入模型
│   │   ├── base.py          # 基础嵌入类
│   │   ├── sentence_transformers.py # Sentence Transformers 模型
│   │   └── tfidf.py         # TF-IDF 模型
│   ├── file_organizer/      # 文件组织
│   │   ├── file_namer.py    # 文件命名器
│   │   └── tag_extractor.py # 标签提取器
│   ├── knowledge_graph/     # 知识图谱
│   │   ├── graph_builder.py # 图谱构建器
│   │   ├── graph_storage.py # 图谱存储
│   │   └── graph_visualizer.py # 图谱可视化
│   ├── models/              # 数据模型
│   │   └── file_content.py  # 文件内容模型
│   ├── content_indexer.py   # 内容索引器
│   ├── file_reader.py       # 文件读取基类
│   └── search_engine.py     # 搜索引擎
├── monitor/                 # 文件监控
│   └── file_monitor.py      # 文件监控器
├── readers/                 # 文件读取器
│   ├── external/            # 外部服务读取器
│   │   ├── notion_reader.py # Notion 读取器
│   │   └── obsidian_reader.py # Obsidian 读取器
│   ├── office/              # Office 文档读取器
│   │   ├── excel_reader.py  # Excel 读取器
│   │   ├── ppt_reader.py    # PowerPoint 读取器
│   │   └── word_reader.py   # Word 读取器
│   ├── others/              # 其他文件读取器
│   │   ├── html_reader.py   # HTML 读取器
│   │   ├── mindmap_reader.py # 思维导图读取器
│   │   └── pdf_reader.py    # PDF 读取器
│   └── text/                # 文本文件读取器
│       ├── markdown_reader.py # Markdown 读取器
│       └── text_reader.py   # 文本读取器
├── web/                     # Web 界面
│   └── app.py               # Streamlit 应用
├── file_brain.py            # 主控制器
├── main.py                  # 入口文件
├── config.py                # 配置文件
├── requirements.txt         # 依赖
├── Dockerfile               # Docker 配置
├── docker-compose.yml       # Docker Compose 配置
└── start.sh                 # 启动脚本
```

## 🔧 高级配置

### 向量模型

默认使用 `sentence-transformers/all-MiniLM-L6-v2`，可以在 `config.py` 中修改：

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500        # 分块大小
CHUNK_OVERLAP = 50      # 分块重叠
```

### 文件监控配置

```python
# 监控模式: 'watchdog' 或 'polling'
MONITOR_MODE = 'watchdog'
# 监控间隔（仅用于 polling 模式）
MONITOR_INTERVAL = 5  # 秒
```

### 添加新的文件类型支持

1. 在 `readers/` 目录创建新的读取器类
2. 继承 `BaseFileReader`
3. 实现 `read()` 方法
4. 在 `config.py` 的 `SUPPORTED_EXTENSIONS` 中添加扩展名映射
5. 在 `readers/__init__.py` 的 `READER_MAP` 中注册读取器

## 📋 依赖说明

主要依赖：
- **FastAPI** - Web API 框架
- **uvicorn** - ASGI 服务器
- **python-multipart** - 表单数据处理
- **scikit-learn** - 机器学习库（用于 TF-IDF）
- **sentence-transformers** - 文本嵌入模型
- **NetworkX** - 知识图谱构建
- **python-docx** - Word 文档读取
- **python-pptx** - PowerPoint 读取
- **openpyxl** - Excel 读取
- **PyPDF2/pdfplumber** - PDF 读取
- **beautifulsoup4** - HTML 解析
- **watchdog** - 文件监控
- **xmindparser** - 思维导图解析
- **notion-client** - Notion API
- **requests** - HTTP 请求
- **streamlit** - Web 界面
- **numpy** - 数值计算

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 📄 许可证

MIT License
