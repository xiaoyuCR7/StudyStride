"""
数据库校验工具

用于在测试增删改接口后验证数据库中的数据是否正确
"""
from core.api_client import ApiClient
from typing import Dict, Any, Optional, List
import allure


class DBValidator:
    """数据库校验器"""
    
    def __init__(self, api_client: ApiClient):
        """
        初始化数据库校验器
        
        Args:
            api_client: API 客户端实例
        """
        self.api_client = api_client
    
    def validate_subject_exists(self, subject_id: str, expected_data: Dict[str, Any]) -> bool:
        """
        验证科目是否存在且数据正确
        
        Args:
            subject_id: 科目ID
            expected_data: 期望的科目数据
            
        Returns:
            bool: 验证是否通过
        """
        with allure.step(f"验证科目 {subject_id} 是否存在于数据库"):
            # 从数据库获取科目
            response = self.api_client.get(
                endpoint=f"subjects?id=eq.{subject_id}"
            )
            
            if not response.is_success:
                allure.attach(
                    f"获取科目失败: {response.data}",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            if not response.data or len(response.data) == 0:
                allure.attach(
                    f"科目 {subject_id} 不存在",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            actual_data = response.data[0]
            
            # 验证数据
            for key, expected_value in expected_data.items():
                if key in actual_data:
                    if actual_data[key] != expected_value:
                        allure.attach(
                            f"字段 {key} 不匹配: 期望 {expected_value}, 实际 {actual_data[key]}",
                            "错误",
                            allure.attachment_type.TEXT
                        )
                        return False
            
            allure.attach(
                f"科目 {subject_id} 验证成功",
                "成功",
                allure.attachment_type.TEXT
            )
            return True
    
    def validate_subject_not_exists(self, subject_id: str) -> bool:
        """
        验证科目是否不存在
        
        Args:
            subject_id: 科目ID
            
        Returns:
            bool: 验证是否通过
        """
        with allure.step(f"验证科目 {subject_id} 是否不存在于数据库"):
            response = self.api_client.get(
                endpoint=f"subjects?id=eq.{subject_id}"
            )
            
            if not response.is_success:
                allure.attach(
                    f"查询科目失败: {response.data}",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            if response.data and len(response.data) > 0:
                allure.attach(
                    f"科目 {subject_id} 仍然存在",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            allure.attach(
                f"科目 {subject_id} 验证不存在成功",
                "成功",
                allure.attachment_type.TEXT
            )
            return True
    
    def validate_study_session_exists(self, session_id: str, expected_data: Dict[str, Any]) -> bool:
        """
        验证学习会话是否存在且数据正确
        
        Args:
            session_id: 会话ID
            expected_data: 期望的会话数据
            
        Returns:
            bool: 验证是否通过
        """
        with allure.step(f"验证学习会话 {session_id} 是否存在于数据库"):
            response = self.api_client.get(
                endpoint=f"study_sessions?id=eq.{session_id}"
            )
            
            if not response.is_success:
                allure.attach(
                    f"获取学习会话失败: {response.data}",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            if not response.data or len(response.data) == 0:
                allure.attach(
                    f"学习会话 {session_id} 不存在",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            actual_data = response.data[0]
            
            # 验证数据
            for key, expected_value in expected_data.items():
                if key in actual_data:
                    if actual_data[key] != expected_value:
                        # 尝试类型转换
                        try:
                            # 如果期望值是字符串，实际值是数字，尝试转换
                            if isinstance(expected_value, str) and isinstance(actual_data[key], (int, float)):
                                actual_value = str(actual_data[key])
                            # 如果期望值是数字，实际值是字符串，尝试转换
                            elif isinstance(expected_value, (int, float)) and isinstance(actual_data[key], str):
                                actual_value = int(actual_data[key])
                        except (ValueError, TypeError):
                            pass

                        if actual_value == expected_value:
                            continue
                        allure.attach(
                            f"字段 {key} 不匹配: 期望 {expected_value}, 实际 {actual_data[key]}",
                            "错误",
                            allure.attachment_type.TEXT
                        )
                        return False
            
            allure.attach(
                f"学习会话 {session_id} 验证成功",
                "成功",
                allure.attachment_type.TEXT
            )
            return True
    
    def validate_user_settings_exists(self, user_id: str, expected_data: Dict[str, Any]) -> bool:
        """
        验证用户设置是否存在且数据正确
        
        Args:
            user_id: 用户ID
            expected_data: 期望的设置数据
            
        Returns:
            bool: 验证是否通过
        """
        with allure.step(f"验证用户 {user_id} 的设置是否存在于数据库"):
            response = self.api_client.get(
                endpoint=f"user_settings?user_id=eq.{user_id}"
            )
            
            if not response.is_success:
                allure.attach(
                    f"获取用户设置失败: {response.data}",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            if not response.data or len(response.data) == 0:
                allure.attach(
                    f"用户 {user_id} 的设置不存在",
                    "错误",
                    allure.attachment_type.TEXT
                )
                return False
            
            actual_data = response.data[0]
            
            # 验证数据
            for key, expected_value in expected_data.items():
                if key in actual_data:
                    if actual_data[key] != expected_value:
                        allure.attach(
                            f"字段 {key} 不匹配: 期望 {expected_value}, 实际 {actual_data[key]}",
                            "错误",
                            allure.attachment_type.TEXT
                        )
                        return False
            
            allure.attach(
                f"用户 {user_id} 的设置验证成功",
                "成功",
                allure.attachment_type.TEXT
            )
            return True
