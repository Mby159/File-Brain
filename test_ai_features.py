"""
测试 AI 功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from file_brain import FileBrain
from config import AI_PROVIDER


def test_ai_features():
    """测试 AI 功能"""
    print("=" * 60)
    print("测试 AI 功能")
    print("=" * 60)
    
    fb = FileBrain()
    
    # 1. 测试 AI 状态
    print("\n1. 获取 AI 状态...")
    status = fb.get_ai_status()
    print(f"   AI 提供方: {status['provider']}")
    print(f"   可用: {status['available']}")
    print(f"   AI 已启用: {status['ai_enabled']}")
    
    # 2. 创建测试文档
    print("\n2. 创建测试文档...")
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "ai_test.txt"
    test_file.write_text("""File Brain 是一个本地文件系统智能搜索工具。
它支持多种文件格式，包括 Word、Excel、PowerPoint、PDF、HTML 等。
它还支持 Notion、Obsidian 等第三方服务。
搜索时使用 TF-IDF 或 AI 嵌入模型。
问答功能可以基于索引内容回答问题。
""", encoding='utf-8')
    
    # 3. 索引文档
    print("\n3. 索引测试文档...")
    success = fb.add_file(test_file)
    print(f"   索引{'成功' if success else '失败'}")
    
    # 4. 测试搜索
    print("\n4. 测试搜索...")
    results = fb.search("文件格式", top_k=3)
    print(f"   找到 {len(results)} 个结果")
    for r in results:
        print(f"   - {r.title}: {r.content[:80]}...")
    
    # 5. 测试 AI 问答
    print("\n5. 测试 AI 问答...")
    result = fb.ask("File Brain 支持哪些功能？", top_k=3)
    print(f"\n回答:")
    print("  " + result['answer'].replace('\n', '\n  '))
    print(f"\nAI 提供方: {result['ai_provider']}")
    print(f"成功: {result['success']}")
    
    if result['sources']:
        print(f"\n参考来源 ({len(result['sources'])}):")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source['title']} (相关度: {source['relevance']:.2%})")
    
    print("\n" + "=" * 60)
    print("AI 功能测试完成!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_ai_features()
    sys.exit(0 if success else 1)
