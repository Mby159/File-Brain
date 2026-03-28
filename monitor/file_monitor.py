"""
文件夹监控器
使用 watchdog 监控文件系统变化
"""
import threading
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Callable, Optional, Union
from enum import Enum

from config import SUPPORTED_EXTENSIONS


class EventType(Enum):
    """事件类型"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class WatchEvent:
    """监控事件"""
    event_type: EventType
    path: Path
    src_path: Optional[Path] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class FileMonitor:
    """文件监控器"""
    
    def __init__(self):
        self.observer = None
        self.is_running = False
        self.watched_paths: List[Path] = []
        self.event_handlers: List[Callable[[WatchEvent], None]] = []
        self.event_queue: List[WatchEvent] = []
        self.debounce_time = 1.0  # 1秒防抖
        self.last_event_time = {}
        self._thread = None
        self._stop_event = None
    
    def _should_process(self, path: Path) -> bool:
        """判断是否应该处理该文件"""
        if path.is_dir():
            return True
        
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False
        
        if any(part.startswith('.') for part in path.parts):
            return False
        
        return True
    
    def _debounce_check(self, path: Path, event_type: EventType) -> bool:
        """防抖检查"""
        key = f"{event_type.value}:{path}"
        current_time = time.time()
        last_time = self.last_event_time.get(key, 0)
        
        if current_time - last_time < self.debounce_time:
            return False
        
        self.last_event_time[key] = current_time
        return True
    
    def add_path(self, path: Union[str, Path], recursive: bool = True) -> bool:
        """
        添加要监控的路径
        
        Args:
            path: 要监控的路径
            recursive: 是否递归监控子目录
        """
        path = Path(path)
        if not path.exists():
            print(f"路径不存在: {path}")
            return False
        
        if path not in self.watched_paths:
            self.watched_paths.append(path)
            print(f"开始监控: {path}")
            return True
        return False
    
    def remove_path(self, path: Union[str, Path]) -> bool:
        """移除监控路径"""
        path = Path(path)
        if path in self.watched_paths:
            self.watched_paths.remove(path)
            print(f"停止监控: {path}")
            return True
        return False
    
    def add_handler(self, handler: Callable[[WatchEvent], None]):
        """添加事件处理器"""
        if handler not in self.event_handlers:
            self.event_handlers.append(handler)
    
    def remove_handler(self, handler: Callable[[WatchEvent], None]):
        """移除事件处理器"""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
    
    def _dispatch_event(self, event: WatchEvent):
        """分发事件到所有处理器"""
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"事件处理器错误: {e}")
    
    def _polling_loop(self):
        """轮询监控循环（替代 watchdog，避免编译依赖）"""
        path_states = {}
        
        # 初始化状态
        for path in self.watched_paths:
            if path.is_dir():
                for file_path in path.rglob("*"):
                    if self._should_process(file_path):
                        stat = file_path.stat()
                        path_states[str(file_path)] = {
                            'mtime': stat.st_mtime,
                            'exists': True
                        }
            elif path.is_file() and self._should_process(path):
                stat = path.stat()
                path_states[str(path)] = {
                    'mtime': stat.st_mtime,
                    'exists': True
                }
        
        while not self._stop_event.is_set():
            try:
                current_paths = set()
                
                # 扫描所有路径
                for watch_path in self.watched_paths:
                    if not watch_path.exists():
                        continue
                    
                    if watch_path.is_dir():
                        for file_path in watch_path.rglob("*"):
                            if self._should_process(file_path):
                                current_paths.add(str(file_path))
                    elif watch_path.is_file() and self._should_process(watch_path):
                        current_paths.add(str(watch_path))
                
                # 检查新增和修改
                for file_path_str in current_paths:
                    file_path = Path(file_path_str)
                    
                    try:
                        stat = file_path.stat()
                        old_state = path_states.get(file_path_str)
                        
                        if old_state is None:
                            # 新增文件
                            if self._debounce_check(file_path, EventType.CREATED):
                                event = WatchEvent(
                                    event_type=EventType.CREATED,
                                    path=file_path
                                )
                                print(f"[监控] 新增: {file_path}")
                                self._dispatch_event(event)
                            
                            path_states[file_path_str] = {
                                'mtime': stat.st_mtime,
                                'exists': True
                            }
                        elif abs(stat.st_mtime - old_state['mtime']) > 0.1:
                            # 文件修改
                            if self._debounce_check(file_path, EventType.MODIFIED):
                                event = WatchEvent(
                                    event_type=EventType.MODIFIED,
                                    path=file_path
                                )
                                print(f"[监控] 修改: {file_path}")
                                self._dispatch_event(event)
                            
                            path_states[file_path_str]['mtime'] = stat.st_mtime
                    
                    except Exception as e:
                        pass
                
                # 检查删除
                for file_path_str in list(path_states.keys()):
                    if file_path_str not in current_paths:
                        file_path = Path(file_path_str)
                        
                        if self._debounce_check(file_path, EventType.DELETED):
                            event = WatchEvent(
                                event_type=EventType.DELETED,
                                path=file_path
                            )
                            print(f"[监控] 删除: {file_path}")
                            self._dispatch_event(event)
                        
                        del path_states[file_path_str]
                
                time.sleep(1)  # 每秒检查一次
            
            except Exception as e:
                print(f"监控循环错误: {e}")
                time.sleep(1)
    
    def start(self):
        """启动监控"""
        if self.is_running:
            print("监控已在运行中")
            return
        
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class _Handler(FileSystemEventHandler):
                def __init__(self, monitor):
                    self.monitor = monitor
                
                def on_created(self, event):
                    if event.is_directory:
                        return
                    path = Path(event.src_path)
                    if self.monitor._should_process(path):
                        if self.monitor._debounce_check(path, EventType.CREATED):
                            watch_event = WatchEvent(EventType.CREATED, path)
                            print(f"[监控] 新增: {path}")
                            self.monitor._dispatch_event(watch_event)
                
                def on_modified(self, event):
                    if event.is_directory:
                        return
                    path = Path(event.src_path)
                    if self.monitor._should_process(path):
                        if self.monitor._debounce_check(path, EventType.MODIFIED):
                            watch_event = WatchEvent(EventType.MODIFIED, path)
                            print(f"[监控] 修改: {path}")
                            self.monitor._dispatch_event(watch_event)
                
                def on_deleted(self, event):
                    if event.is_directory:
                        return
                    path = Path(event.src_path)
                    if self.monitor._debounce_check(path, EventType.DELETED):
                        watch_event = WatchEvent(EventType.DELETED, path)
                        print(f"[监控] 删除: {path}")
                        self.monitor._dispatch_event(watch_event)
            
            self.observer = Observer()
            handler = _Handler(self)
            
            for path in self.watched_paths:
                if path.is_dir():
                    self.observer.schedule(handler, str(path), recursive=True)
                elif path.is_file():
                    self.observer.schedule(handler, str(path.parent), recursive=False)
            
            self.observer.start()
            self.is_running = True
            print("监控已启动 (使用 watchdog)")
        
        except ImportError:
            print("watchdog 未安装，使用轮询模式")
            self._stop_event = threading.Event()
            self._thread = threading.Thread(target=self._polling_loop, daemon=True)
            self._thread.start()
            self.is_running = True
            print("监控已启动 (使用轮询模式)")
    
    def stop(self):
        """停止监控"""
        if not self.is_running:
            return
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        elif self._stop_event:
            self._stop_event.set()
            if self._thread:
                self._thread.join(timeout=5)
        
        self.is_running = False
        print("监控已停止")
    
    def get_watched_paths(self) -> List[Path]:
        """获取正在监控的路径列表"""
        return self.watched_paths.copy()
    
    def is_path_watched(self, path: Union[str, Path]) -> bool:
        """检查路径是否被监控"""
        path = Path(path)
        for watched in self.watched_paths:
            if path == watched or watched in path.parents:
                return True
        return False
