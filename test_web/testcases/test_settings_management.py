import pytest
from pages.settings_page import SettingsPage
from playwright.sync_api import Page
import time
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
        
        time.sleep(1)
        toast_message = settings_page.get_toast_message()
        assert "设置已保存" in toast_message
        logger.info("提醒间隔设置成功")
    
    def test_export_data(self, page: Page):
        """测试导出数据功能"""
        logger.info("测试导出数据功能")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        settings_page.export_data()
        logger.debug("点击导出数据按钮")
        
        time.sleep(1)
        assert settings_page.is_visible(settings_page.toast_modal)
        assert "数据导出成功" in settings_page.get_toast_message()
        logger.info("数据导出成功")
    
    def test_notification_permission_section(self, page: Page):
        """测试通知权限设置区域"""
        logger.info("测试通知权限设置区域")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        assert settings_page.is_visible(settings_page.notification_setting_section)
        logger.info("通知权限设置区域测试成功")
    
    def test_data_management_section(self, page: Page):
        """测试数据管理区域"""
        logger.info("测试数据管理区域")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        assert settings_page.is_visible(settings_page.data_management_section)
        assert settings_page.is_visible(settings_page.export_data_button)
        assert settings_page.is_visible(settings_page.import_data_button)
        assert settings_page.is_visible(settings_page.clear_data_button)
        logger.info("数据管理区域测试成功")
    
    def test_all_settings_sections_visible(self, page: Page):
        """测试所有设置区域是否可见"""
        logger.info("测试所有设置区域是否可见")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        assert settings_page.is_visible(settings_page.reminder_setting_section)
        assert settings_page.is_visible(settings_page.subject_management_section)
        assert settings_page.is_visible(settings_page.notification_setting_section)
        assert settings_page.is_visible(settings_page.data_management_section)
        logger.info("所有设置区域可见性测试成功")