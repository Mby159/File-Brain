"""
测试API功能
"""
import sys
from pathlib import Path
import json
import requests

sys.path.insert(0, str(Path(__file__).parent))

BASE_URL = "http://localhost:8000"


def test_api_root():
    """测试根路径"""
    print("\n=== 测试根路径 ===")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print(f"响应: {data}")
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    print("[OK] 根路径测试通过")


def test_api_stats():
    """测试统计信息"""
    print("\n=== 测试统计信息 ===")
    response = requests.get(f"{BASE_URL}/stats")
    assert response.status_code == 200
    data = response.json()
    print(f"响应: {data}")
    assert "total_documents" in data
    print("[OK] 统计信息测试通过")


def test_api_sources():
    """测试来源列表"""
    print("\n=== 测试来源列表 ===")
    response = requests.get(f"{BASE_URL}/sources")
    assert response.status_code == 200
    data = response.json()
    print(f"响应: {data}")
    assert "sources" in data
    print("[OK] 来源列表测试通过")


def test_api_file_organize():
    """测试文件组织功能"""
    print("\n=== 测试文件组织功能 ===")
    
    # 测试提取标签
    test_file = Path(__file__).parent / "test_files" / "test.txt"
    test_file_path = str(test_file.absolute())
    
    # 提取标签
    print("\n测试提取标签:")
    payload = {"path": test_file_path, "top_n": 5}
    response = requests.post(f"{BASE_URL}/organize/extract-tags", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"响应: {data}")
    assert "success" in data
    assert "tags" in data
    print("[OK] 提取标签测试通过")
    
    # 测试生成文件名
    print("\n测试生成文件名:")
    payload = {"path": test_file_path}
    response = requests.post(f"{BASE_URL}/organize/generate-filename", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"响应: {data}")
    assert "success" in data
    assert "filename" in data
    print("[OK] 生成文件名测试通过")


def test_api_search():
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")
    payload = {"query": "测试", "top_k": 5, "search_type": "semantic"}
    response = requests.post(f"{BASE_URL}/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"响应: {data}")
    assert "results" in data
    assert "total" in data
    assert "query" in data
    print("[OK] 搜索功能测试通过")


def main():
    """主测试函数"""
    print("==================================================")
    print("测试API功能")
    print("==================================================")
    
    try:
        # 启动API服务器（在后台运行）
        import subprocess
        import time
        
        server_process = subprocess.Popen([
            sys.executable, "-c", 
            "from api.server import start_server; start_server()"
        ])
        
        # 等待服务器启动
        time.sleep(3)
        
        # 运行测试
        test_api_root()
        test_api_stats()
        test_api_sources()
        test_api_file_organize()
        test_api_search()
        
        print("\n==================================================")
        print("[OK] 所有API测试通过!")
        print("==================================================")
        
    finally:
        # 停止服务器
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()


if __name__ == "__main__":
    main()