import pytest
from pages.home_page import HomePage
from pages.history_page import HistoryPage
from pages.settings_page import SettingsPage
from pages.community_page import CommunityPage
from pages.login_page import LoginPage
import time
from playwright.sync_api import Page
from utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.nondestructive
class TestNavigation:
    """页面导航功能测试"""
    
    @classmethod
    def setup_class(cls):
        """类级别的setup，生成测试账号"""
        cls.test_email = "test1@qq.com"
        cls.test_password = "Test123456"

    def test_home_to_history_navigation(self, page: Page):
        """测试从首页导航到历史记录页面"""
        logger.info("测试从首页导航到历史记录页面")
        history_page = HistoryPage(page)
        
        page.click("a:has-text('历史记录')")
        history_page.wait_for_load()
        
        assert history_page.is_visible(history_page.date_filter)
        logger.info("导航到历史记录页面成功")
    
    def test_home_to_settings_navigation(self, page: Page):
        """测试从首页导航到设置页面"""
        logger.info("测试从首页导航到设置页面")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        assert settings_page.is_visible(settings_page.subject_management_section)
        logger.info("导航到设置页面成功")
    
    def test_home_to_community_navigation(self, page: Page):
        """测试从首页导航到社区页面"""
        logger.info("测试从首页导航到社区页面")
        community_page = CommunityPage(page)

        # 先登录
        login_page = LoginPage(page)
        page.click("a:has-text('登录')")
        time.sleep(2)
        login_page.login(self.test_email, self.test_password)
        time.sleep(10)

        page.click("a:has-text('学习社区')")
        community_page.wait_for_load()
        
        assert community_page.is_visible(community_page.community_header)
        logger.info("导航到社区页面成功")
    
    def test_history_to_home_navigation(self, page: Page):
        """测试从历史记录页面导航到首页"""
        logger.info("测试从历史记录页面导航到首页")
        
        page.click("a:has-text('历史记录')")
        
        page.click("a:has-text('首页')")
        home_page = HomePage(page)
        home_page.wait_for_load()
        
        assert home_page.is_visible(home_page.timer_container)
        logger.info("导航到首页成功")
    
    def test_settings_to_home_navigation(self, page: Page):
        """测试从设置页面导航到首页"""
        logger.info("测试从设置页面导航到首页")
        page.click("a:has-text('设置')")
        
        page.click("a:has-text('首页')")
        home_page = HomePage(page)
        home_page.wait_for_load()
        
        assert home_page.is_visible(home_page.timer_container)
        logger.info("导航到首页成功")
    
    def test_community_to_home_navigation(self, page: Page):
        """测试从社区页面导航到首页"""
        logger.info("测试从社区页面导航到首页")
        community_page = CommunityPage(page)
        
        # 先登录
        login_page = LoginPage(page)
        page.click("a:has-text('登录')")
        time.sleep(2)
        login_page.login(self.test_email, self.test_password)
        time.sleep(10)
        
        page.click("a:has-text('学习社区')")
        assert community_page.is_visible(community_page.community_header)

        page.click("a:has-text('首页')")
        home_page = HomePage(page)
        home_page.wait_for_load()
        
        assert home_page.is_visible(home_page.timer_container)
        logger.info("导航到首页成功")
    
    def test_full_navigation_cycle(self, page: Page):
        """测试完整的导航循环"""
        logger.info("测试完整的导航循环")
        
        page.click("a:has-text('历史记录')")
        history_page = HistoryPage(page)
        history_page.wait_for_load()
        assert history_page.is_visible(history_page.date_filter)
        logger.debug("首页 -> 历史记录")
        
        page.click("a:has-text('设置')")
        settings_page = SettingsPage(page)
        settings_page.wait_for_load()
        assert settings_page.is_visible(settings_page.subject_management_section)
        logger.debug("历史记录 -> 设置")
        
        page.click("a:has-text('首页')")
        home_page = HomePage(page)
        home_page.wait_for_load()
        assert home_page.is_visible(home_page.timer_container)
        logger.info("完整导航循环测试成功")