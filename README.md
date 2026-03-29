# 🧠 File Brain

<p align="center">
  <strong>Intelligent Local File System Management Tool</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.104%2B-green" alt="FastAPI"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-1.28%2B-red" alt="Streamlit"></a>
</p>

<p align="center">
  <a href="README_CN.md">简体中文</a> | <strong>English</strong>
</p>

---

## 📝 Introduction

File Brain is a powerful local file system management tool that can read, index, intelligently search and organize various types of file content, with support for knowledge graph construction and multi-language processing.

### 🎯 Key Features

- 📄 **Multi-format Support** - Text, Office, PDF, HTML, Mind Maps
- 🔍 **Intelligent Search** - Semantic, keyword, and hybrid search
- 📁 **Smart Organization** - Auto-tagging and intelligent naming
- 🕸️ **Knowledge Graph** - File relationship analysis and visualization
- 🔄 **File Monitoring** - Real-time monitoring and auto-indexing
- 🌐 **API & Web UI** - RESTful API and interactive web interface
- 🐳 **Docker Support** - Easy deployment with Docker

## ✨ Features

### 📄 Supported File Types

| Type | Formats | Description |
|------|---------|-------------|
| **Text Files** | `.txt`, `.md`, `.rst` | Plain text, Markdown |
| **Office Documents** | `.docx`, `.pptx`, `.xlsx` | Word, PowerPoint, Excel |
| **PDF** | `.pdf` | PDF documents |
| **Web Pages** | `.html`, `.htm` | HTML files |
| **Mind Maps** | `.xmind`, `.mm`, `.opml` | XMind, FreeMind, OPML |

### 🔍 Search Capabilities

- **Semantic Search** - Intelligent search based on AI embedding vectors
- **Keyword Search** - Traditional keyword matching
- **Hybrid Search** - Combines the advantages of semantic and keyword search
- **Type Filtering** - Search only specific types of files

### 📁 Smart File Organization

- **Multi-language Tag Extraction** - Intelligently extract tags from file content, supporting Chinese, English, Japanese, etc.
- **Smart Filename Generation** - Generate meaningful filenames based on file content
- **Automatic File Renaming** - Automatically rename files to improve searchability
- **Directory File Organization** - Batch organize files in directories

### 🕸️ Knowledge Graph

- **File Association Analysis** - Automatically identify relationships between files
- **Central File Identification** - Find core files in the knowledge graph
- **Related File Recommendation** - Recommend related files based on similarity
- **Visualization Support** - Provide knowledge graph data for frontend visualization

### 🔄 File Monitoring

- **Real-time Monitoring** - Monitor file system changes
- **Automatic Indexing** - Automatically index new or modified files
- **Multiple Monitoring Modes** - Support for watchdog and polling modes

### 🌐 API Service

- **RESTful API** - RESTful interface based on FastAPI
- **Automatic Documentation** - Automatically generate API documentation
- **File Upload** - Support file upload and indexing
- **Batch Operations** - Support batch file processing

### 🖥️ Web Interface

- **Interactive Interface** - Visual interface based on Streamlit
- **File Management** - Intuitive file management features
- **Search Interface** - User-friendly search experience
- **Knowledge Graph Visualization** - Interactive knowledge graph display

### 🐳 Containerized Deployment

- **Docker Support** - Provides Dockerfile and docker-compose configuration
- **One-click Startup** - Simplified deployment and startup process
- **Environment Isolation** - Containerized runtime to avoid dependency conflicts

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional)

Create a `.env` file:

```env
# Notion API
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id

# Obsidian
OBSIDIAN_VAULT_PATH=/path/to/your/vault

# Google API (for NotebookLM)
GOOGLE_API_KEY=your_google_api_key
```

### 3. Start Interactive Mode

```bash
python main.py
```

### 4. Start API Server and Web Interface

```bash
python main.py --server
```

- **Web Interface**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

### 5. Docker Deployment

```bash
# Using startup script
bash start.sh

# Or use docker-compose directly
docker-compose up -d --build
```

## 📖 User Guide

### Interactive Mode Commands

