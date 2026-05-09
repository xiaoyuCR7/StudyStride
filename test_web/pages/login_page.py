import time
from pages.base_page import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    """登录页面类"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = "#email"
        self.password_input = "#password"
        self.login_button = "button[type='submit']"
        self.register_button = "button.secondary"
        self.error_message = ".error"
        self.info_message = ".info"
        self.back_link = "a.back"
        self.login_form = ".login-form"
    
    def navigate(self):
        """导航到登录页面"""
        self.page.click("a:has-text('登录')")
        self.wait_for_load()
    
    def wait_for_load(self):
        """等待页面加载完成"""
        self.page.wait_for_selector(self.login_form, timeout=10000)
    
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
    
    def is_login_success(self) -> bool:
        """检查登录是否成功（通过检查导航栏中是否有用户菜单）"""
        self.page.wait_for_load_state("networkidle")
        time.sleep(4)
        return self.page.is_visible("button.user-menu-trigger.no-avatar")
    
    def go_back(self):
        """返回首页"""
        self.click(self.back_link)