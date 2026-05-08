import pytest
from pages.community_page import CommunityPage
from pages.login_page import LoginPage
from playwright.sync_api import Page
import time
from utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.nondestructive
class TestCommunity:
    """学习社区功能测试"""
    
    @classmethod
    def setup_class(cls):
        """类级别的setup，生成测试账号"""
        cls.test_email = "test1@qq.com"
        cls.test_password = "Test123456"
    
    def test_community_page_load(self, page: Page):
        """测试社区页面加载"""
        logger.info("测试社区页面加载")
        
        # 先登录
        login_page = LoginPage(page)
        page.click("a:has-text('登录')")
        time.sleep(2)
        login_page.login(self.test_email, self.test_password)
        time.sleep(10)
        
        # 导航到社区页面
        community_page = CommunityPage(page)
        page.click("a:has-text('学习社区')")
        time.sleep(3)
        
        assert community_page.is_visible(community_page.community_header)
        assert community_page.is_visible(community_page.create_post_button)
        assert community_page.is_visible(community_page.filter_tabs)
        logger.info("社区页面加载测试成功")
    
    def test_post_filter_tabs(self, page: Page):
        """测试帖子筛选标签"""
        logger.info("测试帖子筛选标签")
        
        # 先登录
        login_page = LoginPage(page)
        page.click("a:has-text('登录')")
        time.sleep(2)
        login_page.login(self.test_email, self.test_password)
        time.sleep(10)
        
        # 导航到社区页面
        community_page = CommunityPage(page)
        page.click("a:has-text('学习社区')")
        time.sleep(3)
        
        assert community_page.is_visible(community_page.all_tab)
        assert community_page.is_visible(community_page.experience_tab)
        assert community_page.is_visible(community_page.note_tab)
        
        community_page.filter_by_type("experience")
        time.sleep(1)
        community_page.filter_by_type("note")
        time.sleep(1)
        community_page.filter_by_type("all")
        time.sleep(1)
        
        logger.info("帖子筛选标签测试成功")
