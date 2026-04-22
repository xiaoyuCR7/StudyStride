import pytest
from pages.home_page import HomePage
from pages.history_page import HistoryPage
from playwright.sync_api import Page
from datetime import datetime
from utils.allure_helper import AllureHelper
from utils.logger import get_logger

allure_helper = AllureHelper()
logger = get_logger(__name__)

@pytest.mark.nondestructive
class TestHistoryManagement:
    """历史记录管理功能测试"""
    
    def test_quick_record(self, page: Page):
        """测试快速记录功能"""
        logger.info("开始测试快速记录功能")
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        with allure_helper.step("快速记录学习会话"):
            test_subject = "未分类"
            logger.debug(f"快速记录科目: {test_subject}")
            home_page.quick_record_session(test_subject, "1", "30", "测试快速记录功能")
            allure_helper.attach_screenshot(page, "快速记录会话")
        
        with allure_helper.step("等待会话保存完成"):
            import time
            time.sleep(2)
        
        with allure_helper.step("导航到历史记录页面"):
            page.click("a:has-text('历史记录')")
            history_page.wait_for_load()
            history_page.wait_for_sessions()
            allure_helper.attach_screenshot(page, "历史记录页面")
        
        with allure_helper.step("检查是否有记录"):
            session_count = history_page.get_session_count()
            logger.info(f"会话数量: {session_count}")
            allure_helper.attach_text(f"会话数量: {session_count}", "会话数量")
            assert session_count > 0
        logger.info("快速记录功能测试完成")
    
    def test_edit_session(self, page: Page):
        """测试编辑历史记录功能"""
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        with allure_helper.step("创建一条记录"):
            home_page.quick_record_session("未分类", "0", "30", "测试历史记录管理")
            allure_helper.attach_screenshot(page, "创建记录")
        
        with allure_helper.step("等待会话保存完成"):
            import time
            time.sleep(2)
        
        with allure_helper.step("导航到历史记录页面"):
            page.click("a:has-text('历史记录')")
            history_page.wait_for_load()
            # 等待会话项出现
            history_page.wait_for_sessions()
            allure_helper.attach_screenshot(page, "历史记录页面")
        
        with allure_helper.step("编辑第一条记录"):
            history_page.edit_session(0)
            allure_helper.attach_screenshot(page, "编辑记录")
            history_page.save_edit("未分类", "1", "0", "编辑后的内容")
        
        with allure_helper.step("检查提示消息"):
            toast_message = history_page.get_toast_message()
            allure_helper.attach_text(toast_message, "提示消息")
            assert "学习记录已更新成功" in toast_message
    
    def test_delete_session(self, page: Page):
        """测试删除历史记录功能"""
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        with allure_helper.step("创建一条记录"):
            home_page.quick_record_session("未分类", "0", "30", "测试删除功能")
            allure_helper.attach_screenshot(page, "创建记录")
        
        with allure_helper.step("等待会话保存完成"):
            import time
            time.sleep(2)
        
        with allure_helper.step("导航到历史记录页面"):
            page.click("a:has-text('历史记录')")
            history_page.wait_for_load()
            # 等待会话项出现
            history_page.wait_for_sessions()
            allure_helper.attach_screenshot(page, "历史记录页面")
        
        with allure_helper.step("检查初始记录数量"):
            initial_count = history_page.get_session_count()
            allure_helper.attach_text(f"初始会话数量: {initial_count}", "初始会话数量")
            assert initial_count > 0
        
        with allure_helper.step("删除第一条记录"):
            history_page.delete_session(0)
            allure_helper.attach_screenshot(page, "删除确认")
            history_page.confirm_delete()
        
        with allure_helper.step("检查记录数量是否减少"):
            final_count = history_page.get_session_count()
            allure_helper.attach_text(f"删除后会话数量: {final_count}", "删除后会话数量")
            assert final_count == initial_count - 1
        
        with allure_helper.step("检查提示消息"):
            toast_message = history_page.get_toast_message()
            allure_helper.attach_text(toast_message, "提示消息")
            assert "学习记录已删除" in toast_message
    
    def test_filter_by_date(self, page: Page):
        """测试按日期筛选功能"""
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        with allure_helper.step("创建一条记录"):
            today = datetime.now().strftime("%Y-%m-%d")
            home_page.quick_record_session("未分类", "0", "10", "今天的记录")
            allure_helper.attach_screenshot(page, "创建记录")
        
        with allure_helper.step("等待会话保存完成"):
            import time
            time.sleep(2)
        
        with allure_helper.step("导航到历史记录页面"):
            page.click("a:has-text('历史记录')")
            history_page.wait_for_load()
            # 等待会话项出现
            history_page.wait_for_sessions()
            allure_helper.attach_screenshot(page, "历史记录页面")
        
        with allure_helper.step("按日期筛选"):
            history_page.filter_by_date(today)
            allure_helper.attach_screenshot(page, "按日期筛选")
        
        with allure_helper.step("检查筛选后是否有记录"):
            filtered_count = history_page.get_session_count()
            allure_helper.attach_text(f"筛选后会话数量: {filtered_count}", "筛选后会话数量")
            assert filtered_count > 0
        
        with allure_helper.step("显示全部"):
            history_page.show_all()
            allure_helper.attach_screenshot(page, "显示全部")
        
        with allure_helper.step("检查全部记录数量"):
            all_count = history_page.get_session_count()
            allure_helper.attach_text(f"全部会话数量: {all_count}", "全部会话数量")
            assert all_count > 0
