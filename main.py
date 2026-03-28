"""
File Brain - 主入口
"""
import argparse
import sys
from pathlib import Path

# 确保可以导入本地模块
sys.path.insert(0, str(Path(__file__).parent))

from file_brain import FileBrain


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║               File Brain                  ║
    ║        本地文件系统智能搜索工具           ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    try:
        print(banner)
    except UnicodeEncodeError:
        # 移除可能导致编码问题的字符
        banner = banner.replace('╔', '').replace('╗', '').replace('║', '').replace('╚', '').replace('╝', '').replace('═', '-')
        print(banner)


def interactive_mode():
    """交互模式"""
    print_banner()
    
    fb = FileBrain()
    
    print("命令列表:")
    print("  index <路径>     - 索引文件或目录")
    print("  search <查询>    - 搜索内容")
    print("  ask <问题>       - AI 问答（基于索引内容）")
    print("  ai-status        - 显示 AI 状态")
    print("  watch <路径>     - 开始监控路径")
    print("  unwatch <路径>   - 停止监控路径")
    print("  watch-start      - 启动监控")
    print("  watch-stop       - 停止监控")
    print("  watch-list       - 列出监控路径")
    print("  stats            - 显示统计信息")
    print("  sources          - 列出所有来源")
    print("  clear            - 清空所有索引")
    print("  help             - 显示帮助")
    print("  quit             - 退出")
    print()
    
    while True:
        try:
            command = input("file-brain> ").strip()
            
            if not command:
                continue
            
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == "quit" or cmd == "exit":
                print("再见!")
                break
            
            elif cmd == "help":
                print("命令列表:")
                print("  index <路径>     - 索引文件或目录")
                print("  search <查询>    - 搜索内容")
                print("  ask <问题>       - AI 问答（基于索引内容）")
                print("  ai-status        - 显示 AI 状态")
                print("  watch <路径>     - 开始监控路径")
                print("  unwatch <路径>   - 停止监控路径")
                print("  watch-start      - 启动监控")
                print("  watch-stop       - 停止监控")
                print("  watch-list       - 列出监控路径")
                print("  stats            - 显示统计信息")
                print("  sources          - 列出所有来源")
                print("  clear            - 清空所有索引")
                print("  help             - 显示帮助")
                print("  quit             - 退出")
            
            elif cmd == "watch":
                if not arg:
                    print("错误: 请提供路径")
                    continue
                success = fb.watch_path(arg)
                print(f"{'✓' if success else '✗'} 监控添加{'成功' if success else '失败'}")
            
            elif cmd == "unwatch":
                if not arg:
                    print("错误: 请提供路径")
                    continue
                success = fb.unwatch_path(arg)
                print(f"{'✓' if success else '✗'} 监控移除{'成功' if success else '失败'}")
            
            elif cmd == "watch-start":
                fb.start_watching()
                print("✓ 监控已启动")
            
            elif cmd == "watch-stop":
                fb.stop_watching()
                print("✓ 监控已停止")
            
            elif cmd == "watch-list":
                paths = fb.get_watched_paths()
                print(f"\n监控路径 ({len(paths)} 个):")
                for i, path in enumerate(paths, 1):
                    print(f"  {i}. {path}")
                print()
            
            elif cmd == "ask":
                if not arg:
                    print("错误: 请提供问题")
                    continue
                
                print(f"\n正在思考...")
                result = fb.ask(arg, top_k=5)
                
                print("\n" + "=" * 60)
                print("回答:")
                print("=" * 60)
                print(result["answer"])
                print("=" * 60)
                
                if result["sources"]:
                    print(f"\n参考来源 ({len(result['sources'])} 个):")
                    for i, source in enumerate(result["sources"], 1):
                        print(f"\n{i}. {source['title']}")
                        print(f"   来源: {source['source']}")
                        print(f"   相关度: {source['relevance']:.2%}")
                        if source.get('snippet'):
                            print(f"   预览: {source['snippet']}...")
                print()
            
            elif cmd == "ai-status" or cmd == "aistatus":
                status = fb.get_ai_status()
                print("\nAI 状态:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
                print()
            
            elif cmd == "index":
                if not arg:
                    print("错误: 请提供路径")
                    continue
                
                path = Path(arg)
                if path.is_file():
                    success = fb.add_file(path)
                    print(f"{'✓' if success else '✗'} 文件索引{'成功' if success else '失败'}")
                elif path.is_dir():
                    stats = fb.add_directory(path)
                    print(f"✓ 目录索引完成: {stats}")
                else:
                    print(f"错误: 路径不存在: {path}")
            
            elif cmd == "search":
                if not arg:
                    print("错误: 请提供搜索查询")
                    continue
                
                results = fb.search(arg, top_k=5)
                
                if not results:
                    print("未找到结果")
                    continue
                
                print(f"\n找到 {len(results)} 个结果:\n")
                
                for i, result in enumerate(results, 1):
                    print(f"[{i}] {result.title or '无标题'}")
                    print(f"    来源: {result.source}")
                    print(f"    类型: {result.file_type}")
                    print(f"    相关度: {result.score:.2%}")
                    print(f"    内容: {result.content[:200]}...")
                    print()
            
            elif cmd == "stats":
                stats = fb.get_stats()
                print("\n统计信息:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
            
            elif cmd == "sources":
                sources = fb.list_sources()
                print(f"\n共有 {len(sources)} 个来源:\n")
                for i, source in enumerate(sources, 1):
                    print(f"  {i}. {source}")
                print()
            
            elif cmd == "clear":
                confirm = input("确定要清空所有索引吗? (yes/no): ")
                if confirm.lower() == "yes":
                    success = fb.clear_all()
                    print(f"{'✓' if success else '✗'} 清空{'成功' if success else '失败'}")
                else:
                    print("已取消")
            
            else:
                print(f"未知命令: {cmd}")
        
        except KeyboardInterrupt:
            print("\n再见!")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="File Brain - 本地文件系统智能搜索工具")
    parser.add_argument("--server", action="store_true", help="启动 API 服务器")
    parser.add_argument("--index", type=str, help="索引文件或目录")
    parser.add_argument("--search", type=str, help="搜索查询")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    
    args = parser.parse_args()
    
    if args.server:
        from api.server import start_server
        print_banner()
        print(f"启动 API 服务器...")
        print(f"API 文档: http://localhost:8000/docs")
        start_server()
    
    elif args.index:
        fb = FileBrain()
        path = Path(args.index)
        
        if path.is_file():
            success = fb.add_file(path)
            print(f"{'✓' if success else '✗'} 文件索引{'成功' if success else '失败'}")
        elif path.is_dir():
            stats = fb.add_directory(path)
            print(f"✓ 目录索引完成: {stats}")
        else:
            print(f"错误: 路径不存在: {path}")
    
    elif args.search:
        fb = FileBrain()
        results = fb.search(args.search, top_k=10)
        
        if not results:
            print("未找到结果")
            return
        
        print(f"\n找到 {len(results)} 个结果:\n")
        
        for i, result in enumerate(results, 1):
            print(f"[{i}] {result.title or '无标题'}")
            print(f"    来源: {result.source}")
            print(f"    类型: {result.file_type}")
            print(f"    相关度: {result.score:.2%}")
            print(f"    内容: {result.content[:300]}...")
            print()
    
    elif args.stats:
        fb = FileBrain()
        stats = fb.get_stats()
        print("\n统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    
    elif args.interactive:
        interactive_mode()
    
    else:
        # 默认进入交互模式
        interactive_mode()


if __name__ == "__main__":
    main()
