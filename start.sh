#!/bin/bash

# File Brain 启动脚本
echo "===================================="
echo "🧠 File Brain 启动脚本"
echo "===================================="

# 检查是否安装了Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装Docker，请先安装Docker"
    exit 1
fi

# 检查是否安装了docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未安装docker-compose，请先安装docker-compose"
    exit 1
fi

# 构建并启动服务
echo "正在构建并启动File Brain服务..."
docker-compose up -d --build

# 检查服务状态
echo "正在检查服务状态..."
sleep 5
docker-compose ps

echo "===================================="
echo "File Brain服务已启动"
echo "===================================="
echo "Web界面: http://localhost:8501"
echo "API文档: http://localhost:8000/docs"
echo "===================================="
echo "使用 'docker-compose down' 停止服务"
echo "===================================="
