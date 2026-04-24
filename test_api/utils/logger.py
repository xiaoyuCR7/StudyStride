"""
日志工具

提供统一的日志记录功能
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Optional

from config.env_config import EnvConfig


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 保存原始levelname
        original_levelname = record.levelname
        
        # 添加颜色
        if sys.platform != 'win32' or 'ANSICON' in os.environ:
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        result = super().format(record)
        
        # 恢复原始levelname
        record.levelname = original_levelname
        
        return result


class LoggerManager:
    """日志管理器"""
    
    _loggers: dict = {}
    _initialized: bool = False
    _log_dir: Optional[Path] = None
    
    @classmethod
    def _cleanup_old_logs(cls, days_to_keep: int = 2):
        """
        自动删除超过指定天数的日志文件
        
        Args:
            days_to_keep: 保留最近几天的日志，默认为2天
        """
        if not cls._log_dir or not cls._log_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for log_file in cls._log_dir.glob("test_*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except Exception as e:
                pass
        
        if deleted_count > 0:
            root_logger = logging.getLogger()
            root_logger.info(f"自动清理了 {deleted_count} 个过期日志文件")
    
    @classmethod
    def setup_logging(
        cls,
        level: Optional[str] = None,
        log_dir: Optional[str] = None,
        console: bool = True,
        file: bool = True,
        format_string: Optional[str] = None
    ):
        """
        设置日志配置
        
        Args:
            level: 日志级别
            log_dir: 日志目录
            console: 是否输出到控制台
            file: 是否输出到文件
            format_string: 日志格式
        """
        if cls._initialized:
            return
        
        # 获取配置
        test_config = EnvConfig.get_test_config()
        level = level or test_config.log_level
        
        # 设置日志目录
        if log_dir:
            cls._log_dir = Path(log_dir)
        else:
            cls._log_dir = Path(__file__).parent.parent / 'logs'
        
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志格式
        format_string = format_string or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 根日志配置
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 控制台处理器
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = ColoredFormatter(format_string)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # 文件处理器
        if file:
            log_file = cls._log_dir / f"test_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(format_string)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        # 清理过期日志文件
        cls._cleanup_old_logs(days_to_keep=2)
        
        cls._initialized = True
        root_logger.info(f"日志系统初始化完成，级别: {level}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取日志记录器"""
        if not cls._initialized:
            cls.setup_logging()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]


# 便捷函数
def setup_logging(**kwargs):
    """设置日志"""
    LoggerManager.setup_logging(**kwargs)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return LoggerManager.get_logger(name)
