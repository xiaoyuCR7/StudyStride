from .base_page import BasePage
from playwright.sync_api import Page, Locator

class HomePage(BasePage):
    """首页页面对象"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.subject_select = "select#subjectSelect"
        self.start_button = "button:has-text('开始学习')"
        self.pause_button = "button:has-text('暂停')"
        self.stop_button = "button:has-text('结束')"
        self.timer_display = ".timer-display"
        self.continue_button = "button:has-text('继续')"
        self.add_subject_button = "button.add-subject-btn"
        self.new_subject_input = ".modal-content input[type='text']"
        self.modal_confirm_button = ".modal-buttons button:first-child"
        self.modal_cancel_button = ".modal-buttons button:last-child"
        self.quick_record_tab = "h2:has-text('快速记录学习')"
        self.quick_subject_select = "#quickSubject"
        self.quick_hours_input = "#quickHours"
        self.quick_minutes_input = "#quickMinutes"
        self.quick_content_input = "#quickContent"
        self.quick_record_button = "button.record-btn"
        self.subject_selection = ".subject-selection"
        self.current_subject = ".current-subject"
        self.timer_container = ".timer-container"
        self.content_container = ".content-container"
        self.today_summary = ".today-summary"
        self.quick_record = ".quick-record"
        self.modal = ".modal"
    
    def wait_for_load(self):
        """等待页面加载完成"""
        self.page.wait_for_selector(self.timer_container, timeout=10000)
    
    def start_timer(self, subject_name: str = "测试科目"):
        """开始计时"""
        self.add_subject(subject_name)
        self.select_subject(subject_name)
        self.click(self.start_button)
    
    def pause_timer(self):
        """暂停计时"""
        self.click(self.pause_button)
    
    def stop_timer(self):
        """结束计时"""
        self.click(self.stop_button)
    
    def get_timer_display(self) -> str:
        """获取计时器显示"""
        return self.get_text(self.timer_display)
    
    def continue_timer(self):
        """继续计时"""
        self.click(self.continue_button)
    
    def select_subject(self, subject: str):
        """选择科目"""
        self.select_option(self.subject_select, subject)
    
    def add_subject(self, subject_name: str):
        """添加科目"""
        self.click(self.add_subject_button)
        self.fill(self.new_subject_input, subject_name)
        self.click(self.modal_confirm_button)
    
    def is_timer_running(self) -> bool:
        """检查计时器是否正在运行"""
        return self.is_visible(self.pause_button)
    
    def is_timer_paused(self) -> bool:
        """检查计时器是否已暂停"""
        return self.is_visible(self.continue_button)
    
    def is_subject_selected(self, subject_name: str) -> bool:
        """检查科目是否已选择"""
        selected = self.page.locator(self.subject_select).evaluate('el => el.value')
        return selected == subject_name
    
    def quick_record_session(self, subject: str, hours: str, minutes: str, content: str = ""):
        """快速记录学习会话"""
        self.add_subject(subject)
        import time
        time.sleep(0.5)
        self.select_option(self.quick_subject_select, subject)
        self.fill(self.quick_hours_input, hours)
        self.fill(self.quick_minutes_input, minutes)
        if content:
            self.fill(self.quick_content_input, content)
        self.click(self.quick_record_button)
        time.sleep(1)
    
    def get_today_sessions_count(self) -> str:
        """获取今日学习次数"""
        stat_value = self.page.locator(".today-summary .stat-value").first
        return stat_value.inner_text()
    
    def cancel_add_subject(self):
        """取消添加科目"""
        self.click(self.modal_cancel_button)
    
    def close_modal(self):
        """关闭弹窗"""
        if self.is_visible(self.modal):
            self.click(self.modal)
    
    def get_session_content_textarea(self) -> Locator:
        """获取学习内容文本框"""
        return self.page.locator(".content-container textarea")
    
    def fill_session_content(self, content: str):
        """填写学习内容"""
        textarea = self.get_session_content_textarea()
        if textarea.is_visible():
            textarea.fill(content)