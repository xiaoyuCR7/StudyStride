"""
截图辅助工具

提供截图功能，支持：
- 自动截图
- 失败截图
- 截图管理
"""
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
import allure

from utils.logger import get_logger


class ScreenshotHelper:
    """截图辅助类"""
    
    def __init__(self, screenshot_dir: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        if screenshot_dir:
            self.screenshot_dir = Path(screenshot_dir)
        else:
            self.screenshot_dir = Path(__file__).parent.parent / 'screenshots'
        
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_count = 0
    
    def take_screenshot(
        self,
        name: Optional[str] = None,
        attach_to_allure: bool = True
    ) -> str:
        """
        截取屏幕截图
        
        注意：当前实现为模拟截图，实际使用时需要集成具体的UI测试工具
        （如Selenium、Playwright等）
        
        Args:
            name: 截图名称
            attach_to_allure: 是否附加到Allure报告
        
        Returns:
            截图文件路径
        """
        self.screenshot_count += 1
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = name or f'screenshot_{timestamp}_{self.screenshot_count}'
        filename = f"{name}.png"
        filepath = self.screenshot_dir / filename
        
        # 创建模拟截图（实际项目中替换为真实截图代码）
        self._create_placeholder_screenshot(filepath)
        
        self.logger.info(f"截图已保存: {filepath}")
        
        # 附加到Allure报告
        if attach_to_allure:
            self._attach_to_allure(filepath, name)
        
        return str(filepath)
    
    def take_screenshot_on_failure(
        self,
        test_name: str,
        error_info: Optional[str] = None
    ) -> str:
        """
        失败时截图
        
        Args:
            test_name: 测试名称
            error_info: 错误信息
        
        Returns:
            截图文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = f"failure_{test_name}_{timestamp}"
        
        filepath = self.take_screenshot(name=name, attach_to_allure=True)
        
        # 附加错误信息
        if error_info:
            allure.attach(
                error_info,
                name='错误信息',
                attachment_type=allure.attachment_type.TEXT
            )
        
        return filepath
    
    def _create_placeholder_screenshot(self, filepath: Path):
        """
        创建占位截图
        
        实际项目中应替换为真实的截图实现
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建空白图片
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # 添加文字
            text = f"Screenshot Placeholder\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 尝试使用默认字体
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置（居中）
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (800 - text_width) / 2
            y = (600 - text_height) / 2
            
            draw.text((x, y), text, fill='black', font=font)
            
            # 保存图片
            img.save(filepath)
            
        except ImportError:
            # 如果没有PIL，创建一个简单的文本文件作为占位
            with open(filepath.with_suffix('.txt'), 'w') as f:
                f.write(f"Screenshot Placeholder\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.warning("PIL未安装，使用文本占位符")
    
    def _attach_to_allure(self, filepath: Path, name: str):
        """附加截图到Allure报告"""
        if filepath.exists():
            with open(filepath, 'rb') as f:
                allure.attach(
                    f.read(),
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
    
    def cleanup_old_screenshots(self, days: int = 7):
        """
        清理旧截图
        
        Args:
            days: 保留天数
        """
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        deleted_count = 0
        for file_path in self.screenshot_dir.iterdir():
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                if file_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
        
        self.logger.info(f"清理了 {deleted_count} 个旧截图")
    
    def get_screenshot_dir(self) -> str:
        """获取截图目录路径"""
        return str(self.screenshot_dir)


# 全局截图助手实例
_screenshot_helper: Optional[ScreenshotHelper] = None


def get_screenshot_helper() -> ScreenshotHelper:
    """获取全局截图助手实例"""
    global _screenshot_helper
    if _screenshot_helper is None:
        _screenshot_helper = ScreenshotHelper()
    return _screenshot_helper


def take_screenshot(name: Optional[str] = None) -> str:
    """便捷函数：截取屏幕"""
    return get_screenshot_helper().take_screenshot(name)


def take_screenshot_on_failure(test_name: str, error_info: Optional[str] = None) -> str:
    """便捷函数：失败时截图"""
    return get_screenshot_helper().take_screenshot_on_failure(test_name, error_info)
