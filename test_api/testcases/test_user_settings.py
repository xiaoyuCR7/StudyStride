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
from utils.schema_validator import validate_schema
from utils.db_validator import DBValidator


@allure_feature("用户设置管理")
@allure_story("用户设置CRUD")
class TestUserSettings:
    """用户设置接口测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.api_client = ApiClient()
        cls.auth_manager = AuthManager(cls.api_client)
        cls.db_validator = DBValidator(cls.api_client)
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
            
            # 添加详细的调试信息
            debug_info = f"状态码: {response.status_code}\n"
            debug_info += f"数据类型: {type(response.data).__name__}\n"
            debug_info += f"数据内容: {response.data}\n"
            
            # 检查数据结构
            if isinstance(response.data, dict):
                debug_info += f"字典键: {list(response.data.keys())}\n"
            elif isinstance(response.data, list):
                debug_info += f"列表长度: {len(response.data)}\n"
                if response.data:
                    first_item = response.data[0]
                    if isinstance(first_item, dict):
                        debug_info += f"列表第一个元素类型: {type(first_item).__name__}\n"
                        debug_info += f"列表第一个元素键: {list(first_item.keys())}\n"
                        debug_info += f"列表第一个元素内容: {first_item}\n"
            
            allure.attach(
                debug_info,
                "响应信息",
                allure.attachment_type.TEXT
            )
            
            assert response.status_code in [200, 204, 201]
            
            # 处理不同的数据结构
            schema_validation_data = None
            reminder_interval = None
            
            if response.is_success:
                if isinstance(response.data, dict):
                    # 响应是字典
                    schema_validation_data = response.data
                    if 'reminder_interval' in response.data:
                        reminder_interval = response.data['reminder_interval']
                    
                elif isinstance(response.data, list) and len(response.data) > 0:
                    # 响应是列表
                    first_item = response.data[0]
                    if isinstance(first_item, dict):
                        schema_validation_data = first_item
                        if 'reminder_interval' in first_item:
                            reminder_interval = first_item['reminder_interval']
                
                # 如果响应为空，通过查询获取数据
                elif isinstance(response.data, str) and response.data.strip() == '' or response.status_code == 204:
                    with allure.step("响应体为空或204状态码，通过查询获取用户设置"):
                        query_response = self.api_client.get(
                            endpoint=f"{self.base_endpoint}?user_id=eq.{user_id}"
                        )
                        
                        if query_response.is_success and isinstance(query_response.data, list) and len(query_response.data) > 0:
                            first_item = query_response.data[0]
                            schema_validation_data = first_item
                            if 'reminder_interval' in first_item:
                                reminder_interval = first_item['reminder_interval']
                            allure.attach(
                                f"通过查询获取到用户设置: user_id={user_id}",
                                "查询结果",
                                allure.attachment_type.TEXT
                            )
                        else:
                            allure.attach(
                                "无法通过查询获取用户设置",
                                "警告",
                                allure.attachment_type.TEXT
                            )
                
                # 验证提醒间隔
                if reminder_interval is not None:
                    assert reminder_interval == settings_data['reminder_interval'], f"提醒间隔不匹配: 期望 {settings_data['reminder_interval']}, 实际 {reminder_interval}"
            
            # JSON Schema 校验（单独分开）
            if schema_validation_data:
                with allure.step("JSON Schema 校验"):
                    validate_schema(schema_validation_data, "user_settings")
            else:
                allure.attach(
                    "无法获取数据进行 JSON Schema 校验",
                    "警告",
                    allure.attachment_type.TEXT
                )
            
            # 数据库校验（单独分开）
            with allure.step("数据库校验"):
                assert self.db_validator.validate_user_settings_exists(user_id, settings_data)
                
                # 清理：重置为默认值
                with allure.step("清理测试数据"):
                    reset_data = {
                        "user_id": user_id,
                        "reminder_interval": 60
                    }
                    reset_response = self.api_client.put(
                        params={"user_id": f"eq.{user_id}"},
                        endpoint=endpoint,
                        json_data=reset_data
                    )
                    assert reset_response.status_code in [200, 204, 201]
    
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
            
            # 处理不同的数据结构
            schema_validation_data = None
            
            if response.is_success:
                if isinstance(response.data, dict):
                    handler.assert_field_exists('user_id')
                    handler.assert_field_exists('reminder_interval')
                    schema_validation_data = response.data
                    
                elif isinstance(response.data, list) and len(response.data) > 0:
                    first_item = response.data[0]
                    if isinstance(first_item, dict):
                        # 直接验证字典字段
                        assert 'user_id' in first_item, "字段 'user_id' 不存在"
                        assert 'reminder_interval' in first_item, "字段 'reminder_interval' 不存在"
                        schema_validation_data = first_item
            
            # JSON Schema 校验
            if schema_validation_data:
                with allure.step("JSON Schema 校验"):
                    validate_schema(schema_validation_data, "user_settings")
            else:
                allure.attach(
                    "无法获取数据进行 JSON Schema 校验",
                    "警告",
                    allure.attachment_type.TEXT
                )
    
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
