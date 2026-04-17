from .base_page import BasePage
from playwright.sync_api import Page

class HistoryPage(BasePage):
    """历史记录页面页面对象"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        # 筛选相关
        self.date_filter = "input[type='date']"
        self.show_all_button = "button:has-text('显示全部')"
        self.subject_filter = "select[id='subjectFilter']"
        
        # 记录相关
        self.session_items = ".session-item"
        self.edit_buttons = ".edit-btn"
        self.delete_buttons = ".delete-btn"
        
        # 编辑弹窗相关
        self.edit_modal = ".modal:has-text('编辑学习记录')"
        self.edit_subject_select = "#editSubject"
        self.edit_hours_input = "input[placeholder='小时']"
        self.edit_minutes_input = "input[placeholder='分钟']"
        self.edit_content_input = "#editContent"
        self.save_edit_button = "button:has-text('保存')"
        self.cancel_edit_button = "button:has-text('取消')"
        
        # 删除弹窗相关
        self.delete_modal = ".modal:has-text('确认删除')"
        self.confirm_delete_button = "button.danger"
        self.cancel_delete_button = "button:has-text('取消')"
        
        # 提示消息
        self.toast_message = ".modal"
    
    def wait_for_load(self):
        """等待页面加载完成"""
        super().wait_for_load()
        # 等待会话项加载完成
        import time
        time.sleep(1)
        
    def wait_for_sessions(self, timeout: int = 10):
        """等待会话项出现"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.get_session_count() > 0:
                return
            time.sleep(0.5)
        # 如果超时，仍然继续执行，不抛出异常
    
    def filter_by_date(self, date: str):
        """按日期筛选"""
        self.fill(self.date_filter, date)
    
    def show_all(self):
        """显示全部记录"""
        self.click(self.show_all_button)
    
    def filter_by_subject(self, subject: str):
        """按科目筛选"""
        self.select_option(self.subject_filter, subject)
    
    def get_session_count(self) -> int:
        """获取会话数量"""
        return self.page.locator(self.session_items).count()
    
    def edit_session(self, index: int):
        """编辑指定索引的会话"""
        edit_buttons = self.page.locator(self.edit_buttons).all()
        if index < len(edit_buttons):
            edit_buttons[index].click()
            self.wait_for_selector(self.edit_modal)
    
    def delete_session(self, index: int):
        """删除指定索引的会话"""
        delete_buttons = self.page.locator(self.delete_buttons).all()
        if index < len(delete_buttons):
            delete_buttons[index].click()
            self.wait_for_selector(self.delete_modal)
    
    def save_edit(self, subject: str, hours: str, minutes: str, content: str = ""):
        """保存编辑"""
        self.select_option(self.edit_subject_select, subject)
        self.fill(self.edit_hours_input, hours)
        self.fill(self.edit_minutes_input, minutes)
        if content:
            self.fill(self.edit_content_input, content)
        self.click(self.save_edit_button)
    
    def cancel_edit(self):
        """取消编辑"""
        self.click(self.cancel_edit_button)
    
    def confirm_delete(self):
        """确认删除"""
        self.click(self.confirm_delete_button)
    
    def cancel_delete(self):
        """取消删除"""
        self.click(self.cancel_delete_button)
    
    def get_toast_message(self) -> str:
        """获取提示消息"""
        self.wait_for_selector(self.toast_message)
        return self.get_text(self.toast_message)
