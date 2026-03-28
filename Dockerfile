# File Brain Dockerfile
# 使用官方Python镜像作为基础
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装额外的系统依赖（用于PDF处理等）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 暴露端口
EXPOSE 8000 8501

# 设置环境变量
ENV HOST=0.0.0.0
ENV PORT=8000

# 启动命令
CMD ["sh", "-c", "python -m streamlit run web/app.py --server.headless true --server.port 8501 & python main.py --server"]