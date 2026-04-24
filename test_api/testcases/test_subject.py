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
from utils.schema_validator import validate_schema
from utils.db_validator import DBValidator


@allure_feature("科目管理")
@allure_story("科目CRUD")
class TestSubject:
    """科目接口测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        from utils.logger import get_logger
        cls.logger = get_logger(__name__)
        cls.api_client = ApiClient()
        cls.auth_manager = AuthManager(cls.api_client)
        cls.data_provider = DataProvider()
        cls.db_validator = DBValidator(cls.api_client)
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

        with allure.step("验证响应"):
            if login_response.is_success:
                # 从响应数据中获取用户ID
                user_id = login_response.data['user']['id']
                cls.user_id = user_id
                allure.attach(
                    f"用户ID: {user_id}",
                    "登录信息",
                    allure.attachment_type.TEXT
                )
            else:
                # 如果登录失败，可能是测试环境未配置
                allure.attach(
                    "登录失败，可能是测试环境未配置",
                    "警告",
                    allure.attachment_type.TEXT
                )
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 登出
        with allure.step("执行登出"):
            cls.auth_manager.logout()
        cls.api_client.close()

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
            subject_data = self._generate_subject_data(self.user_id, "编程")
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
            
            # 记录到日志
            self.logger.info(f"响应状态码: {response.status_code}")
            self.logger.info(f"响应数据类型: {type(response.data).__name__}")
            self.logger.info(f"响应数据: {response.data}")
            
            assert response.status_code in [200, 201]
            
            # 处理不同的数据结构
            subject_id = None
            subject_name = None
            schema_validation_data = None
            
            if response.is_success:
                if isinstance(response.data, dict):
                    # 响应是字典
                    handler.assert_field_exists('id')
                    handler.assert_field_exists('name')
                    subject_id = response.data['id']
                    subject_name = response.data['name']
                    schema_validation_data = response.data
                    
                elif isinstance(response.data, list) and len(response.data) > 0:
                    # 响应是列表
                    first_item = response.data[0]
                    if isinstance(first_item, dict):
                        handler.assert_field_exists('id', data=first_item)
                        handler.assert_field_exists('name', data=first_item)
                        subject_id = first_item['id']
                        subject_name = first_item['name']
                        schema_validation_data = first_item
                
                elif isinstance(response.data, str) and response.data.strip() == '':
                    # 响应是空字符串（Supabase API 行为）
                    with allure.step("响应体为空，通过查询获取科目"):
                        # 通过用户 ID 和科目名称查询刚创建的科目
                        query_response = self.api_client.get(
                            endpoint=f"{self.base_endpoint}?user_id=eq.{self.user_id}&name=eq.{subject_data['name']}"
                        )
                        
                        if query_response.is_success and isinstance(query_response.data, list) and len(query_response.data) > 0:
                            first_item = query_response.data[0]
                            subject_id = first_item['id']
                            subject_name = first_item['name']
                            schema_validation_data = first_item
                            allure.attach(
                                f"通过查询获取到科目: {subject_id}",
                                "查询结果",
                                allure.attachment_type.TEXT
                            )
                        else:
                            allure.attach(
                                "无法通过查询获取科目",
                                "警告",
                                allure.attachment_type.TEXT
                            )
                
                # 验证科目名称
                if subject_name:
                    assert subject_name == subject_data['name'], f"科目名称不匹配: 期望 {subject_data['name']}, 实际 {subject_name}"
            
            # JSON Schema 校验（单独分开）
            if schema_validation_data:
                with allure.step("JSON Schema 校验"):
                    validate_schema(schema_validation_data, "subject")
            else:
                allure.attach(
                    "无法获取数据进行 JSON Schema 校验",
                    "警告",
                    allure.attachment_type.TEXT
                )
            
            # 数据库校验（单独分开）
            if subject_id:
                with allure.step("数据库校验"):
                    assert self.db_validator.validate_subject_exists(subject_id, subject_data)
                    
                    # 清理：删除创建的科目
                    with allure.step("清理测试数据"):
                        delete_response = self.api_client.delete(
                            endpoint=f"{self.base_endpoint}?id=eq.{subject_id}"
                        )
                        assert delete_response.status_code in [200, 204]
            else:
                allure.attach(
                    "无法获取 subject_id，跳过数据库校验和清理",
                    "警告",
                    allure.attachment_type.TEXT
                )



    @allure_severity("normal")
    @allure_tag("positive")
    @pytest.mark.positive
    @pytest.mark.subject
    def test_batch_create_subjects(self):
        """测试批量创建科目"""
        with allure.step("准备批量数据"):
            subjects = [
                self._generate_subject_data(self.user_id, "数学"),
                self._generate_subject_data(self.user_id, "英语"),
                self._generate_subject_data(self.user_id, "物理")
            ]
        
        with allure.step("发送批量创建请求"):
            response = self.api_client.post(
                endpoint=self.base_endpoint,
                json_data=subjects
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
                for i, item in enumerate(response.data):
                    if isinstance(item, dict):
                        debug_info += f"第 {i} 个元素键: {list(item.keys())}\n"
                        debug_info += f"第 {i} 个元素内容: {item}\n"
            
            allure.attach(
                debug_info,
                "响应信息",
                allure.attachment_type.TEXT
            )
            
            assert response.status_code in [200, 201]
            
            # 处理不同的数据结构
            subject_ids = []
            schema_validation_items = []
            
            if response.is_success:
                if isinstance(response.data, list) and len(response.data) > 0:
                    # 响应是列表
                    for item in response.data:
                        if isinstance(item, dict) and 'id' in item:
                            subject_ids.append(item['id'])
                            schema_validation_items.append(item)
                elif isinstance(response.data, dict):
                    # 响应是字典（单个对象）
                    if 'id' in response.data:
                        subject_ids.append(response.data['id'])
                        schema_validation_items.append(response.data)
                
                # 如果响应为空或我们没有获取到ID，通过查询获取
                if not subject_ids or (isinstance(response.data, str) and response.data.strip() == ''):
                    with allure.step("响应体为空或没有获取到ID，通过查询获取科目"):
                        # 按科目名称查询
                        for subject_data in subjects:
                            query_response = self.api_client.get(
                                endpoint=f"{self.base_endpoint}?user_id=eq.{self.user_id}&name=eq.{subject_data['name']}"
                            )
                            
                            if query_response.is_success and isinstance(query_response.data, list) and len(query_response.data) > 0:
                                first_item = query_response.data[0]
                                if 'id' in first_item:
                                    subject_ids.append(first_item['id'])
                                    schema_validation_items.append(first_item)
                        allure.attach(
                            f"通过查询获取到科目数量: {len(subject_ids)}",
                            "查询结果",
                            allure.attachment_type.TEXT
                        )
            
            # JSON Schema 校验（单独分开）
            if schema_validation_items:
                with allure.step("JSON Schema 校验"):
                    for i, item in enumerate(schema_validation_items):
                        validate_schema(item, "subject")
                        allure.attach(
                            f"第 {i} 个科目 JSON Schema 校验通过",
                            "成功",
                            allure.attachment_type.TEXT
                        )
            else:
                allure.attach(
                    "无法获取数据进行 JSON Schema 校验",
                    "警告",
                    allure.attachment_type.TEXT
                )
            
            # 数据库校验（单独分开）
            if subject_ids:
                with allure.step("数据库校验"):
                    for i, subject_id in enumerate(subject_ids):
                        expected_data = subjects[i] if i < len(subjects) else subjects[0]
                        assert self.db_validator.validate_subject_exists(subject_id, expected_data)
                    
                    # 清理：删除创建的科目
                    with allure.step("清理测试数据"):
                        for subject_id in subject_ids:
                            delete_response = self.api_client.delete(
                                endpoint=f"{self.base_endpoint}?id=eq.{subject_id}"
                            )
                            assert delete_response.status_code in [200, 204]
            else:
                allure.attach(
                    "无法获取 subject_ids，跳过数据库校验和清理",
                    "警告",
                    allure.attachment_type.TEXT
                )
           