```
file-brain> index <path>        # Index file or directory
file-brain> search <query>      # Search content
file-brain> stats               # Show statistics
file-brain> sources             # List all sources
file-brain> clear               # Clear all indexes
file-brain> help                # Show help
file-brain> quit                # Exit
```

### Command Line Usage

```bash
# Index file
python main.py --index ./my-document.docx

# Index directory
python main.py --index ./my-documents/

# Search
python main.py --search "artificial intelligence"

# Show statistics
python main.py --stats

# Start server
python main.py --server
```

### API Usage Examples

```python
import requests

# Upload and index file
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/files/upload',
        files={'file': f}
    )

# Search
response = requests.post(
    'http://localhost:8000/search',
    json={'query': 'artificial intelligence', 'limit': 5}
)
results = response.json()

# Extract file tags
response = requests.post(
    'http://localhost:8000/organize/extract-tags',
    json={'content': 'Python is a high-level programming language'}
)
tags = response.json()['tags']

# Generate filename
response = requests.post(
    'http://localhost:8000/organize/generate-filename',
    json={'content': 'Python is a high-level programming language'}
)
filename = response.json()['filename']

# Organize directory
response = requests.post(
    'http://localhost:8000/organize/directory',
    json={'directory': './my-documents/'}
)
result = response.json()

# Get knowledge graph
response = requests.get('http://localhost:8000/knowledge-graph')
graph = response.json()
```

## 🏗️ Project Structure

```
file-brain/
├── ai/                      # AI related modules
│   ├── ai_provider.py       # AI service provider
│   └── qa_engine.py         # Q&A engine
├── api/                     # API interface
│   └── server.py            # FastAPI service
├── core/                    # Core modules
│   ├── embedding/           # Embedding models
│   ├── file_organizer/      # File organization
│   ├── knowledge_graph/     # Knowledge graph
│   ├── content_indexer.py   # Content indexer
│   ├── file_reader.py       # File reader base class
│   └── search_engine.py     # Search engine
├── monitor/                 # File monitoring
│   └── file_monitor.py      # File monitor
├── readers/                 # File readers
│   ├── external/            # External service readers
│   ├── office/              # Office document readers
│   ├── others/              # Other file readers
│   └── text/                # Text file readers
├── web/                     # Web interface
│   └── app.py               # Streamlit application
├── file_brain.py            # Main controller
├── main.py                  # Entry file
├── config.py                # Configuration file
├── requirements.txt         # Dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── start.sh                 # Startup script
```

## 🔧 Advanced Configuration

### Vector Model

By default uses `sentence-transformers/all-MiniLM-L6-v2`, can be modified in `config.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500        # Chunk size
CHUNK_OVERLAP = 50      # Chunk overlap
```

### File Monitoring Configuration

```python
# Monitoring mode: 'watchdog' or 'polling'
MONITOR_MODE = 'watchdog'
# Monitoring interval (only for polling mode)
MONITOR_INTERVAL = 5  # seconds
```

### Adding Support for New File Types

1. Create a new reader class in the `readers/` directory
2. Inherit from `BaseFileReader`
3. Implement the `read()` method
4. Add extension mapping in `config.py`'s `SUPPORTED_EXTENSIONS`
5. Register the reader in `readers/__init__.py`'s `READER_MAP`

## 📋 Dependencies

Main dependencies:
- **FastAPI** - Web API framework
- **uvicorn** - ASGI server
- **python-multipart** - Form data processing
- **scikit-learn** - Machine learning library (for TF-IDF)
- **sentence-transformers** - Text embedding model
- **NetworkX** - Knowledge graph construction
- **python-docx** - Word document reading
- **python-pptx** - PowerPoint reading
- **openpyxl** - Excel reading
- **PyPDF2/pdfplumber** - PDF reading
- **beautifulsoup4** - HTML parsing
- **watchdog** - File monitoring
- **xmindparser** - Mind map parsing
- **notion-client** - Notion API
- **requests** - HTTP requests
- **streamlit** - Web interface
- **numpy** - Numerical computing

## 🤝 Contributing

Issues and Pull Requests are welcome!

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## 📄 License

MIT License

---

<p align="center">
  Made with ❤️ by Mby159
</p>