"""
重试辅助工具

提供失败重试功能
"""
import time
import functools
from typing import Callable, Optional, Type, Tuple, Any
import allure

from utils.logger import get_logger


class RetryHelper:
    """重试辅助类"""
    
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        on_retry: Optional[Callable[[Exception, int], None]] = None
    ):
        """
        初始化重试助手
        
        Args:
            max_retries: 最大重试次数
            delay: 初始延迟时间（秒）
            backoff: 延迟增长倍数
            exceptions: 需要重试的异常类型
            on_retry: 重试时的回调函数
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.on_retry = on_retry
        self.logger = get_logger(__name__)
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行带重试的函数
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            函数返回值
        """
        last_exception = None
        current_delay = self.delay
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    self.logger.warning(
                        f"函数执行失败（尝试 {attempt + 1}/{self.max_retries + 1}）: {e}"
                    )
                    
                    if self.on_retry:
                        self.on_retry(e, attempt + 1)
                    
                    time.sleep(current_delay)
                    current_delay *= self.backoff
                else:
                    self.logger.error(f"函数执行失败，已用尽所有重试次数: {e}")
        
        raise last_exception


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 延迟增长倍数
        exceptions: 需要重试的异常类型
        on_retry: 重试回调函数
    
    使用示例：
        @retry(max_retries=3, delay=1)
        def test_api():
            # 可能失败的API调用
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        @allure.step(f"执行 {func.__name__} (最多重试{max_retries}次)")
        def wrapper(*args, **kwargs):
            helper = RetryHelper(
                max_retries=max_retries,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions,
                on_retry=on_retry
            )
            return helper.execute(func, *args, **kwargs)
        
        return wrapper
    
    return decorator


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0
):
    """
    pytest失败重试装饰器
    
    使用示例：
        @retry_on_failure(max_retries=3)
        def test_example():
            pass
    """
    import pytest
    
    return pytest.mark.flaky(reruns=max_retries, reruns_delay=delay)
