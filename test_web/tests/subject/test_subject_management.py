import pytest
from pages.home_page import HomePage
from pages.settings_page import SettingsPage
from playwright.sync_api import Page
import time

@pytest.mark.nondestructive
class TestSubjectManagement:
    """科目管理功能测试"""
    
    def test_add_subject(self, page: Page):
        """测试添加科目功能"""
        home_page = HomePage(page)
        settings_page = SettingsPage(page)
        
        # 导航到设置页面
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        # 切换到科目管理
        settings_page.switch_to_subject_management()
        initial_count = settings_page.get_subject_count()
        
        # 导航回首页
        page.click("a:has-text('首页')")
        home_page.wait_for_load()
        
        # 添加科目
        test_subject = f"测试科目_{int(time.time())}"
        home_page.add_subject(test_subject)
        
        # 导航到设置页面查看科目是否添加成功
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        settings_page.switch_to_subject_management()
        
        # 检查科目数量是否增加
        assert settings_page.get_subject_count() == initial_count + 1
    
    def test_edit_subject(self, page: Page):
        """测试编辑科目功能"""
        home_page = HomePage(page)
        settings_page = SettingsPage(page)
        
        # 先添加一个科目
        test_subject = f"编辑测试科目_{int(time.time())}"
        home_page.add_subject(test_subject)
        
        # 导航到设置页面
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        settings_page.switch_to_subject_management()
        
        # 编辑科目
        new_subject_name = f"编辑后的科目_{int(time.time())}"
        settings_page.edit_subject(0, new_subject_name)
        
        # 检查提示消息
        assert "科目更新成功" in settings_page.get_toast_message()
    
    def test_delete_subject(self, page: Page):
        """测试删除科目功能"""
        home_page = HomePage(page)
        settings_page = SettingsPage(page)
        
        # 先添加一个科目
        test_subject = f"删除测试科目_{int(time.time())}"
        home_page.add_subject(test_subject)
        
        # 导航到设置页面
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        settings_page.switch_to_subject_management()
        initial_count = settings_page.get_subject_count()
        
        # 删除科目
        settings_page.delete_subject(0)
        
        # 检查科目数量是否减少
        assert settings_page.get_subject_count() == initial_count - 1
        # 检查提示消息
        assert "科目删除成功" in settings_page.get_toast_message()
