"""
用户设置接口测试

测试用户设置的增删改查功能
"""
import pytest
import allure

from core.api_client import ApiClient
from core.response_handler import ResponseHandler
from core.auth_manager import AuthManager
from utils.faker_helper import faker_helper
from utils.allure_helper import allure_feature, allure_story, allure_severity, allure_tag
from utils.retry_helper import retry_on_failure


@allure_feature("用户设置管理")
@allure_story("用户设置CRUD")
class TestUserSettings:
    """用户设置接口测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.api_client = ApiClient()
        cls.auth_manager = AuthManager(cls.api_client)
        cls.base_endpoint = "user_settings"
        
        # 生成测试账号
        cls.test_email = faker_helper.generate_email(prefix='test')
        cls.test_password = faker_helper.generate_password()
        cls.test_name = faker_helper.generate_name()
        
        # 先注册
        with allure.step(f"使用邮箱 {cls.test_email} 注册"):
            signup_response = cls.auth_manager.signup(
                email=cls.test_email,
                password=cls.test_password,
                user_metadata={"name": cls.test_name}
            )
        
        # 执行登录，获取认证令牌
        with allure.step(f"使用邮箱 {cls.test_email} 登录获取认证令牌"):
            login_response = cls.auth_manager.login(cls.test_email, cls.test_password)
            if not login_response.is_success:
                allure.attach(
                    f"登录失败: {login_response.data}",
                    "警告",
                    allure.attachment_type.TEXT
                )
                pytest.skip("登录失败，跳过测试")
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 登出
        with allure.step("执行登出"):
            cls.auth_manager.logout()
        cls.api_client.close()
    
    def _generate_user_settings_data(self):
        """生成测试用户设置数据"""
        return {
            "user_id": self.auth_manager.get_user_id(),
            "reminder_interval": faker_helper.faker.random_int(min=5, max=60)
        }
    
    @allure_severity("critical")
    @allure_tag("smoke", "positive")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.user_settings
    def test_update_user_settings(self):
        """测试更新用户设置"""
        with allure.step("准备测试数据"):
            user_id = self.auth_manager.get_user_id()
            settings_data = {
                "user_id": user_id,
                "reminder_interval": faker_helper.faker.random_int(min=5, max=60)
            }
            allure.attach(
                str(settings_data),
                "请求数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送更新请求"):
            # PostgREST要求更新操作必须包含主键过滤
            endpoint = f"{self.base_endpoint}"
            response = self.api_client.put(
                params={"user_id": f"eq.{user_id}"},
                endpoint=endpoint,
                json_data=settings_data
            )
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            assert response.status_code in [200, 204, 201]
    
    @allure_severity("normal")
    @allure_tag("positive")
    @pytest.mark.positive
    @pytest.mark.user_settings
    def test_get_user_settings(self):
        """测试获取用户设置"""
        with allure.step("发送获取请求"):
            response = self.api_client.get(endpoint=self.base_endpoint)
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            assert response.status_code == 200
            if response.is_success and isinstance(response.data, dict):
                handler.assert_field_exists('user_id')
                handler.assert_field_exists('reminder_interval')
    
    @allure_severity("normal")
    @allure_tag("negative")
    @pytest.mark.negative
    @pytest.mark.user_settings
    def test_update_user_settings_invalid_data(self):
        """测试更新用户设置失败（无效数据）"""
        with allure.step("准备无效测试数据"):
            user_id = self.auth_manager.get_user_id()
            invalid_data = {
                "user_id": user_id,
                "reminder_interval": "invalid"  # reminder_interval应该是整数
            }
        
        with allure.step("发送更新请求"):
            # PostgREST要求更新操作必须包含主键过滤
            endpoint = f"{self.base_endpoint}?user_id=eq.{user_id}"
            response = self.api_client.put(
                endpoint=endpoint,
                json_data=invalid_data
            )
        
        with allure.step("验证错误响应"):
            assert response.status_code >= 400
