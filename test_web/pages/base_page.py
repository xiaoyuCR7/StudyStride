from playwright.sync_api import Page
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import config

class BasePage:
    """页面对象基类"""
    
    def __init__(self, page: Page):
        self.page = page
        self.timeout = config.TIMEOUT
    
    def wait_for_load(self):
        """等待页面加载完成"""
        self.page.wait_for_load_state("networkidle", timeout=self.timeout * 1000)
    
    def click(self, locator: str):
        """点击元素"""
        self.page.click(locator, timeout=self.timeout * 1000)
    
    def fill(self, locator: str, text: str):
        """填写文本"""
        self.page.fill(locator, text, timeout=self.timeout * 1000)
    
    def select_option(self, locator: str, value: str):
        """选择下拉选项"""
        self.page.select_option(locator, value, timeout=self.timeout * 1000)
    
    def get_text(self, locator: str) -> str:
        """获取元素文本"""
        return self.page.inner_text(locator, timeout=self.timeout * 1000)
    
    def is_visible(self, locator: str) -> bool:
        """检查元素是否可见"""
        try:
            self.page.wait_for_selector(locator, timeout=2000)
            return True
        except:
            return False
    
    def navigate_to(self, url: str):
        """导航到指定URL"""
        self.page.goto(url, timeout=self.timeout * 1000)
        self.wait_for_load()
    
    def wait_for_selector(self, locator: str, timeout: int = None):
        """等待元素出现"""
        if timeout is None:
            timeout = self.timeout
        self.page.wait_for_selector(locator, timeout=timeout * 1000)
    
    def get_attribute(self, locator: str, attribute: str) -> str:
        """获取元素属性"""
        return self.page.get_attribute(locator, attribute, timeout=self.timeout * 1000)
    
    def wait_for_url(self, url: str, timeout: int = None):
        """等待URL变化"""
        if timeout is None:
            timeout = self.timeout
        self.page.wait_for_url(url, timeout=timeout * 1000)
