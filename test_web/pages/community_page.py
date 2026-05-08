from .base_page import BasePage
from playwright.sync_api import Page

class CommunityPage(BasePage):
    """社区页面页面对象"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.community_header = ".community-header"
        self.create_post_button = "button.create-btn"
        self.search_bar = "input[type='search']"
        self.filter_tabs = ".filter-tabs"
        self.all_tab = ".tab:has-text('全部')"
        self.experience_tab = ".tab:has-text('学习经验')"
        self.note_tab = ".tab:has-text('笔记分享')"
        self.posts_list = ".posts-list"
        self.post_card = ".post-card"
        self.skeleton_list = ".skeleton-list"
        self.loading_more = ".loading-more"
        self.no_more = ".no-more"
        self.empty_state = ".empty-state"
        self.post_title = ".post-title"
        self.post_content = ".post-content"
        self.author_name = ".author-name"
        self.post_time = ".post-time"
        self.type_badge = ".type-badge"
        self.like_button = ".interaction-btn:has(.icon:has-text('♥'))"
        self.comment_button = ".interaction-btn:has(.icon:has-text('💬'))"
        self.scroll_trigger = ".scroll-trigger"
    
    def wait_for_load(self):
        """等待页面加载完成"""
        self.page.wait_for_selector(self.community_header, timeout=10000)
        self.page.wait_for_load_state("networkidle")
    
    def wait_for_posts(self, timeout: int = 15):
        """等待帖子加载完成"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_visible(self.skeleton_list):
                return
            time.sleep(0.5)
    
    def go_to_create_post(self):
        """导航到发布帖子页面"""
        self.click(self.create_post_button)
    
    def search_posts(self, keyword: str):
        """搜索帖子"""
        self.fill(self.search_bar, keyword)
    
    def filter_by_type(self, post_type: str):
        """按类型筛选帖子"""
        if post_type == "all":
            self.click(self.all_tab)
        elif post_type == "experience":
            self.click(self.experience_tab)
        elif post_type == "note":
            self.click(self.note_tab)
    
    def get_post_count(self) -> int:
        """获取帖子数量"""
        return self.page.locator(self.post_card).count()
    
    def click_post(self, index: int):
        """点击指定索引的帖子"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            posts[index].click()
    
    def get_post_title(self, index: int) -> str:
        """获取指定帖子的标题"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            title = posts[index].locator(self.post_title)
            if title.is_visible():
                return title.inner_text()
        return ""
    
    def get_post_content(self, index: int) -> str:
        """获取指定帖子的内容摘要"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            content = posts[index].locator(self.post_content)
            if content.is_visible():
                return content.inner_text()
        return ""
    
    def get_post_author(self, index: int) -> str:
        """获取指定帖子的作者"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            author = posts[index].locator(self.author_name)
            if author.is_visible():
                return author.inner_text()
        return ""
    
    def get_post_time(self, index: int) -> str:
        """获取指定帖子的发布时间"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            post_time = posts[index].locator(self.post_time)
            if post_time.is_visible():
                return post_time.inner_text()
        return ""
    
    def get_post_type(self, index: int) -> str:
        """获取指定帖子的类型"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            badge = posts[index].locator(self.type_badge)
            if badge.is_visible():
                return badge.inner_text()
        return ""
    
    def like_post(self, index: int):
        """点赞指定帖子"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            like_btn = posts[index].locator(self.like_button)
            if like_btn.is_visible():
                like_btn.click()
    
    def comment_post(self, index: int):
        """评论指定帖子"""
        posts = self.page.locator(self.post_card).all()
        if index < len(posts):
            comment_btn = posts[index].locator(self.comment_button)
            if comment_btn.is_visible():
                comment_btn.click()
    
    def is_loading_more(self) -> bool:
        """检查是否正在加载更多"""
        return self.is_visible(self.loading_more)
    
    def is_no_more_posts(self) -> bool:
        """检查是否已加载全部"""
        return self.is_visible(self.no_more)
    
    def is_empty_state(self) -> bool:
        """检查是否为空状态"""
        return self.is_visible(self.empty_state)
    
    def get_empty_state_text(self) -> str:
        """获取空状态文本"""
        return self.get_text(self.empty_state)