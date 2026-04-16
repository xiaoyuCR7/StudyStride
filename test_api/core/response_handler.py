"""
响应处理器

统一处理API响应，提供断言和验证功能
"""
from typing import Any, Optional, List, Dict, Callable
import json
import allure

from core.api_client import ApiResponse
from utils.logger import get_logger


class ResponseHandler:
    """
    响应处理器
    
    提供响应验证和断言功能
    """
    
    def __init__(self, response: ApiResponse):
        self.response = response
        self.logger = get_logger(__name__)
    
    @property
    def status_code(self) -> int:
        """获取状态码"""
        return self.response.status_code
    
    @property
    def data(self) -> Any:
        """获取响应数据"""
        return self.response.data
    
    @property
    def headers(self) -> Dict[str, str]:
        """获取响应头"""
        return self.response.headers
    
    @property
    def response_time(self) -> float:
        """获取响应时间"""
        return self.response.response_time
    
    # ========== 状态码断言 ==========
    
    @allure.step("验证状态码为 {expected}")
    def assert_status_code(self, expected: int, message: Optional[str] = None) -> 'ResponseHandler':
        """断言状态码"""
        actual = self.status_code
        if actual != expected:
            msg = message or f"状态码不匹配: 期望 {expected}, 实际 {actual}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"状态码验证通过: {actual}")
        return self
    
    def assert_success(self) -> 'ResponseHandler':
        """断言成功响应（2xx）"""
        if not self.response.is_success:
            msg = f"期望成功响应，但得到状态码: {self.status_code}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info("成功响应验证通过")
        return self
    
    def assert_error(self) -> 'ResponseHandler':
        """断言错误响应（非2xx）"""
        if self.response.is_success:
            msg = f"期望错误响应，但得到状态码: {self.status_code}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info("错误响应验证通过")
        return self
    
    # ========== 数据断言 ==========
    
    @allure.step("验证字段 {path} 等于 {expected}")
    def assert_field_equals(self, path: str, expected: Any, message: Optional[str] = None) -> 'ResponseHandler':
        """
        断言字段值等于期望值
        
        Args:
            path: 字段路径，支持点号分隔（如：data.user.name）
            expected: 期望值
            message: 自定义错误消息
        """
        actual = self._get_field_by_path(path)
        if actual != expected:
            msg = message or f"字段 {path} 不匹配: 期望 {expected}, 实际 {actual}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"字段 {path} 验证通过: {actual}")
        return self
    
    @allure.step("验证字段 {path} 包含 {expected}")
    def assert_field_contains(self, path: str, expected: Any, message: Optional[str] = None) -> 'ResponseHandler':
        """断言字段值包含期望值"""
        actual = self._get_field_by_path(path)
        if expected not in actual:
            msg = message or f"字段 {path} 不包含 {expected}: 实际值 {actual}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"字段 {path} 包含验证通过")
        return self
    
    @allure.step("验证字段 {path} 不为空")
    def assert_field_not_empty(self, path: str, message: Optional[str] = None) -> 'ResponseHandler':
        """断言字段不为空"""
        actual = self._get_field_by_path(path)
        if not actual:
            msg = message or f"字段 {path} 为空"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"字段 {path} 非空验证通过")
        return self
    
    @allure.step("验证字段 {path} 存在")
    def assert_field_exists(self, path: str, message: Optional[str] = None) -> 'ResponseHandler':
        """断言字段存在"""
        try:
            self._get_field_by_path(path)
            self.logger.info(f"字段 {path} 存在验证通过")
            return self
        except (KeyError, TypeError):
            msg = message or f"字段 {path} 不存在"
            self.logger.error(msg)
            raise AssertionError(msg)
    
    @allure.step("验证字段 {path} 类型为 {expected_type}")
    def assert_field_type(self, path: str, expected_type: type, message: Optional[str] = None) -> 'ResponseHandler':
        """断言字段类型"""
        actual = self._get_field_by_path(path)
        if not isinstance(actual, expected_type):
            msg = message or f"字段 {path} 类型不匹配: 期望 {expected_type}, 实际 {type(actual)}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"字段 {path} 类型验证通过: {expected_type}")
        return self
    
    @allure.step("验证字段 {path} 在 {min_val} 和 {max_val} 之间")
    def assert_field_between(self, path: str, min_val: Any, max_val: Any, message: Optional[str] = None) -> 'ResponseHandler':
        """断言字段值在范围内"""
        actual = self._get_field_by_path(path)
        if not (min_val <= actual <= max_val):
            msg = message or f"字段 {path} 不在范围内: 期望 {min_val}-{max_val}, 实际 {actual}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"字段 {path} 范围验证通过")
        return self
    
    # ========== 列表断言 ==========
    
    @allure.step("验证列表长度等于 {expected_length}")
    def assert_list_length(self, path: str, expected_length: int, message: Optional[str] = None) -> 'ResponseHandler':
        """断言列表长度"""
        actual = self._get_field_by_path(path)
        if not isinstance(actual, list):
            msg = message or f"字段 {path} 不是列表"
            self.logger.error(msg)
            raise AssertionError(msg)
        
        if len(actual) != expected_length:
            msg = message or f"列表 {path} 长度不匹配: 期望 {expected_length}, 实际 {len(actual)}"
            self.logger.error(msg)
            raise AssertionError(msg)
        
        self.logger.info(f"列表 {path} 长度验证通过: {expected_length}")
        return self
    
    @allure.step("验证列表不为空")
    def assert_list_not_empty(self, path: str, message: Optional[str] = None) -> 'ResponseHandler':
        """断言列表不为空"""
        actual = self._get_field_by_path(path)
        if not isinstance(actual, list) or len(actual) == 0:
            msg = message or f"列表 {path} 为空"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"列表 {path} 非空验证通过")
        return self
    
    @allure.step("验证列表包含 {expected_item}")
    def assert_list_contains(self, path: str, expected_item: Any, message: Optional[str] = None) -> 'ResponseHandler':
        """断言列表包含指定项"""
        actual = self._get_field_by_path(path)
        if expected_item not in actual:
            msg = message or f"列表 {path} 不包含 {expected_item}"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info(f"列表 {path} 包含验证通过")
        return self
    
    # ========== 响应时间断言 ==========
    
    @allure.step("验证响应时间小于 {max_time}s")
    def assert_response_time_less_than(self, max_time: float, message: Optional[str] = None) -> 'ResponseHandler':
        """断言响应时间"""
        actual = self.response_time
        if actual > max_time:
            msg = message or f"响应时间超过限制: 最大 {max_time}s, 实际 {actual:.3f}s"
            self.logger.warning(msg)
            # 响应时间通常不导致测试失败，只记录警告
        else:
            self.logger.info(f"响应时间验证通过: {actual:.3f}s")
        return self
    
    # ========== 自定义断言 ==========
    
    @allure.step("自定义验证")
    def assert_custom(self, validator: Callable[[Any], bool], message: Optional[str] = None) -> 'ResponseHandler':
        """
        自定义断言
        
        Args:
            validator: 验证函数，接收响应数据返回布尔值
            message: 错误消息
        """
        if not validator(self.data):
            msg = message or "自定义验证失败"
            self.logger.error(msg)
            raise AssertionError(msg)
        self.logger.info("自定义验证通过")
        return self
    
    # ========== 辅助方法 ==========
    
    def _get_field_by_path(self, path: str) -> Any:
        """
        根据路径获取字段值
        
        Args:
            path: 字段路径，支持点号分隔
        
        Returns:
            字段值
        """
        keys = path.split('.')
        current = self.data
        
        for key in keys:
            if isinstance(current, dict):
                if key not in current:
                    raise KeyError(f"字段 {path} 不存在")
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                if idx >= len(current):
                    raise IndexError(f"索引 {idx} 超出范围")
                current = current[idx]
            else:
                raise TypeError(f"无法访问字段 {path}")
        
        return current
    
    def get_field(self, path: str, default: Any = None) -> Any:
        """
        安全获取字段值
        
        Args:
            path: 字段路径
            default: 默认值
        
        Returns:
            字段值或默认值
        """
        try:
            return self._get_field_by_path(path)
        except (KeyError, TypeError, IndexError):
            return default
    
    def extract(self, *paths: str) -> Dict[str, Any]:
        """
        提取多个字段值
        
        Args:
            *paths: 字段路径列表
        
        Returns:
            字段值字典
        """
        result = {}
        for path in paths:
            result[path] = self.get_field(path)
        return result
