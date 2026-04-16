from .base_page import BasePage
from playwright.sync_api import Page

class SettingsPage(BasePage):
    """设置页面页面对象"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        # 标签页相关
        self.subject_management_tab = "h2:has-text('科目管理')"
        self.data_management_tab = "h2:has-text('数据管理')"
        self.notification_tab = "h2:has-text('休息提醒设置')"
        
        # 科目管理相关
        self.subject_list = ".subject-item"
        self.edit_subject_buttons = ".edit"
        self.delete_subject_buttons = ".danger"
        self.edit_subject_input = "input[placeholder='输入科目名称']"
        self.confirm_edit_subject = "button:has-text('确定')"
        self.cancel_edit_subject = "button:has-text('取消')"
        
        # 通知设置相关
        self.reminder_interval_input = "input[type='number']"
        self.save_settings_button = "button:has-text('保存设置')"
        
        # 数据管理相关
        self.export_data_button = "button:has-text('导出数据')"
        self.import_data_button = "button:has-text('导入数据')"
        self.import_file_input = "input[type='file']"
        self.confirm_import_button = "button:has-text('确认导入')"
        
        # 提示消息
        self.toast_message = ".modal"
    
    def switch_to_subject_management(self):
        """切换到科目管理标签"""
        self.click(self.subject_management_tab)
    
    def switch_to_data_management(self):
        """切换到数据管理标签"""
        self.click(self.data_management_tab)
    
    def switch_to_notification_settings(self):
        """切换到通知设置标签"""
        self.click(self.notification_tab)
    
    def get_subject_count(self) -> int:
        """获取科目数量"""
        return len(self.page.locator(self.subject_list).all())
    
    def edit_subject(self, index: int, new_name: str):
        """编辑指定索引的科目"""
        edit_buttons = self.page.locator(self.edit_subject_buttons).all()
        if index < len(edit_buttons):
            edit_buttons[index].click()
            self.fill(self.edit_subject_input, new_name)
            self.click(self.confirm_edit_subject)
    
    def delete_subject(self, index: int):
        """删除指定索引的科目"""
        # 获取所有科目删除按钮（排除其他危险按钮）
        subject_delete_buttons = self.page.locator(".subject-item .danger").all()
        if index < len(subject_delete_buttons):
            subject_delete_buttons[index].click()
            # 等待确认弹窗出现
            self.page.wait_for_selector(".modal")
            # 点击模态框中的删除按钮
            self.page.locator(".modal .danger").click()
    
    def set_reminder_interval(self, interval):
        """设置提醒间隔"""
        self.switch_to_notification_settings()
        self.fill(self.reminder_interval_input, str(interval))
        self.click(self.save_settings_button)
    
    def export_data(self):
        """导出数据"""
        self.switch_to_data_management()
        self.click(self.export_data_button)
    
    def import_data(self, file_path: str):
        """导入数据"""
        self.switch_to_data_management()
        self.click(self.import_data_button)
        # 上传文件
        with self.page.expect_file_chooser() as fc_info:
            self.click(self.import_file_input)
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        self.click(self.confirm_import_button)
    
    def get_toast_message(self) -> str:
        """获取提示消息"""
        self.wait_for_selector(self.toast_message)
        return self.get_text(self.toast_message)
