"""
智能监控管理器
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Any

from core.config.smart_monitor_config import SmartMonitorConfig, DEFAULT_SMART_MONITOR_CONFIG
from monitor.file_monitor import FileMonitor, EventType, WatchEvent


class SmartMonitorManager:
    """智能监控管理器"""
    
    def __init__(self, config: SmartMonitorConfig = None):
        """初始化"""
        self.config = config or DEFAULT_SMART_MONITOR_CONFIG
        self.file_monitor = FileMonitor()
        self.search_history: Dict[str, Dict] = self._load_search_history()
        self.active_files: Set[str] = set()
        self.last_access_time: Dict[str, float] = {}
        
    def _load_search_history(self) -> Dict[str, Dict]:
        """加载搜索历史"""
        try:
            history_path = self.config.get_search_history_path()
            if history_path.exists():
                with open(history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载搜索历史失败: {e}")
        return {}
    
    def _save_search_history(self):
        """保存搜索历史"""
        try:
            history_path = self.config.get_search_history_path()
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存搜索历史失败: {e}")
    
    def record_search(self, query: str, file_paths: List[str]):
        """记录搜索历史"""
        for file_path in file_paths:
            self.add_searched_file(file_path)
    
    def add_searched_file(self, file_path: str):
        """添加搜索过的文件"""
        file_path = str(Path(file_path).absolute())
        timestamp = time.time()
        
        if file_path not in self.search_history:
            self.search_history[file_path] = {
                'first_searched': timestamp,
                'last_searched': timestamp,
                'search_count': 1
            }
        else:
            self.search_history[file_path]['last_searched'] = timestamp
            self.search_history[file_path]['search_count'] += 1
        
        self.active_files.add(file_path)
        self.last_access_time[file_path] = timestamp
        self._save_search_history()
    
    def get_searched_files(self, days: int = 30) -> List[str]:
        """获取最近搜索的文件"""
        cutoff_time = time.time() - (days * 24 * 3600)
        return [
            file_path for file_path, info in self.search_history.items()
            if info['last_searched'] > cutoff_time
        ]
    
    def update_file_activity(self, file_path: str):
        """更新文件活跃度"""
        file_path = str(Path(file_path).absolute())
        self.last_access_time[file_path] = time.time()
        self.active_files.add(file_path)
    
    def is_file_active(self, file_path: str, threshold_seconds: int = 3600) -> bool:
        """判断文件是否活跃"""
        file_path = str(Path(file_path).absolute())
        last_access = self.last_access_time.get(file_path, 0)
        return time.time() - last_access < threshold_seconds
    
    def get_monitoring_interval(self, file_path: str) -> int:
        """获取文件的监控间隔"""
        if self.is_file_active(file_path):
            return self.config.active_file_interval
        return self.config.inactive_file_interval
    
    def should_monitor_file(self, file_path: str) -> bool:
        """判断是否应该监控文件"""
        file_path = str(Path(file_path).absolute())
        
        # 检查黑名单
        for blacklisted in self.config.blacklist:
            if blacklisted in file_path:
                return False
        
        # 检查白名单
        for whitelisted in self.config.whitelist:
            if whitelisted in file_path:
                return True
        
        # 检查搜索历史
        if self.config.monitor_searched_files:
            return file_path in self.search_history
        
        # 检查自定义目录
        for custom_dir in self.config.monitor_custom_dirs:
            if file_path.startswith(custom_dir):
                return True
        
        return False
    
    def add_path(self, path: str):
        """添加监控路径"""
        return self.file_monitor.add_path(path)
    
    def remove_path(self, path: str):
        """移除监控路径"""
        return self.file_monitor.remove_path(path)
    
    def start(self):
        """启动监控"""
        self.file_monitor.start()
    
    def stop(self):
        """停止监控"""
        self.file_monitor.stop()
    
    def add_handler(self, handler):
        """添加事件处理器"""
        self.file_monitor.add_handler(handler)
    
    @property
    def is_running(self):
        """检查是否运行"""
        return self.file_monitor.is_running
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            'is_running': self.is_running,
            'watched_paths': [str(path) for path in self.get_watched_paths()],
            'search_history_summary': self.get_search_history_summary(),
            'active_files': len(self.active_files)
        }
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取搜索历史"""
        history = []
        for file_path, info in self.search_history.items():
            history.append({
                'file_path': file_path,
                'first_searched': info['first_searched'],
                'last_searched': info['last_searched'],
                'search_count': info['search_count']
            })
        # 按最后搜索时间排序
        history.sort(key=lambda x: x['last_searched'], reverse=True)
        return history[:limit]
    
    def get_monitored_files(self) -> List[str]:
        """获取监控文件"""
        return list(self.search_history.keys())
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return True
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False
    
    def get_watched_paths(self) -> List[Path]:
        """获取正在监控的路径"""
        return self.file_monitor.get_watched_paths()
    
    def get_search_history_summary(self) -> Dict:
        """获取搜索历史摘要"""
        return {
            'total_files': len(self.search_history),
            'active_files': len(self.active_files),
            'last_updated': time.time()
        }
