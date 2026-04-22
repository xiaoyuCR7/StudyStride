import allure
from allure_commons.types import AttachmentType

class AllureHelper:
    """Allure报告辅助类"""
    
    @staticmethod
    def step(description):
        """添加测试步骤"""
        return allure.step(description)
    
    @staticmethod
    def attach_screenshot(page, name):
        """添加截图附件"""
        screenshot = page.screenshot()
        allure.attach(
            body=screenshot,
            name=name,
            attachment_type=AttachmentType.PNG
        )
    
    @staticmethod
    def attach_text(content, name):
        """添加文本附件"""
        allure.attach(
            body=content,
            name=name,
            attachment_type=AttachmentType.TEXT
        )
    
    @staticmethod
    def attach_html(content, name):
        """添加HTML附件"""
        allure.attach(
            body=content,
            name=name,
            attachment_type=AttachmentType.HTML
        )
    
    @staticmethod
    def set_feature(feature_name):
        """设置测试功能"""
        allure.feature(feature_name)
    
    @staticmethod
    def set_story(story_name):
        """设置测试故事"""
        allure.story(story_name)
    
    @staticmethod
    def set_severity(severity):
        """设置测试严重程度"""
        allure.severity(severity)
    
    @staticmethod
    def set_tag(tag):
        """设置测试标签"""
        allure.tag(tag)
