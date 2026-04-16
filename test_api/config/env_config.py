"""
环境配置快捷访问

支持从 .env 文件、环境变量或 settings.yaml 读取配置
"""
import os
from config.config_manager import get_config, EnvironmentConfig, TestConfig


class EnvConfig:
    """
    环境配置快捷访问类
    
    配置优先级：
    1. .env 文件中的环境变量
    2. 系统环境变量
    3. settings.yaml 配置文件
    """
    
    _config = None
    
    @classmethod
    def _get_config(cls):
        if cls._config is None:
            cls._config = get_config()
        return cls._config
    
    @classmethod
    def get_base_url(cls) -> str:
        """获取基础URL"""
        return cls._get_config().get_env_config().base_url
    
    @classmethod
    def get_auth_url(cls) -> str:
        """获取认证URL"""
        return cls._get_config().get_env_config().auth_url
    
    @classmethod
    def get_rest_url(cls) -> str:
        """获取REST API URL"""
        return cls._get_config().get_env_config().rest_url
    
    @classmethod
    def get_anon_key(cls) -> str:
        """获取匿名密钥"""
        return cls._get_config().get_env_config().anon_key
    
    @classmethod
    def get_timeout(cls) -> int:
        """获取超时时间"""
        return cls._get_config().get_env_config().timeout
    
    @classmethod
    def get_retry_times(cls) -> int:
        """获取重试次数"""
        return cls._get_config().get_env_config().retry_times
    
    @classmethod
    def get_env_config(cls) -> EnvironmentConfig:
        """获取完整环境配置"""
        return cls._get_config().get_env_config()
    
    @classmethod
    def get_test_config(cls) -> TestConfig:
        """获取测试配置"""
        return cls._get_config().get_test_config()
    
    @classmethod
    def get_current_env(cls) -> str:
        """获取当前环境名称"""
        return cls._get_config().get_current_env()
    
    @classmethod
    def set_env(cls, env: str):
        """设置当前环境"""
        cls._get_config().set_env(env)
    
    @classmethod
    def reload_config(cls):
        """重新加载配置"""
        cls._get_config().reload()
