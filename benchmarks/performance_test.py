"""
性能基准测试
测量文件索引速度和内存使用情况
"""
import time
import os
import sys
from pathlib import Path
import psutil

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from file_brain import FileBrain


def create_test_files(directory: Path, count: int = 1000):
    """创建测试文件"""
    directory.mkdir(exist_ok=True)
    
    for i in range(count):
        file_path = directory / f"test_file_{i}.txt"
        content = f"这是测试文件 {i} 的内容。\n包含一些测试文本，用于性能基准测试。\n" * 10
        file_path.write_text(content, encoding='utf-8')
    
    return directory


def measure_memory():
    """测量当前内存使用情况"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB


def run_performance_test(file_count: int = 1000):
    """运行性能测试"""
    print(f"=== 性能基准测试: 索引 {file_count} 个文件 ===")
    
    # 创建测试目录
    test_dir = Path(__file__).parent / "test_files"
    test_dir = create_test_files(test_dir, file_count)
    
    # 初始化 FileBrain
    fb = FileBrain()
    
    # 测量内存使用
    initial_memory = measure_memory()
    print(f"初始内存使用: {initial_memory:.2f} MB")
    
    # 开始计时
    start_time = time.time()
    
    # 索引文件
    print("开始索引...")
    stats = fb.add_directory(test_dir, recursive=False)
    
    # 结束计时
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 测量内存使用
    final_memory = measure_memory()
    memory_used = final_memory - initial_memory
    
    # 输出结果
    print(f"\n=== 测试结果 ===")
    print(f"索引 {file_count} 个文件耗时: {elapsed_time:.2f} 秒")
    print(f"平均每个文件耗时: {elapsed_time / file_count:.3f} 秒")
    print(f"内存使用: {final_memory:.2f} MB")
    print(f"内存增长: {memory_used:.2f} MB")
    print(f"索引统计: {stats}")
    
    # 清空索引
    fb.clear_all()
    print("\n索引已清空")
    
    return {
        'file_count': file_count,
        'elapsed_time': elapsed_time,
        'memory_used': memory_used,
        'stats': stats
    }


if __name__ == "__main__":
    # 运行测试
    result = run_performance_test()
    
    # 可选：测试不同文件数量
    # for count in [100, 500, 1000, 2000]:
    #     print(f"\n" + "=" * 60)
    #     run_performance_test(count)
    #     print("=" * 60)
