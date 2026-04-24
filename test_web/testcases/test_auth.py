import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from playwright.sync_api import Page
from utils.faker_helper import faker_helper
from utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.nondestructive
@allure.feature("用户认证")
class TestAuthentication:
    """用户认证功能测试"""
    
    @classmethod
    def setup_class(cls):
        """类级别的setup，生成测试账号并注册"""
        # 生成测试账号
        cls.test_email = faker_helper.generate_email()
        cls.test_password = faker_helper.generate_password()
        logger.info(f"生成测试账号: {cls.test_email}")
    
    @allure.story("用户注册")
    @allure.description("测试新用户注册功能，验证用户能否成功注册并收到确认邮件")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_register_new_user(self, page: Page):
        """测试注册新用户"""
        with allure.step("开始测试新用户注册"):
            logger.info("测试注册新用户")
            login_page = LoginPage(page)
            
            with allure.step("导航到登录页面"):
                login_page.navigate()
                
            with allure.step(f"使用邮箱 {self.test_email} 注册新用户"):
                logger.debug(f"注册新用户: {self.test_email}")
                # 执行注册
                login_page.register(self.test_email, self.test_password)
                
            with allure.step("等待注册成功消息"):
                page.wait_for_selector(".info", timeout=5000)
                
            with allure.step("验证注册成功"):
                # 检查是否显示注册成功消息
                info_message = login_page.get_info_message()
                allure.attach(info_message, "注册成功消息", allure.attachment_type.TEXT)
                assert "请查收邮件" in info_message
                logger.info("注册测试成功")
                
            # 添加截图
            screenshot = page.screenshot()
            allure.attach(screenshot, "注册成功页面", allure.attachment_type.PNG)
    
    @allure.story("用户登录")
    @allure.description("测试使用有效凭证登录功能，验证用户能否成功登录系统")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_02_login_with_valid_credentials(self, page: Page):
        """测试使用有效凭证登录"""
        with allure.step("开始测试有效凭证登录"):
            logger.info("测试使用有效凭证登录")
            login_page = LoginPage(page)
            
            with allure.step("导航到登录页面"):
                login_page.navigate()
                
            with allure.step(f"使用账号 {self.test_email} 登录"):
                # 使用类级别的测试账号
                email = self.test_email
                password = self.test_password
                
                logger.debug(f"使用账号登录: {email}")
                # 执行登录
                login_page.login(email, password)
                
            with allure.step("等待页面加载完成"):
                # 等待页面跳转和加载
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)  # 额外等待2秒确保页面完全加载
                
            with allure.step("验证登录成功"):
                # 检查是否登录成功
                assert login_page.is_login_success(email)
                logger.info("登录测试成功")
                
            # 添加截图
            screenshot = page.screenshot()
            allure.attach(screenshot, "登录成功页面", allure.attachment_type.PNG)
    
    @allure.story("用户登录")
    @allure.description("测试使用无效凭证登录功能，验证系统是否正确拒绝无效登录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_03_login_with_invalid_credentials(self, page: Page):
        """测试使用无效凭证登录"""
        with allure.step("开始测试无效凭证登录"):
            logger.info("测试使用无效凭证登录")
            login_page = LoginPage(page)
            
            with allure.step("导航到登录页面"):
                login_page.navigate()
                
            with allure.step("生成并使用无效账号登录"):
                # 生成无效账号
                email = faker_helper.generate_email()
                password = faker_helper.generate_password()
                
                logger.debug(f"使用无效账号登录: {email}")
                # 执行登录
                login_page.login(email, password)
                
            with allure.step("等待错误消息"):
                # 等待错误消息
                page.wait_for_selector(".error", timeout=5000)
                
            with allure.step("验证登录失败"):
                # 检查是否显示错误消息
                error_message = login_page.get_error_message()
                allure.attach(error_message, "错误消息", allure.attachment_type.TEXT)
                assert error_message != ""
                logger.info(f"无效登录测试成功，错误消息: {error_message}")
                
            # 添加截图
            screenshot = page.screenshot()
            allure.attach(screenshot, "登录失败页面", allure.attachment_type.PNG)