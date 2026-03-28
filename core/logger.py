"""
日志模块
提供结构化的日志记录功能
"""
import logging
import os
from pathlib import Path
from datetime import datetime

# 日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件
LOG_FILE = LOG_DIR / f"file_brain_{datetime.now().strftime('%Y%m%d')}.log"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 创建日志记录器
logger = logging.getLogger("file_brain")

# 自定义日志方法
def log_info(message: str, **kwargs):
    """记录信息日志"""
    logger.info(message, extra=kwargs)

def log_error(message: str, error: Exception = None, **kwargs):
    """记录错误日志"""
    if error:
        message = f"{message}: {str(error)}"
    logger.error(message, extra=kwargs)

def log_debug(message: str, **kwargs):
    """记录调试日志"""
    logger.debug(message, extra=kwargs)

def log_warning(message: str, **kwargs):
    """记录警告日志"""
    logger.warning(message, extra=kwargs)
