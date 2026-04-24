from pages.base_page import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    """登录页面类"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = "#email"
        self.password_input = "#password"
        self.login_button = "button:has-text('登录')"
        self.register_button = "button:has-text('注册')"
        self.error_message = ".error"
        self.info_message = ".info"
        self.login_success = "span.navbar-email"
    
    def navigate(self):
        """导航到登录页面"""
        self.page.click("a:has-text('登录')")
        self.wait_for_load()
    
    def wait_for_load(self):
        """等待页面加载完成"""
        self.page.wait_for_selector(self.email_input, timeout=10000)
    
    def login(self, email: str, password: str):
        """登录操作"""
        self.page.fill(self.email_input, email)
        self.page.fill(self.password_input, password)
        self.page.click(self.login_button)
    
    def register(self, email: str, password: str):
        """注册操作"""
        self.page.fill(self.email_input, email)
        self.page.fill(self.password_input, password)
        self.page.click(self.register_button)
    
    def get_error_message(self) -> str:
        """获取错误消息"""
        if self.page.is_visible(self.error_message):
            return self.page.inner_text(self.error_message)
        return ""
    
    def get_info_message(self) -> str:
        """获取信息消息"""
        if self.page.is_visible(self.info_message):
            return self.page.inner_text(self.info_message)
        return ""

    def is_login_success(self, email: str = None) -> bool:
        """检查登录是否成功（通过登录成功后的邮箱判断）"""
        if email:
            return self.page.is_visible(self.login_success) and email in self.page.inner_text(self.login_success)
        return self.page.is_visible(self.login_success)
