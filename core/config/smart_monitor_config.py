"""
智能监控配置
"""
from typing import List
from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class SmartMonitorConfig:
    """智能监控配置"""
    # 监控模式: "smart", "full", "custom"
    mode: str = "smart"
    
    # 智能监控设置
    monitor_searched_files: bool = True
    monitor_custom_dirs: List[str] = None
    
    # 自适应频率（秒）
    active_file_interval: int = 5      # 活跃文件监控间隔
    inactive_file_interval: int = 300   # 不活跃文件监控间隔
    
    # 白名单和黑名单
    whitelist: List[str] = None
    blacklist: List[str] = None
    
    # 历史记录配置
    search_history_path: str = "~/.file-brain/search_history.json"
    
    def __post_init__(self):
        """初始化"""
        if self.monitor_custom_dirs is None:
            self.monitor_custom_dirs = []
        
        if self.whitelist is None:
            self.whitelist = []
        
        if self.blacklist is None:
            self.blacklist = []
        
        # 解析搜索历史路径
        self.search_history_path = os.path.expanduser(self.search_history_path)
        
    def get_search_history_path(self) -> Path:
        """获取搜索历史文件路径"""
        path = Path(self.search_history_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


# 默认配置
DEFAULT_SMART_MONITOR_CONFIG = SmartMonitorConfig()
