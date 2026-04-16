import pytest
from pages.settings_page import SettingsPage
from playwright.sync_api import Page

@pytest.mark.nondestructive
class TestSettingsManagement:
    """设置管理功能测试"""
    
    def test_set_reminder_interval(self, page: Page):
        """测试设置提醒间隔功能"""
        settings_page = SettingsPage(page)
        
        # 导航到设置页面
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        # 设置提醒间隔
        settings_page.set_reminder_interval(45)
        
        # 检查提示消息
        assert "设置已保存" in settings_page.get_toast_message()
    
    def test_export_data(self, page: Page):
        """测试导出数据功能"""
        settings_page = SettingsPage(page)
        
        # 导航到设置页面
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        # 导出数据
        settings_page.export_data()
        # 这里可以添加文件下载的检查
        # 由于文件下载是异步的，这里只测试按钮点击是否成功
        assert settings_page.is_visible(".modal")
        assert "数据导出成功" in settings_page.get_toast_message()
    
    def test_data_management_tab_switch(self, page: Page):
        """测试数据管理标签切换功能"""
        settings_page = SettingsPage(page)
        
        # 导航到设置页面
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        # 切换到数据管理标签
        settings_page.switch_to_data_management()
        
        # 检查导出数据按钮是否可见
        assert settings_page.is_visible(settings_page.export_data_button)
        
        # 切换到通知设置标签
        settings_page.switch_to_notification_settings()
        
        # 检查提醒间隔输入框是否可见
        assert settings_page.is_visible(settings_page.reminder_interval_input)
