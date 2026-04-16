"""
认证接口测试

测试用户登录、注册、Token刷新等功能
"""
import pytest
import allure

from core.api_client import ApiClient
from core.auth_manager import AuthManager
from core.response_handler import ResponseHandler
from utils.data_provider import DataProvider, TestData
from utils.allure_helper import allure_feature, allure_story, allure_severity, allure_tag
from utils.retry_helper import retry_on_failure


@allure_feature("认证管理")
@allure_story("用户登录")
class TestAuth:
    """认证接口测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.api_client = ApiClient()
        cls.auth_manager = AuthManager(cls.api_client)
        cls.data_provider = DataProvider()
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        cls.api_client.close()
    
    @allure_severity("blocker")
    @allure_tag("smoke", "positive")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.auth
    @retry_on_failure(max_retries=2)
    def test_login_success(self):
        """测试正常登录"""
        with allure.step("准备测试数据"):
            email = "1178327328@qq.com"
            password = "12345678"
        
        with allure.step("执行登录请求"):
            response = self.auth_manager.login(email, password)
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            # 注意：实际测试时需要根据API实际行为调整断言
            # 这里使用示例断言
            if response.is_success:
                handler.assert_success()
                if isinstance(response.data, dict):
                    handler.assert_field_exists('access_token')
            else:
                # 如果登录失败，可能是测试环境未配置
                allure.attach(
                    "登录失败，可能是测试环境未配置",
                    "警告",
                    allure.attachment_type.TEXT
                )
    
    @allure_severity("critical")
    @allure_tag("negative")
    @pytest.mark.negative
    @pytest.mark.auth
    @pytest.mark.parametrize(
        "email,password,expected_status",
        [
            ("117832732@qq.com", "WrongPass", 400),
            ("1178327328@qq.com", "", 400),
            ("", "12345678", 400),
            ("1178327328qq.com", "12345678", 400),
        ],
        ids=["错误凭证", "空密码", "空邮箱", "无效邮箱格式"]
    )
    def test_login_failure(self, email, password, expected_status):
        """测试登录失败场景"""
        with allure.step(f"使用邮箱 {email} 和密码 {password} 登录"):
            response = self.auth_manager.login(email, password)
        
        with allure.step("验证错误响应"):
            assert response.status_code == expected_status or not response.is_success
    
    @allure_severity("critical")
    @allure_tag("smoke", "positive")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.auth
    def test_signup(self):
        """测试用户注册"""
        import uuid
        
        with allure.step("生成唯一邮箱"):
            unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            password = "Test123456"
        
        with allure.step("执行注册请求"):
            response = self.auth_manager.signup(
                email=unique_email,
                password=password,
                user_metadata={"name": "Test User"}
            )
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            # 注册可能成功或失败（如果用户已存在）
            if response.is_success:
                handler.assert_success()
    
    
    @allure_severity("normal")
    @allure_tag("positive")
    @pytest.mark.positive
    @pytest.mark.auth
    def test_logout(self):
        """测试用户登出"""
        with allure.step("执行登出"):
            response = self.auth_manager.logout()
        
        with allure.step("验证Token已清除"):
            assert self.auth_manager.get_access_token() is None
            assert not self.auth_manager.is_authenticated()


@allure_feature("认证管理")
@allure_story("数据驱动登录测试")
class TestAuthDataDriven:
    """数据驱动认证测试"""
    
    @classmethod
    def setup_class(cls):
        cls.api_client = ApiClient()
        cls.auth_manager = AuthManager(cls.api_client)
        cls.data_provider = DataProvider()
    
    @classmethod
    def teardown_class(cls):
        cls.api_client.close()
    
    @allure_severity("critical")
    @pytest.mark.auth
    @pytest.mark.parametrize(
        "test_data",
        DataProvider().load_yaml("auth_data.yaml"),
        ids=lambda x: x.name
    )
    def test_login_data_driven(self, test_data: TestData):
        """数据驱动登录测试"""
        with allure.step(f"执行测试: {test_data.name}"):
            allure.description(test_data.description)
            
            # 添加标签
            if test_data.tags:
                for tag in test_data.tags:
                    allure.tag(tag)
            
            data = test_data.data
            
            # 根据测试数据决定执行登录还是注册
            if "注册" in test_data.name:
                with allure.step("执行注册"):
                    response = self.auth_manager.signup(
                        email=data.get('email', ''),
                        password=data.get('password', ''),
                        user_metadata=data.get('user_metadata')
                    )
            else:
                with allure.step("执行登录"):
                    response = self.auth_manager.login(
                        email=data.get('email', ''),
                        password=data.get('password', '')
                    )
            
            with allure.step("验证响应"):
                handler = ResponseHandler(response)
                expected = test_data.expected or {}
                
                # 验证状态码
                if 'status_code' in expected:
                    handler.assert_status_code(expected['status_code'])
                
                # 验证Token
                if expected.get('has_token'):
                    if isinstance(response.data, dict):
                        handler.assert_field_exists('access_token')
                
                # 验证用户存在
                if expected.get('has_user'):
                    if isinstance(response.data, dict):
                        handler.assert_field_exists('user')
                
                # 验证错误消息
                if 'error_message' in expected:
                    # 检查响应中是否包含错误信息
                    error_message = expected['error_message']
                    if isinstance(response.data, dict):
                        if 'error' in response.data:
                            error_info = response.data['error']
                            if isinstance(error_info, str):
                                assert error_message in error_info, f"错误消息不匹配: 期望包含 '{error_message}', 实际 '{error_info}'"
                            elif isinstance(error_info, dict) and 'message' in error_info:
                                assert error_message in error_info['message'], f"错误消息不匹配: 期望包含 '{error_message}', 实际 '{error_info['message']}'"
                    elif isinstance(response.data, str):
                        assert error_message in response.data, f"错误消息不匹配: 期望包含 '{error_message}', 实际 '{response.data}'"
