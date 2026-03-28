"""
测试 PDF 文件读取
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from readers.pdf_reader import PDFReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def create_test_pdf(file_path):
    """创建测试 PDF 文件"""
    c = canvas.Canvas(str(file_path), pagesize=A4)
    c.setTitle("PDF 测试文档")
    c.setAuthor("File Brain")
    
    # 第一页
    c.drawString(100, 800, "PDF 测试文档")
    c.drawString(100, 750, "这是用于测试 File Brain PDF 读取功能的文档。")
    c.drawString(100, 700, "包含多页内容。")
    
    # 第二页
    c.showPage()
    c.drawString(100, 800, "第二页")
    c.drawString(100, 750, "这是第二页的内容。")
    
    c.save()
    print(f"[OK] 创建测试 PDF: {file_path}")


def test_pdf():
    """测试 PDF 读取"""
    print("=" * 60)
    print("测试 PDF 文件读取")
    print("=" * 60)
    
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    pdf_file = test_dir / "test.pdf"
    
    try:
        # 安装 reportlab 来创建 PDF
        from reportlab.pdfgen import canvas
        create_test_pdf(pdf_file)
    except ImportError:
        print("[SKIP] 需要安装 reportlab 来创建测试 PDF")
        print("       pip install reportlab")
        return None
    
    # 测试读取
    try:
        reader = PDFReader()
        content = reader.read(pdf_file)
        
        print(f"[OK] PDF 读取成功")
        print(f"    标题: {content.title}")
        print(f"    内容长度: {len(content.content)} 字符")
        print(f"    页数: {content.metadata.get('page_count', '未知')}")
        
        # 显示部分内容
        preview = content.content[:200].replace('\n', ' ')
        print(f"    内容预览: {preview}...")
        
        return True
    except Exception as e:
        print(f"[X] PDF 读取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf()
    sys.exit(0 if success else 1)
