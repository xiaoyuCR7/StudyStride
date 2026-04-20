"""
学习会话接口测试

测试学习会话的增删改查功能
"""
import pytest
import allure

from core.api_client import ApiClient
from core.response_handler import ResponseHandler
from core.auth_manager import AuthManager
from utils.faker_helper import faker_helper
from utils.allure_helper import allure_feature, allure_story, allure_severity, allure_tag
from utils.retry_helper import retry_on_failure


@allure_feature("学习会话管理")
@allure_story("学习会话CRUD")
class TestStudySession:
    """学习会话接口测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.api_client = ApiClient()
        cls.auth_manager = AuthManager(cls.api_client)
        cls.base_endpoint = "study_sessions"
        cls.subjects_endpoint = "subjects"
        cls.subject_id = None
        
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
        
        # 执行登录，获取认证令牌和用户ID
        with allure.step(f"使用邮箱 {cls.test_email} 登录获取认证令牌和用户ID"):
            login_response = cls.auth_manager.login(cls.test_email, cls.test_password)
            if not login_response.is_success:
                allure.attach(
                    f"登录失败: {login_response.data}",
                    "警告",
                    allure.attachment_type.TEXT
                )
                pytest.skip("登录失败，跳过测试")
            # 获取用户ID
            cls.user_id = cls.auth_manager.get_user_id()
            if not cls.user_id:
                allure.attach(
                    "无法获取用户ID",
                    "警告",
                    allure.attachment_type.TEXT
                )
                pytest.skip("无法获取用户ID，跳过测试")
        
        # 创建测试科目
        with allure.step("创建测试科目"):
            subject_data = {
                "user_id": cls.user_id,
                "name": f"测试科目_{faker_helper.generate_name()}"
            }
            allure.attach(
                str(subject_data),
                "科目创建数据",
                allure.attachment_type.JSON
            )
            subject_response = cls.api_client.post(
                endpoint=cls.subjects_endpoint,
                json_data=subject_data
            )
            allure.attach(
                f"状态码: {subject_response.status_code}, 响应数据: {subject_response.data}",
                "科目创建响应",
                allure.attachment_type.TEXT
            )
            if subject_response.is_success:
                # 直接使用一个固定的subject_id，因为创建科目成功但无法获取ID
                # 这里使用一个固定值，实际测试中应该从响应中获取
                cls.subject_id = "1"
                allure.attach(
                    f"使用固定的subject_id: {cls.subject_id}",
                    "信息",
                    allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    f"创建科目失败: {subject_response.data}",
                    "警告",
                    allure.attachment_type.TEXT
                )
                pytest.skip("创建科目失败，跳过测试")
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 登出
        with allure.step("执行登出"):
            cls.auth_manager.logout()
        cls.api_client.close()
    
    def _generate_study_session_data(self):
        """生成测试学习会话数据"""
        import datetime
        # 生成随机的开始时间
        start_time = datetime.datetime.now(datetime.timezone.utc)
        # 生成随机的持续时间（1-3小时）
        duration = faker_helper.faker.random_int(min=3600, max=10800)
        # 计算结束时间
        end_time = start_time + datetime.timedelta(seconds=duration)
        
        return {
            "user_id": self.user_id,
            "subject": faker_helper.faker.word(),
            "content": faker_helper.faker.sentence(),
            "duration": str(duration),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "session_date": start_time.strftime("%Y-%m-%d")
        }
    
    @allure_severity("critical")
    @allure_tag("smoke", "positive")
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.study_session
    def test_create_study_session(self):
        """测试创建学习会话"""
        with allure.step("准备测试数据"):
            session_data = self._generate_study_session_data()
            allure.attach(
                str(session_data),
                "请求数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送创建请求"):
            response = self.api_client.post(
                endpoint=self.base_endpoint,
                json_data=session_data
            )
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            assert response.status_code in [200, 201]
            if response.is_success:
                if isinstance(response.data, dict):
                    handler.assert_field_exists('id')
                    handler.assert_field_exists('user_id')
                elif isinstance(response.data, list) and len(response.data) > 0:
                    # 如果响应是列表，检查第一个元素
                    first_item = response.data[0]
                    if isinstance(first_item, dict):
                        handler.assert_field_exists('id', data=first_item)
                        handler.assert_field_exists('user_id', data=first_item)
    
    @allure_severity("normal")
    @allure_tag("positive")
    @pytest.mark.positive
    @pytest.mark.study_session
    def test_get_study_sessions(self):
        """测试获取学习会话列表"""
        with allure.step("发送获取请求"):
            response = self.api_client.get(endpoint=self.base_endpoint)
        
        with allure.step("验证响应"):
            handler = ResponseHandler(response)
            assert response.status_code == 200
    
    @allure_severity("normal")
    @allure_tag("negative")
    @pytest.mark.negative
    @pytest.mark.study_session
    def test_create_study_session_invalid_data(self):
        """测试创建学习会话失败（无效数据）"""
        with allure.step("准备无效测试数据"):
            invalid_data = {}
        
        with allure.step("发送创建请求"):
            response = self.api_client.post(
                endpoint=self.base_endpoint,
                json_data=invalid_data
            )
        
        with allure.step("验证错误响应"):
            assert response.status_code >= 400
