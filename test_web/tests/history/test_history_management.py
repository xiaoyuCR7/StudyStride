import pytest
from pages.home_page import HomePage
from pages.history_page import HistoryPage
from playwright.sync_api import Page
from datetime import datetime

@pytest.mark.nondestructive
class TestHistoryManagement:
    """历史记录管理功能测试"""
    
    def test_quick_record(self, page: Page):
        """测试快速记录功能"""
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        # 快速记录学习会话
        test_subject = "未分类"
        home_page.quick_record_session(test_subject, "1", "30", "测试快速记录功能")
        
        # 导航到历史记录页面
        page.click("a:has-text('历史记录')")
        history_page.wait_for_load()
        
        # 检查是否有记录
        assert history_page.get_session_count() > 0
    
    def test_edit_session(self, page: Page):
        """测试编辑历史记录功能"""
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        # 先创建一条记录
        home_page.quick_record_session("未分类", "0", "30", "测试历史记录管理")
        
        # 导航到历史记录页面
        page.click("a:has-text('历史记录')")
        history_page.wait_for_load()
        
        # 编辑第一条记录
        history_page.edit_session(0)
        history_page.save_edit("未分类", "1", "0", "编辑后的内容")
        
        # 检查提示消息
        assert "学习记录已更新成功" in history_page.get_toast_message()
    
    def test_delete_session(self, page: Page):
        """测试删除历史记录功能"""
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        # 先创建一条记录
        home_page.quick_record_session("未分类", "0", "30", "测试删除功能")
        
        # 导航到历史记录页面
        page.click("a:has-text('历史记录')")
        history_page.wait_for_load()
        
        # 检查记录数量
        initial_count = history_page.get_session_count()
        assert initial_count > 0
        
        # 删除第一条记录
        history_page.delete_session(0)
        history_page.confirm_delete()
        
        # 检查记录数量是否减少
        assert history_page.get_session_count() == initial_count - 1
        # 检查提示消息
        assert "学习记录已删除" in history_page.get_toast_message()
    
    def test_filter_by_date(self, page: Page):
        """测试按日期筛选功能"""
        home_page = HomePage(page)
        history_page = HistoryPage(page)
        
        # 创建一条记录
        today = datetime.now().strftime("%Y-%m-%d")
        home_page.quick_record_session("未分类", "0", "10", "今天的记录")
        
        # 导航到历史记录页面
        page.click("a:has-text('历史记录')")
        history_page.wait_for_load()
        
        # 按日期筛选
        history_page.filter_by_date(today)
        
        # 检查是否有记录
        assert history_page.get_session_count() > 0
        
        # 显示全部
        history_page.show_all()
        
        # 检查记录数量
        assert history_page.get_session_count() > 0
