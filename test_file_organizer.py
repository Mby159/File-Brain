"""
测试文件组织功能
"""
import os
import tempfile
from pathlib import Path

from core.file_organizer import FileNamer, TagExtractor
from core.models import FileContent


def test_tag_extractor():
    """测试标签提取器"""
    print("\n=== 测试标签提取器 ===")
    
    # 创建测试内容
    test_content = "Python 是一种高级编程语言，被广泛应用于数据科学、Web开发和人工智能领域。"
    file_content = FileContent(
        source="test.txt",
        content=test_content,
        file_type="text"
    )
    
    # 提取标签
    extractor = TagExtractor()
    tags = extractor.extract_tags(file_content, top_n=5)
    
    print(f"提取的标签: {tags}")
    assert len(tags) > 0, "标签提取失败"
    print("[OK] 标签提取成功")


def test_file_namer():
    """测试文件命名器"""
    print("\n=== 测试文件命名器 ===")
    
    # 创建测试内容
    test_content = "Python 是一种高级编程语言，被广泛应用于数据科学、Web开发和人工智能领域。"
    file_content = FileContent(
        source="test.txt",
        content=test_content,
        file_type="text"
    )
    
    # 生成文件名
    namer = FileNamer()
    filename = namer.generate_filename(file_content)
    
    print(f"生成的文件名: {filename}")
    assert len(filename) > 0, "文件名生成失败"
    assert ".txt" in filename, "文件扩展名添加失败"
    print("[OK] 文件名生成成功")


def test_file_rename():
    """测试文件重命名"""
    print("\n=== 测试文件重命名 ===")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write("Python 是一种高级编程语言，被广泛应用于数据科学、Web开发和人工智能领域。".encode('utf-8'))
        temp_file_path = f.name
    
    try:
        # 创建文件内容对象
        file_content = FileContent(
            source=temp_file_path,
            content="Python 是一种高级编程语言，被广泛应用于数据科学、Web开发和人工智能领域。",
            file_type="text"
        )
        
        # 重命名文件
        namer = FileNamer()
        new_path = namer.rename_file(temp_file_path, file_content)
        
        print(f"原路径: {temp_file_path}")
        print(f"新路径: {new_path}")
        assert new_path != temp_file_path, "文件重命名失败"
        assert os.path.exists(new_path), "新文件不存在"
        print("[OK] 文件重命名成功")
        
    finally:
        # 清理文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if 'new_path' in locals() and os.path.exists(new_path):
            os.remove(new_path)


def test_empty_content():
    """测试空内容"""
    print("\n=== 测试空内容 ===")
    
    # 创建空内容
    file_content = FileContent(
        source="empty.txt",
        content="",
        file_type="text"
    )
    
    # 提取标签
    extractor = TagExtractor()
    tags = extractor.extract_tags(file_content)
    assert len(tags) == 0, "空内容应该返回空标签列表"
    print("[OK] 空内容标签提取成功")
    
    # 生成文件名
    namer = FileNamer()
    filename = namer.generate_filename(file_content)
    assert len(filename) > 0, "空内容应该生成默认文件名"
    print(f"空内容生成的文件名: {filename}")
    print("[OK] 空内容文件名生成成功")


def test_multi_language():
    """测试多语言支持"""
    print("\n=== 测试多语言支持 ===")
    
    # 测试英文
    print("\n测试英文:")
    en_content = "Python is a high-level programming language widely used in data science, web development, and artificial intelligence."
    en_file_content = FileContent(
        source="en_test.txt",
        content=en_content,
        file_type="text"
    )
    extractor = TagExtractor()
    en_tags = extractor.extract_tags(en_file_content, top_n=5)
    print(f"英文标签: {en_tags}")
    assert len(en_tags) > 0, "英文标签提取失败"
    print("[OK] 英文标签提取成功")
    
    # 测试中文
    print("\n测试中文:")
    zh_content = "Python 是一种高级编程语言，被广泛应用于数据科学、Web开发和人工智能领域。"
    zh_file_content = FileContent(
        source="zh_test.txt",
        content=zh_content,
        file_type="text"
    )
    zh_tags = extractor.extract_tags(zh_file_content, top_n=5)
    print(f"中文标签: {zh_tags}")
    assert len(zh_tags) > 0, "中文标签提取失败"
    print("[OK] 中文标签提取成功")
    
    # 测试日文
    print("\n测试日文:")
    ja_content = "Pythonは、データサイエンス、Web開発、人工知能の分野で広く使用されている高級プログラミング言語です。"
    ja_file_content = FileContent(
        source="ja_test.txt",
        content=ja_content,
        file_type="text"
    )
    ja_tags = extractor.extract_tags(ja_file_content, top_n=5)
    print(f"日文标签: {ja_tags}")
    assert len(ja_tags) > 0, "日文标签提取失败"
    print("[OK] 日文标签提取成功")


if __name__ == "__main__":
    print("==================================================")
    print("测试文件组织功能")
    print("==================================================")
    
    test_tag_extractor()
    test_file_namer()
    test_file_rename()
    test_empty_content()
    test_multi_language()
    
    print("\n==================================================")
    print("[OK] 所有测试通过!")
    print("==================================================")