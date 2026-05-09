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
    
    def test_add_subject_on_homepage(self, page: Page):
        """测试在首页添加科目功能"""
        logger.info("测试在首页添加科目功能")
        home_page = HomePage(page)
        
        test_subject = f"测试科目_{int(time.time())}"
        logger.debug(f"添加科目: {test_subject}")
        home_page.add_subject(test_subject)
        
        time.sleep(0.5)
        assert home_page.is_subject_selected(test_subject)
        logger.info("在首页添加科目测试成功")
    
    def test_add_subject_on_settings(self, page: Page):
        """测试在设置页面添加科目功能"""
        logger.info("测试在设置页面添加科目功能")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        initial_count = settings_page.get_subject_count()
        logger.debug(f"初始科目数量: {initial_count}")
        
        test_subject = f"设置页面测试科目_{int(time.time())}"
        logger.debug(f"添加科目: {test_subject}")
        settings_page.add_subject(test_subject)
        
        time.sleep(0.5)
        final_count = settings_page.get_subject_count()
        logger.info(f"添加后科目数量: {final_count}")
        assert final_count == initial_count + 1
        assert settings_page.is_subject_present(test_subject)
        logger.info("在设置页面添加科目测试成功")
    
    def test_edit_subject(self, page: Page):
        """测试编辑科目功能"""
        logger.info("测试编辑科目功能")
        settings_page = SettingsPage(page)
        
        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        test_subject = f"编辑测试科目_{int(time.time())}"
        logger.debug(f"添加测试科目: {test_subject}")
        settings_page.add_subject(test_subject)
        
        new_subject_name = f"编辑后的科目_{int(time.time())}"
        logger.debug(f"编辑科目为新名称: {new_subject_name}")
        settings_page.edit_subject(0, new_subject_name)
        
        time.sleep(0.5)
        assert settings_page.is_subject_present(new_subject_name)
        logger.info("编辑科目测试成功")
    
    def test_delete_subject(self, page: Page):
        """测试删除科目功能"""
        logger.info("测试删除科目功能")
        settings_page = SettingsPage(page)

        page.click("a:has-text('设置')")
        settings_page.wait_for_load()
        
        test_subject = f"删除测试科目_{int(time.time())}"
        logger.debug(f"添加测试科目: {test_subject}")
        settings_page.add_subject(test_subject)
        
        initial_count = settings_page.get_subject_count()
        logger.debug(f"删除前科目数量: {initial_count}")
        
        settings_page.delete_subject(0)
        
        time.sleep(0.5)
        final_count = settings_page.get_subject_count()
        logger.info(f"删除后科目数量: {final_count}")
        assert final_count == initial_count - 1
        assert not settings_page.is_subject_present(test_subject)
        logger.info("删除科目测试成功")