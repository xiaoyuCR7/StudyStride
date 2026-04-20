"""
科目接口测试

测试科目的增删改查功能
"""
import pytest
import allure
import uuid

from core.api_client import ApiClient
from core.response_handler import ResponseHandler
from core.request_builder import RequestBuilder, SortOrder
from core.auth_manager import AuthManager
from utils.data_provider import DataProvider, TestData
from utils.allure_helper import allure_feature, allure_story, allure_severity, allure_tag
from utils.retry_helper import retry_on_failure
from utils.faker_helper import faker_helper


@allure_feature("科目管理")
@allure_story("科目CRUD")
class TestSubject:
    """科目接口测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.api_client = ApiClient()
        cls.auth_manager = AuthManager(cls.api_client)
        cls.data_provider = DataProvider()
        cls.base_endpoint = "subjects"
        
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
    
    @pytest.fixture(scope="class")
    def user_id(self):
        """获取用户ID"""
        with allure.step(f"使用邮箱 {self.test_email} 登录获取用户ID"):
            response = self.auth_manager.login(self.test_email, self.test_password)
        
        with allure.step("验证响应"):
            if response.is_success:
                user_id = response.user['id']
                yield user_id
            else:
                # 如果登录失败，可能是测试环境未配置
                allure.attach(
                    "登录失败，可能是测试环境未配置",
                    "警告",
                    allure.attachment_type.TEXT
                )


    @pytest.fixture(scope="class")
    def subject_id(self):
        """创建科目并返回 subject_id"""
        with allure.step("准备测试数据"):
            subject_data = self._generate_subject_data("测试科目")
        
        with allure.step("创建科目"):
            response = self.api_client.post(
                endpoint=self.base_endpoint,
                json_data=subject_data
            )
        
        with allure.step("获取 subject_id"):
            if response.is_success:
                subject_id = response.json()['id']
                yield subject_id
                
                # 清理：删除创建的科目
                with allure.step("清理测试数据"):
                    self.api_client.delete(
                        endpoint=f"{self.base_endpoint}?id=eq.{subject_id}"
                    )
            else:
                allure.attach(
                    "创建科目失败，无法获取 subject_id",
                    "警告",
                    allure.attachment_type.TEXT
                )
                yield None

    def _generate_subject_data(self, user_id, name: str = None):
        """生成测试科目数据"""
        return {
            "user_id": user_id,
            "name": name or f"科目_{uuid.uuid4().hex[:6]}"
        }
    

    @allure_severity("critical")
    @allure_tag("smoke", "positive")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.subject
    def test_create_subject(self):
        """测试创建科目"""
        with allure.step("准备测试数据"):
            user_id = self.auth_manager.get_user_id()
            subject_data = self._generate_subject_data(user_id, "编程")
            allure.attach(
                str(subject_data),
                "请求数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送创建请求"):
            response = self.api_client.post(
                endpoint=self.base_endpoint,
                json_data=subject_data
            )
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            assert response.status_code in [200, 201]
            if response.is_success and isinstance(response.data, dict):
                handler.assert_field_exists('id')
                handler.assert_field_exists('name')
                assert response.json()['name'] == subject_data['name']



    @allure_severity("normal")
    @allure_tag("positive")
    @pytest.mark.positive
    @pytest.mark.subject
    def test_batch_create_subjects(self):
        """测试批量创建科目"""
        with allure.step("准备批量数据"):
            user_id = self.auth_manager.get_user_id()
            subjects = [
                self._generate_subject_data(user_id, "数学"),
                self._generate_subject_data(user_id, "英语"),
                self._generate_subject_data(user_id, "物理")
            ]
        
        with allure.step("发送批量创建请求"):
            response = self.api_client.post(
                endpoint=self.base_endpoint,
                json_data=subjects
            )
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            assert response.status_code in [200, 201]
           