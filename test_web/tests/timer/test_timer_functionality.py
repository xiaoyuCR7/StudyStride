import pytest
from pages.home_page import HomePage
from playwright.sync_api import Page
import time

@pytest.mark.nondestructive
class TestTimerFunctionality:
    """计时器功能测试"""
    
    def test_start_pause_resume_stop_timer(self, page: Page):
        """测试计时器的开始、暂停、继续和结束功能"""
        home_page = HomePage(page)
        
        # 开始计时
        home_page.start_timer()
        time.sleep(2)  # 等待2秒
        
        # 检查计时器是否正在运行
        initial_time = home_page.get_timer_display()
        assert initial_time != "00:00:00"
        
        # 暂停计时
        home_page.pause_timer()
        paused_time = home_page.get_timer_display()
        time.sleep(1)  # 等待1秒
        
        # 检查计时器是否暂停
        assert home_page.get_timer_display() == paused_time
        
        # 继续计时
        home_page.continue_timer()
        time.sleep(1)  # 等待1秒
        
        # 检查计时器是否继续运行
        assert home_page.get_timer_display() != paused_time
        
        # 结束计时
        home_page.stop_timer()
        time.sleep(1)  # 等待1秒
        
        # 检查计时器是否重置
        assert home_page.get_timer_display() == "00:00:00"
    
    def test_timer_display_format(self, page: Page):
        """测试计时器显示格式是否正确"""
        home_page = HomePage(page)
        
        # 开始计时
        home_page.start_timer()
        time.sleep(1)  # 等待1秒
        
        # 检查计时器显示格式
        timer_display = home_page.get_timer_display()
        assert len(timer_display) == 8  # HH:MM:SS格式
        assert timer_display.count(":") == 2  # 应该有两个冒号
        
        # 结束计时
        home_page.stop_timer()
