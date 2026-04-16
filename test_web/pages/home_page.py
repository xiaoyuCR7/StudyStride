from .base_page import BasePage
from playwright.sync_api import Page

class HomePage(BasePage):
    """首页页面对象"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        # 计时器相关
        self.subject_select_option = "select#subjectSelect"
        self.start_button = "button:has-text('开始学习')"
        self.pause_button = "button:has-text('暂停')"
        self.stop_button = "button:has-text('结束')"
        self.timer_display = ".timer-display"
        self.continue_button = "button:has-text('继续')"

        # 科目相关
        self.subject_select = "select#subjectSelect"
        self.add_subject_button = "button:has-text('添加科目')"
        self.subject_input = "input[placeholder='输入科目名称']"
        self.confirm_add_subject = "button:has-text('确定')"
        self.cancel_add_subject = "button:has-text('取消')"
        
        # 快速记录相关
        self.quick_record_tab = "h2:has-text('快速记录学习')"
        self.quick_subject_select = "#quickSubject"
        self.quick_hours_input = "#quickHours"
        self.quick_minutes_input = "#quickMinutes"
        self.quick_content_input = "#quickContent"
        self.quick_record_button = "button:has-text('记录学习')"
    
    def start_timer(self):
        """开始计时"""
        self.add_subject("测试科目")
        self.page.locator(self.subject_select).click()
        self.page.locator(self.subject_select_option).select_option(index=1)
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
        self.fill(self.subject_input, subject_name)
        self.click(self.confirm_add_subject)
    
    def switch_to_quick_record(self):
        """切换到快速记录标签"""
        self.click(self.quick_record_tab)
    
    def quick_record_session(self, subject: str, hours: str, minutes: str, content: str = ""):
        """快速记录学习会话"""
        self.add_subject(subject)
        self.switch_to_quick_record()
        self.select_option(self.quick_subject_select, subject)
        self.fill(self.quick_hours_input, hours)
        self.fill(self.quick_minutes_input, minutes)
        if content:
            self.fill(self.quick_content_input, content)
        self.click(self.quick_record_button)
