"""
视频录制工具

提供测试视频录制功能，利用 Playwright 的自动视频录制功能
"""
import os
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page
from typing import Optional


class VideoRecorder:
    """视频录制器（基于 Playwright 自动录制）"""
    
    def __init__(self, page: Page, test_name: str = None):
        self.page = page
        self.test_name = test_name or "test_video"
        self.video_path: Optional[Path] = None
        self._setup_video_directory()
    
    def _setup_video_directory(self):
        """设置视频保存目录"""
        self.video_dir = Path('test_web/videos')
        self.video_dir.mkdir(parents=True, exist_ok=True)
    
    def get_video_path(self) -> Optional[str]:
        """获取录制的视频文件路径"""
        try:
            # 从 page 对象获取视频路径
            video = self.page.video
            if video:
                # Playwright 会自动保存视频到这个路径
                self.video_path = Path(video.path())
                if self.video_path.exists():
                    return str(self.video_path)
        except Exception as e:
            print(f"Failed to get video path: {e}")
        return None


class VideoRecorderManager:
    """视频录制管理器"""
    
    _recorders: dict = {}
    
    @classmethod
    def start_recording(cls, page: Page, test_name: str) -> VideoRecorder:
        """为指定测试创建录制器"""
        recorder = VideoRecorder(page, test_name)
        cls._recorders[test_name] = recorder
        return recorder
    
    @classmethod
    def get_video_path(cls, test_name: str) -> Optional[str]:
        """获取指定测试的视频路径"""
        if test_name in cls._recorders:
            return cls._recorders[test_name].get_video_path()
        return None


def start_video_recording(page: Page, test_name: str) -> VideoRecorder:
    """开始视频录制"""
    return VideoRecorderManager.start_recording(page, test_name)


def stop_video_recording(test_name: str) -> Optional[str]:
    """停止视频录制并返回视频文件路径"""
    # Playwright 会自动保存视频，不需要手动停止
    # 直接返回视频路径
    return VideoRecorderManager.get_video_path(test_name)


def get_video_path(test_name: str) -> Optional[str]:
    """获取视频路径"""
    return VideoRecorderManager.get_video_path(test_name)
