"""
日志工具

提供统一的日志记录功能，按日期分文件存储
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        original_levelname = record.levelname
        
        if sys.platform != 'win32' or 'ANSICON' in os.environ:
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        result = super().format(record)
        
        record.levelname = original_levelname
        
        return result


class LoggerManager:
    """日志管理器"""
    
    _loggers: dict = {}
    _initialized: bool = False
    _log_dir: Optional[Path] = None
    _current_date: Optional[str] = None
    _file_handler: Optional[RotatingFileHandler] = None
    
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
        
        level = level or os.getenv('LOG_LEVEL', 'INFO')
        
        if log_dir:
            cls._log_dir = Path(log_dir)
        else:
            cls._log_dir = Path(__file__).parent.parent / 'logs'
        
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        
        format_string = format_string or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        root_logger.handlers.clear()
        
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = ColoredFormatter(format_string)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        if file:
            cls._current_date = datetime.now().strftime('%Y%m%d')
            log_file = cls._log_dir / f"test_{cls._current_date}.log"
            cls._file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            cls._file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(format_string)
            cls._file_handler.setFormatter(file_formatter)
            root_logger.addHandler(cls._file_handler)
        
        cls._initialized = True
        root_logger.info(f"日志系统初始化完成，级别: {level}")
    
    @classmethod
    def _check_date_change(cls):
        """检查日期是否变化，如果变化则创建新的日志文件"""
        current_date = datetime.now().strftime('%Y%m%d')
        if cls._current_date != current_date:
            cls._current_date = current_date
            root_logger = logging.getLogger()
            
            if cls._file_handler:
                root_logger.removeHandler(cls._file_handler)
                cls._file_handler.close()
            
            log_file = cls._log_dir / f"test_{current_date}.log"
            cls._file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            cls._file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            cls._file_handler.setFormatter(file_formatter)
            root_logger.addHandler(cls._file_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取日志记录器"""
        if not cls._initialized:
            cls.setup_logging()
        
        cls._check_date_change()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]


def setup_logging(**kwargs):
    """设置日志"""
    LoggerManager.setup_logging(**kwargs)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return LoggerManager.get_logger(name)
