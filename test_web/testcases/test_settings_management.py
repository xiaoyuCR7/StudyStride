import pytest
from pages.settings_page import SettingsPage
from playwright.sync_api import Page
from utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.nondestructive
class TestSettingsManagement:
    """设置管理功能测试"""
    
    def test_set_reminder_interval(self, page: Page):
        """测试设置提醒间隔功能"""
        logger.info("测试设置提醒间隔功能")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        settings_page.set_reminder_interval(45)
        logger.debug("设置提醒间隔为45分钟")
        
        assert "设置已保存" in settings_page.get_toast_message()
        logger.info("提醒间隔设置成功")
    
    def test_export_data(self, page: Page):
        """测试导出数据功能"""
        logger.info("测试导出数据功能")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        settings_page.export_data()
        logger.debug("点击导出数据按钮")
        assert settings_page.is_visible(".modal")
        assert "数据导出成功" in settings_page.get_toast_message()
        logger.info("数据导出成功")
    
    def test_data_management_tab_switch(self, page: Page):
        """测试数据管理标签切换功能"""
        logger.info("测试数据管理标签切换功能")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        settings_page.switch_to_data_management()
        logger.debug("切换到数据管理标签")
        assert settings_page.is_visible(settings_page.export_data_button)
        
        settings_page.switch_to_notification_settings()
        logger.debug("切换到通知设置标签")
        assert settings_page.is_visible(settings_page.reminder_interval_input)
        logger.info("标签切换测试成功")
