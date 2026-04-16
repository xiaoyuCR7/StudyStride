import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Config:
    """测试配置类"""
    # 基础URL
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5173')
    
    # 浏览器配置
    BROWSER = os.getenv('BROWSER', 'chromium')
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    SLOW_MO = int(os.getenv('SLOW_MO', '100'))
    
    # 测试超时设置
    TIMEOUT = 30
    
    # 测试数据
    TEST_SUBJECT = '测试科目'
    TEST_CONTENT = '测试内容'
    
    @classmethod
    def get_browser_launch_options(cls):
        """获取浏览器启动选项"""
        return {
            'headless': cls.HEADLESS,
            'slow_mo': cls.SLOW_MO
        }

# 创建全局配置实例
config = Config()
