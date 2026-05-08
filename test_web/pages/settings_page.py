from .base_page import BasePage
from playwright.sync_api import Page

class SettingsPage(BasePage):
    """设置页面页面对象"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.reminder_setting_section = "h2:has-text('休息提醒设置')"
        self.subject_management_section = "h2:has-text('科目管理')"
        self.notification_setting_section = "h2:has-text('通知权限')"
        self.data_management_section = "h2:has-text('数据管理')"
        self.subject_list = ".subject-item"
        self.add_subject_input = ".add-subject input[type='text']"
        self.add_subject_button = ".add-subject button"
        self.edit_subject_buttons = ".subject-item button.edit"
        self.delete_subject_buttons = ".subject-item button.danger"
        self.edit_subject_input = ".modal:has(h3:has-text('编辑科目')) input[type='text']"
        self.confirm_edit_button = ".modal:has(h3:has-text('编辑科目')) button:has-text('确定')"
        self.cancel_edit_button = ".modal:has(h3:has-text('编辑科目')) button:has-text('取消')"
        self.reminder_interval_input = "#reminderInterval"
        self.save_settings_button = "button:has-text('保存设置')"
        self.export_data_button = "button:has-text('导出数据')"
        self.import_data_button = "button:has-text('导入数据')"
        self.clear_data_button = "button:has-text('清除数据').danger"
        self.import_file_input = "#fileInput"
        self.notification_permission_button = "button:has-text('请求通知权限')"
        self.permission_status = ".permission-status"
        self.toast_modal = ".modal:has(.toast)"
        self.toast_message = ".toast-message"
        self.delete_confirm_modal = ".modal:has(h3:has-text('确认删除'))"
        self.confirm_delete_button = ".modal:has(h3:has-text('确认删除')) button.danger"
        self.clear_data_modal = ".modal:has(h3:has-text('确认清除数据'))"
        self.confirm_clear_button = ".modal:has(h3:has-text('确认清除数据')) button.danger"
        self.modal_cancel_button = ".modal button:has-text('取消')"
    
    def wait_for_load(self):
        """等待页面加载完成"""
        self.page.wait_for_selector(self.subject_management_section, timeout=10000)
    
    def get_subject_count(self) -> int:
        """获取科目数量"""
        return self.page.locator(self.subject_list).count()
    
    def add_subject(self, subject_name: str):
        """添加科目"""
        self.fill(self.add_subject_input, subject_name)
        self.click(self.add_subject_button)
    
    def edit_subject(self, index: int, new_name: str):
        """编辑指定索引的科目"""
        edit_buttons = self.page.locator(self.edit_subject_buttons).all()
        if index < len(edit_buttons):
            edit_buttons[index].click()
            self.fill(self.edit_subject_input, new_name)
            self.click(self.confirm_edit_button)
    
    def delete_subject(self, index: int):
        """删除指定索引的科目"""
        delete_buttons = self.page.locator(self.delete_subject_buttons).all()
        if index < len(delete_buttons):
            delete_buttons[index].click()
            self.page.wait_for_selector(self.delete_confirm_modal)
            self.click(self.confirm_delete_button)
    
    def set_reminder_interval(self, interval: int):
        """设置提醒间隔"""
        self.fill(self.reminder_interval_input, str(interval))
        self.click(self.save_settings_button)
    
    def export_data(self):
        """导出数据"""
        self.click(self.export_data_button)
    
    def import_data(self, file_path: str):
        """导入数据"""
        self.click(self.import_data_button)
        with self.page.expect_file_chooser() as fc_info:
            self.page.click(self.import_file_input)
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
    
    def clear_all_data(self):
        """清除所有数据"""
        self.click(self.clear_data_button)
        self.page.wait_for_selector(self.clear_data_modal)
        self.click(self.confirm_clear_button)
    
    def request_notification_permission(self):
        """请求通知权限"""
        self.click(self.notification_permission_button)
    
    def get_permission_status(self) -> str:
        """获取通知权限状态"""
        if self.is_visible(self.permission_status):
            return self.get_text(self.permission_status)
        return ""
    
    def get_toast_message(self) -> str:
        """获取提示消息"""
        if self.is_visible(self.toast_modal):
            return self.get_text(self.toast_message)
        return ""
    
    def is_subject_present(self, subject_name: str) -> bool:
        """检查科目是否存在"""
        subjects = self.page.locator(self.subject_list)
        count = subjects.count()
        for i in range(count):
            subject_name_el = subjects.nth(i).locator(".subject-name")
            if subject_name_el.is_visible() and subject_name_el.inner_text() == subject_name:
                return True
        return False