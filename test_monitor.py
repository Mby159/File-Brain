"""
测试文件夹监控功能
"""
import sys
import time
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from file_brain import FileBrain


def test_monitor():
    """测试监控功能"""
    print("=" * 60)
    print("测试文件夹监控功能")
    print("=" * 60)
    
    fb = FileBrain()
    
    # 创建测试目录
    test_dir = Path(__file__).parent / "test_monitor_dir"
    test_dir.mkdir(exist_ok=True)
    
    print(f"\n1. 添加监控路径: {test_dir}")
    success = fb.watch_path(test_dir)
    print(f"   {'[OK]' if success else '[X]'} 监控添加{'成功' if success else '失败'}")
    
    print(f"\n2. 启动监控...")
    fb.start_watching()
    print(f"   [OK] 监控已启动")
    
    # 等待一下
    time.sleep(1)
    
    print(f"\n3. 创建测试文件...")
    test_file = test_dir / "monitored_test.txt"
    test_file.write_text("这是监控测试文件的内容。\nFile Brain 会自动索引这个文件。", encoding='utf-8')
    
    # 等待监控检测
    print(f"   等待监控检测...")
    time.sleep(2)
    
    print(f"\n4. 修改文件...")
    test_file.write_text("这是修改后的内容。\nFile Brain 应该会自动更新索引。", encoding='utf-8')
    
    # 等待监控检测
    print(f"   等待监控检测...")
    time.sleep(2)
    
    print(f"\n5. 检查来源列表...")
    sources = fb.list_sources()
    print(f"   已索引 {len(sources)} 个来源:")
    for source in sources:
        print(f"   - {source}")
    
    print(f"\n6. 停止监控...")
    fb.stop_watching()
    print(f"   [OK] 监控已停止")
    
    print(f"\n7. 测试搜索...")
    results = fb.search("监控测试", top_k=3)
    print(f"   找到 {len(results)} 个结果")
    for result in results:
        print(f"   - {result.title}: {result.content[:100]}...")
    
    print("\n" + "=" * 60)
    print("监控功能测试完成!")
    print("=" * 60)
    
    # 清理
    fb.clear_all()
    
    return True


if __name__ == "__main__":
    success = test_monitor()
    sys.exit(0 if success else 1)
