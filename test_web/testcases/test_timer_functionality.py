import pytest
from pages.home_page import HomePage
from playwright.sync_api import Page
import time
from utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.nondestructive
class TestTimerFunctionality:
    """计时器功能测试"""
    
    def test_start_pause_resume_stop_timer(self, page: Page):
        """测试计时器的开始、暂停、继续和结束功能"""
        logger.info("测试计时器的开始、暂停、继续和结束功能")
        home_page = HomePage(page)
        
        home_page.start_timer()
        logger.debug("开始计时")
        time.sleep(2)
        
        initial_time = home_page.get_timer_display()
        logger.debug(f"初始时间: {initial_time}")
        assert initial_time != "00:00:00"
        
        home_page.pause_timer()
        logger.debug("暂停计时")
        paused_time = home_page.get_timer_display()
        time.sleep(1)
        
        assert home_page.get_timer_display() == paused_time
        logger.debug("验证暂停成功")
        
        home_page.continue_timer()
        logger.debug("继续计时")
        time.sleep(1)
        
        assert home_page.get_timer_display() != paused_time
        logger.debug("验证继续成功")
        
        home_page.stop_timer()
        logger.debug("结束计时")
        time.sleep(1)
        
        assert home_page.get_timer_display() == "00:00:00"
        logger.info("计时器功能测试成功")
    
    def test_timer_display_format(self, page: Page):
        """测试计时器显示格式是否正确"""
        logger.info("测试计时器显示格式是否正确")
        home_page = HomePage(page)
        
        home_page.start_timer()
        logger.debug("开始计时")
        time.sleep(1)
        
        timer_display = home_page.get_timer_display()
        logger.debug(f"计时器显示: {timer_display}")
        assert len(timer_display) == 8
        assert timer_display.count(":") == 2
        logger.debug("验证格式正确")
        
        home_page.stop_timer()
        logger.info("计时器显示格式测试成功")
