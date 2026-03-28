"""
基础测试脚本 - 验证 File Brain 核心功能
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 使用简单的 ASCII 字符
CHECK = "[OK]"
CROSS = "[X]"


def test_imports():
    """测试所有模块是否能正确导入"""
    print("=" * 50)
    print("测试模块导入...")
    print("=" * 50)
    
    try:
        from config import SUPPORTED_EXTENSIONS
        print(f"{CHECK} config 模块导入成功")
        print(f"  支持的文件类型: {list(SUPPORTED_EXTENSIONS.keys())}")
    except Exception as e:
        print(f"{CROSS} config 模块导入失败: {e}")
        return False
    
    try:
        from core.file_reader import BaseFileReader, FileContent
        print(f"{CHECK} core.file_reader 模块导入成功")
    except Exception as e:
        print(f"{CROSS} core.file_reader 模块导入失败: {e}")
        return False
    
    try:
        from core.content_indexer import ContentIndexer
        print(f"{CHECK} core.content_indexer 模块导入成功")
    except Exception as e:
        print(f"{CROSS} core.content_indexer 模块导入失败: {e}")
        return False
    
    try:
        from core.search_engine import SearchEngine
        print(f"{CHECK} core.search_engine 模块导入成功")
    except Exception as e:
        print(f"{CROSS} core.search_engine 模块导入失败: {e}")
        return False
    
    try:
        from readers import get_reader_for_file
        print(f"{CHECK} readers 模块导入成功")
    except Exception as e:
        print(f"{CROSS} readers 模块导入失败: {e}")
        return False
    
    try:
        from file_brain import FileBrain
        print(f"{CHECK} file_brain 模块导入成功")
    except Exception as e:
        print(f"{CROSS} file_brain 模块导入失败: {e}")
        return False
    
    print("\n所有模块导入成功!")
    return True


def test_text_reader():
    """测试文本读取器"""
    print("\n" + "=" * 50)
    print("测试文本读取器...")
    print("=" * 50)
    
    from readers.text_reader import TextReader, MarkdownReader
    
    # 创建测试文件
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    # 测试纯文本
    test_txt = test_dir / "test.txt"
    test_txt.write_text("这是一个测试文本文件。\nFile Brain 可以读取这个文件。", encoding='utf-8')
    
    reader = TextReader()
    content = reader.read(test_txt)
    
    print(f"{CHECK} 读取文本文件成功")
    print(f"  标题: {content.title}")
    print(f"  内容长度: {len(content.content)} 字符")
    print(f"  分块数: {len(content.chunks)}")
    
    # 测试 Markdown
    test_md = test_dir / "test.md"
    test_md.write_text("""---
title: 测试文档
tags: [test, markdown]
---

# 测试标题

这是 Markdown 测试文件的内容。

## 第二节

- 列表项 1
- 列表项 2
- 列表项 3
""", encoding='utf-8')
    
    reader = MarkdownReader()
    content = reader.read(test_md)
    
    print(f"{CHECK} 读取 Markdown 文件成功")
    print(f"  标题: {content.title}")
    print(f"  标签: {content.metadata.get('tags', [])}")
    print(f"  内容长度: {len(content.content)} 字符")
    
    return True


def test_indexer():
    """测试索引器"""
    print("\n" + "=" * 50)
    print("测试索引器...")
    print("=" * 50)
    
    from core.content_indexer import ContentIndexer
    from core.file_reader import FileContent
    
    indexer = ContentIndexer(collection_name="test_collection")
    
    # 创建测试内容
    test_content = FileContent(
        source="test://document1",
        content="人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
        file_type="text",
        title="人工智能介绍",
    )
    test_content.chunks = [test_content.content]
    test_content.file_hash = "test_hash_1"
    
    # 索引内容
    success = indexer.index_content(test_content)
    print(f"{CHECK if success else CROSS} 索引内容{'成功' if success else '失败'}")
    
    # 添加更多测试内容
    test_content2 = FileContent(
        source="test://document2",
        content="机器学习是人工智能的一个子集，它使用算法和统计模型来让计算机系统从数据中学习和改进。",
        file_type="text",
        title="机器学习介绍",
    )
    test_content2.chunks = [test_content2.content]
    test_content2.file_hash = "test_hash_2"
    
    success = indexer.index_content(test_content2)
    print(f"{CHECK if success else CROSS} 索引第二个内容{'成功' if success else '失败'}")
    
    # 测试搜索
    print("\n测试搜索功能...")
    results = indexer.search("人工智能", top_k=5)
    print(f"搜索 '人工智能' 找到 {len(results)} 个结果")
    
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result['metadata']['title']} (相关度: {result['score']:.2%})")
    
    # 测试统计
    stats = indexer.get_stats()
    print(f"\n索引统计: {stats}")
    
    # 清空测试索引
    indexer.clear_all()
    print(f"{CHECK} 清空索引成功")
    
    return True


def test_file_brain():
    """测试 FileBrain 主类"""
    print("\n" + "=" * 50)
    print("测试 FileBrain 主类...")
    print("=" * 50)
    
    from file_brain import FileBrain
    
    fb = FileBrain()
    
    # 创建测试目录和文件
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    # 创建多个测试文件
    for i in range(3):
        test_file = test_dir / f"test_{i}.txt"
        test_file.write_text(f"这是测试文件 {i} 的内容。\n包含一些关于 Python 编程的信息。", encoding='utf-8')
    
    # 索引目录
    stats = fb.add_directory(test_dir, recursive=False)
    print(f"{CHECK} 目录索引完成: {stats}")
    
    # 测试搜索
    print("\n测试搜索...")
    results = fb.search("Python 编程", top_k=5)
    print(f"搜索 'Python 编程' 找到 {len(results)} 个结果")
    
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result.title} (相关度: {result.score:.2%})")
    
    # 获取统计
    stats = fb.get_stats()
    print(f"\n系统统计: {stats}")
    
    # 列出来源
    sources = fb.list_sources()
    print(f"\n已索引的来源 ({len(sources)} 个):")
    for source in sources:
        print(f"  - {source}")
    
    # 清空
    fb.clear_all()
    print(f"\n{CHECK} 清空所有索引")
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("File Brain 基础测试")
    print("=" * 50)
    
    all_passed = True
    
    # 运行测试
    tests = [
        ("模块导入", test_imports),
        ("文本读取器", test_text_reader),
        ("索引器", test_indexer),
        ("FileBrain 主类", test_file_brain),
    ]
    
    for name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"\n{CROSS} {name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print(f"{CHECK} 所有测试通过!")
    else:
        print(f"{CROSS} 部分测试失败")
    print("=" * 50)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
