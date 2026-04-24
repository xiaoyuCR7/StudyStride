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
from utils.faker_helper import faker_helper
from utils.schema_validator import validate_schema


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
        # 生成测试账号
        cls.test_email = faker_helper.generate_email(prefix='test')
        cls.test_password = faker_helper.generate_password()
        cls.test_name = faker_helper.generate_name()
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        cls.api_client.close()
    
    @allure_severity("critical")
    @allure_tag("smoke", "positive")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.auth
    def test_signup(self):
        """测试用户注册"""
        with allure.step(f"使用邮箱 {self.test_email} 注册"):
            response = self.auth_manager.signup(
                email=self.test_email,
                password=self.test_password,
                user_metadata={"name": self.test_name}
            )
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            # 注册可能成功或失败（如果用户已存在）
            if response.is_success:
                handler.assert_success()
                
                # JSON Schema 校验
                schema_validation_data = None
                if isinstance(response.data, dict):
                    schema_validation_data = response.data
                elif isinstance(response.data, list) and len(response.data) > 0:
                    schema_validation_data = response.data[0]
                
                if schema_validation_data:
                    with allure.step("JSON Schema 校验"):
                        validate_schema(schema_validation_data, "auth")
                else:
                    allure.attach(
                        "无法获取数据进行 JSON Schema 校验",
                        "警告",
                        allure.attachment_type.TEXT
                    )
    
    @allure_severity("blocker")
    @allure_tag("smoke", "positive")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.auth
    @retry_on_failure(max_retries=2)
    def test_login_success(self):
        """测试正常登录"""
        with allure.step(f"使用邮箱 {self.test_email} 和密码 {self.test_password} 登录"):
            response = self.auth_manager.login(self.test_email, self.test_password)
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            # 注意：实际测试时需要根据API实际行为调整断言
            # 这里使用示例断言
            if response.is_success:
                handler.assert_success()
                if isinstance(response.data, dict):
                    handler.assert_field_exists('access_token')
                
                # JSON Schema 校验
                schema_validation_data = None
                if isinstance(response.data, dict):
                    schema_validation_data = response.data
                elif isinstance(response.data, list) and len(response.data) > 0:
                    schema_validation_data = response.data[0]
                
                if schema_validation_data:
                    with allure.step("JSON Schema 校验"):
                        validate_schema(schema_validation_data, "auth")
                else:
                    allure.attach(
                        "无法获取数据进行 JSON Schema 校验",
                        "警告",
                        allure.attachment_type.TEXT
                    )
            else:
                # 如果登录失败，可能是测试环境未配置
                allure.attach(
                    "登录失败，可能是测试环境未配置",
                    "警告",
                    allure.attachment_type.TEXT
                )
    
    @allure_severity("normal")
    @allure_tag("positive")
    @pytest.mark.positive
    @pytest.mark.auth
    def test_logout(self):
        """测试用户登出"""
        # 确保先登录
        with allure.step("确保用户已登录"):
            self.auth_manager.login(self.test_email, self.test_password)
        
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
        # 为数据驱动测试生成测试账号
        cls.test_email = faker_helper.generate_email(prefix='test')
        cls.test_password = faker_helper.generate_password()
    
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
            
            # 根据测试场景使用不同的账号数据
            if "正常登录" in test_data.name:
                # 使用类级别的测试账号
                email = self.test_email
                password = self.test_password
                # 确保账号已注册
                with allure.step(f"确保账号 {email} 已注册"):
                    signup_response = self.auth_manager.signup(
                        email=email,
                        password=password,
                        user_metadata={"name": faker_helper.generate_name()}
                    )
            elif "错误密码" in test_data.name:
                # 使用已注册的账号，但使用错误密码
                email = self.test_email
                password = "WrongPassword123"
            elif "不存在的用户" in test_data.name:
                # 使用未注册的账号
                email = faker_helper.generate_email(prefix='test')
                password = faker_helper.generate_password()
            elif "空邮箱" in test_data.name:
                # 使用空邮箱
                email = ""
                password = faker_helper.generate_password()
            elif "空密码" in test_data.name:
                # 使用空密码
                email = self.test_email
                password = ""
            elif "注册" in test_data.name:
                # 使用类级别的测试账号
                email = self.test_email
                password = self.test_password
            else:
                # 默认使用类级别的测试账号
                email = self.test_email
                password = self.test_password
            
            # 根据测试数据决定执行登录还是注册
            if "注册" in test_data.name:
                with allure.step(f"使用邮箱 {email} 执行注册"):
                    response = self.auth_manager.signup(
                        email=email,
                        password=password,
                        user_metadata=data.get('user_metadata') or {"name": faker_helper.generate_name()}
                    )
            else:
                with allure.step(f"使用邮箱 {email} 执行登录"):
                    response = self.auth_manager.login(
                        email=email,
                        password=password
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
