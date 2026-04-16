"""
Allure报告辅助工具

提供Allure报告的增强功能：
- 请求/响应信息附加
- 截图附加
- 步骤装饰器
- 测试分类标签
"""
import os
import json
import allure
from typing import Any, Optional, Dict
from pathlib import Path

from utils.logger import get_logger


class AllureHelper:
    """Allure报告辅助类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    @staticmethod
    def attach_request_info(
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        body: Any = None
    ):
        """
        附加请求信息到Allure报告
        
        Args:
            method: HTTP方法
            url: 请求URL
            headers: 请求头
            params: 请求参数
            body: 请求体
        """
        # 构建请求信息
        request_info = {
            'method': method,
            'url': url,
            'headers': headers or {},
            'params': params or {},
            'body': body
        }
        
        # 附加为JSON
        allure.attach(
            json.dumps(request_info, indent=2, ensure_ascii=False, default=str),
            name='请求信息',
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def attach_response_info(
        status_code: int,
        headers: Dict[str, str],
        body: Any,
        response_time: float
    ):
        """
        附加响应信息到Allure报告
        
        Args:
            status_code: 状态码
            headers: 响应头
            body: 响应体
            response_time: 响应时间
        """
        response_info = {
            'status_code': status_code,
            'headers': headers,
            'body': body,
            'response_time': f"{response_time:.3f}s"
        }
        
        allure.attach(
            json.dumps(response_info, indent=2, ensure_ascii=False, default=str),
            name='响应信息',
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def attach_screenshot(screenshot_path: str, name: str = '截图'):
        """
        附加截图到Allure报告
        
        Args:
            screenshot_path: 截图文件路径
            name: 附件名称
        """
        if not os.path.exists(screenshot_path):
            return
        
        with open(screenshot_path, 'rb') as f:
            allure.attach(
                f.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
    
    @staticmethod
    def attach_text(content: str, name: str = '文本'):
        """附加文本内容"""
        allure.attach(
            content,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )
    
    @staticmethod
    def attach_html(content: str, name: str = 'HTML'):
        """附加HTML内容"""
        allure.attach(
            content,
            name=name,
            attachment_type=allure.attachment_type.HTML
        )
    
    @staticmethod
    def attach_file(file_path: str, name: Optional[str] = None):
        """
        附加文件到报告
        
        Args:
            file_path: 文件路径
            name: 附件名称
        """
        if not os.path.exists(file_path):
            return
        
        name = name or Path(file_path).name
        
        # 根据扩展名选择附件类型
        ext = Path(file_path).suffix.lower()
        type_mapping = {
            '.json': allure.attachment_type.JSON,
            '.xml': allure.attachment_type.XML,
            '.html': allure.attachment_type.HTML,
            '.png': allure.attachment_type.PNG,
            '.jpg': allure.attachment_type.JPG,
            '.jpeg': allure.attachment_type.JPG,
            '.txt': allure.attachment_type.TEXT,
            '.csv': allure.attachment_type.CSV,
            '.pdf': allure.attachment_type.PDF,
            '.mp4': allure.attachment_type.MP4,
            '.uri': allure.attachment_type.URI_LIST
        }
        
        attachment_type = type_mapping.get(ext, allure.attachment_type.TEXT)
        
        with open(file_path, 'rb') as f:
            allure.attach(
                f.read(),
                name=name,
                attachment_type=attachment_type
            )
    
    @staticmethod
    def feature(name: str):
        """功能标签"""
        return allure.feature(name)
    
    @staticmethod
    def story(name: str):
        """故事标签"""
        return allure.story(name)
    
    @staticmethod
    def severity(level: str):
        """
        严重级别
        
        Args:
            level: blocker, critical, normal, minor, trivial
        """
        return allure.severity(level)
    
    @staticmethod
    def tag(*tags: str):
        """标签"""
        return allure.tag(*tags)
    
    @staticmethod
    def link(url: str, name: Optional[str] = None, link_type: str = 'link'):
        """添加链接"""
        return allure.link(url, name=name, link_type=link_type)
    
    @staticmethod
    def issue(url: str, name: Optional[str] = None):
        """关联Issue"""
        return allure.issue(url, name=name)
    
    @staticmethod
    def testcase(url: str, name: Optional[str] = None):
        """关联测试用例"""
        return allure.testcase(url, name=name)
    
    @staticmethod
    def description(text: str):
        """测试描述"""
        return allure.description(text)
    
    @staticmethod
    def description_html(html: str):
        """HTML格式测试描述"""
        return allure.description_html(html)
    
    @staticmethod
    def step(title: str):
        """测试步骤"""
        return allure.step(title)
    
    @staticmethod
    def dynamic_feature(name: str):
        """动态功能标签"""
        allure.dynamic.feature(name)
    
    @staticmethod
    def dynamic_story(name: str):
        """动态故事标签"""
        allure.dynamic.story(name)
    
    @staticmethod
    def dynamic_severity(level: str):
        """动态严重级别"""
        allure.dynamic.severity(level)
    
    @staticmethod
    def dynamic_tag(*tags: str):
        """动态标签"""
        allure.dynamic.tag(*tags)
    
    @staticmethod
    def dynamic_link(url: str, name: Optional[str] = None, link_type: str = 'link'):
        """动态链接"""
        allure.dynamic.link(url, name=name, link_type=link_type)


def allure_feature(name: str):
    """功能标签装饰器"""
    return allure.feature(name)


def allure_story(name: str):
    """故事标签装饰器"""
    return allure.story(name)


def allure_severity(level: str):
    """严重级别装饰器"""
    return allure.severity(level)


def allure_tag(*tags: str):
    """标签装饰器"""
    return allure.tag(*tags)


def allure_step(title: str):
    """步骤装饰器"""
    return allure.step(title)
