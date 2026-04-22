import pytest
from pages.home_page import HomePage
from pages.history_page import HistoryPage
from pages.settings_page import SettingsPage
from playwright.sync_api import Page
from utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.nondestructive
class TestNavigation:
    """页面导航功能测试"""
    
    def test_home_to_history_navigation(self, page: Page):
        """测试从首页导航到历史记录页面"""
        logger.info("测试从首页导航到历史记录页面")
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        page.click("a:has-text('历史记录')")
        history_page.wait_for_load()
        
        assert history_page.is_visible(history_page.date_filter)
        logger.info("导航到历史记录页面成功")
    
    def test_home_to_settings_navigation(self, page: Page):
        """测试从首页导航到设置页面"""
        logger.info("测试从首页导航到设置页面")
        home_page = HomePage(page)
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        assert settings_page.is_visible(settings_page.subject_management_tab)
        logger.info("导航到设置页面成功")
    
    def test_history_to_home_navigation(self, page: Page):
        """测试从历史记录页面导航到首页"""
        logger.info("测试从历史记录页面导航到首页")
        page.click("a:has-text('历史记录')")
        
        page.click("a:has-text('首页')")
        home_page = HomePage(page)
        home_page.wait_for_load()
        
        assert home_page.is_visible(home_page.start_button)
        logger.info("导航到首页成功")
    
    def test_settings_to_home_navigation(self, page: Page):
        """测试从设置页面导航到首页"""
        logger.info("测试从设置页面导航到首页")
        page.click("a:has-text('设置')")
        
        page.click("a:has-text('首页')")
        home_page = HomePage(page)
        home_page.wait_for_load()
        
        assert home_page.is_visible(home_page.start_button)
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
        assert settings_page.is_visible(settings_page.subject_management_tab)
        logger.debug("历史记录 -> 设置")
        
        page.click("a:has-text('首页')")
        home_page = HomePage(page)
        home_page.wait_for_load()
        assert home_page.is_visible(home_page.start_button)
        logger.info("完整导航循环测试成功")
