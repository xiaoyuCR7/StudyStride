import pytest
from pages.home_page import HomePage
from pages.settings_page import SettingsPage
from playwright.sync_api import Page
import time
from utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.nondestructive
class TestSubjectManagement:
    """科目管理功能测试"""
    
    def test_add_subject(self, page: Page):
        """测试添加科目功能"""
        logger.info("测试添加科目功能")
        home_page = HomePage(page)
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        settings_page.switch_to_subject_management()
        initial_count = settings_page.get_subject_count()
        logger.debug(f"初始科目数量: {initial_count}")
        
        page.click("a:has-text('首页')")
        home_page.wait_for_load()
        
        test_subject = f"测试科目_{int(time.time())}"
        logger.debug(f"添加科目: {test_subject}")
        home_page.add_subject(test_subject)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        settings_page.switch_to_subject_management()
        
        final_count = settings_page.get_subject_count()
        logger.info(f"添加后科目数量: {final_count}")
        assert final_count == initial_count + 1
        logger.info("添加科目测试成功")
    
    def test_edit_subject(self, page: Page):
        """测试编辑科目功能"""
        logger.info("测试编辑科目功能")
        home_page = HomePage(page)
        settings_page = SettingsPage(page)
        
        test_subject = f"编辑测试科目_{int(time.time())}"
        logger.debug(f"添加测试科目: {test_subject}")
        home_page.add_subject(test_subject)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        settings_page.switch_to_subject_management()
        
        new_subject_name = f"编辑后的科目_{int(time.time())}"
        logger.debug(f"编辑科目为新名称: {new_subject_name}")
        settings_page.edit_subject(0, new_subject_name)
        
        assert "科目更新成功" in settings_page.get_toast_message()
        logger.info("编辑科目测试成功")
    
    def test_delete_subject(self, page: Page):
        """测试删除科目功能"""
        logger.info("测试删除科目功能")
        home_page = HomePage(page)
        settings_page = SettingsPage(page)
        
        test_subject = f"删除测试科目_{int(time.time())}"
        logger.debug(f"添加测试科目: {test_subject}")
        home_page.add_subject(test_subject)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        settings_page.switch_to_subject_management()
        initial_count = settings_page.get_subject_count()
        logger.debug(f"删除前科目数量: {initial_count}")
        
        settings_page.delete_subject(0)
        
        final_count = settings_page.get_subject_count()
        logger.info(f"删除后科目数量: {final_count}")
        assert final_count == initial_count - 1
        assert "科目删除成功" in settings_page.get_toast_message()
        logger.info("删除科目测试成功")
