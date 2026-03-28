"""
测试知识图谱功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from file_brain import FileBrain


def test_knowledge_graph():
    """测试知识图谱功能"""
    print("=" * 60)
    print("测试知识图谱功能")
    print("=" * 60)
    
    fb = FileBrain()
    
    # 创建测试文件
    test_files = []
    for i in range(3):
        test_file = Path(__file__).parent / f"test_knowledge_{i}.txt"
        test_file.write_text(f"这是测试文件 {i} 的内容。\n主题是知识图谱和文件管理。", encoding='utf-8')
        test_files.append(test_file)
    
    # 索引文件
    print("\n1. 索引测试文件...")
    for test_file in test_files:
        success = fb.add_file(test_file)
        print(f"   {'[OK]' if success else '[X]'} 索引文件: {test_file.name}")
    
    # 测试知识图谱统计
    print("\n2. 知识图谱统计...")
    stats = fb.get_knowledge_graph_stats()
    print(f"   节点数: {stats['nodes']}")
    print(f"   边数: {stats['edges']}")
    print(f"   密度: {stats['density']:.4f}")
    
    # 测试获取相关文件
    print("\n3. 获取相关文件...")
    if test_files:
        related = fb.get_related_files(test_files[0])
        print(f"   与 {test_files[0].name} 相关的文件:")
        for item in related:
            print(f"   - {Path(item['file_path']).name}: 相似度 {item['similarity']:.4f}")
    
    # 测试获取中心文件
    print("\n4. 获取中心文件...")
    central_files = fb.get_central_files()
    print(f"   知识图谱中心文件:")
    for item in central_files:
        print(f"   - {Path(item['file_path']).name}: 中心度 {item['centrality']:.4f}")
    
    # 测试获取知识图谱数据
    print("\n5. 获取知识图谱数据...")
    graph_data = fb.get_knowledge_graph()
    print(f"   节点数: {len(graph_data['nodes'])}")
    print(f"   边数: {len(graph_data['edges'])}")
    
    # 清理
    print("\n6. 清理测试文件...")
    for test_file in test_files:
        if test_file.exists():
            test_file.unlink()
    
    fb.clear_all()
    print("   [OK] 清理完成")
    
    print("\n" + "=" * 60)
    print("知识图谱功能测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_knowledge_graph()
    sys.exit(0)
