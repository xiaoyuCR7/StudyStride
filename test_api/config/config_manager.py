"""
配置管理器 - 统一处理YAML/JSON/.env配置，支持多环境切换
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from functools import lru_cache

# 尝试导入python-dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


@dataclass
class EnvironmentConfig:
    """环境配置数据类"""
    name: str
    base_url: str
    auth_url: str
    rest_url: str
    anon_key: str
    timeout: int = 30
    retry_times: int = 3
    retry_interval: int = 1


@dataclass
class TestConfig:
    """测试配置数据类"""
    markers: Dict[str, str] = field(default_factory=dict)
    retry_enabled: bool = True
    retry_max_times: int = 3
    retry_delay: int = 1
    allure_enabled: bool = True
    screenshot_enabled: bool = True
    screenshot_on_failure: bool = True
    log_level: str = "INFO"


class ConfigManager:
    """
    配置管理器
    
    功能：
    1. 支持YAML/JSON配置文件
    2. 支持.env环境变量文件
    3. 多环境切换（dev/test/prod）
    4. 环境变量覆盖
    5. 配置缓存
    """
    
    _instance = None
    _config_data: Dict[str, Any] = {}
    _current_env: str = "dev"
    _dotenv_loaded: bool = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None, env_file: Optional[str] = None):
        if not self._config_data:
            # 首先加载.env文件
            self._load_dotenv(env_file)
            
            self.config_path = config_path or self._get_default_config_path()
            self._load_config()
    
    def _load_dotenv(self, env_file: Optional[str] = None):
        """
        加载.env文件
        
        Args:
            env_file: .env文件路径，默认查找项目根目录
        """
        if not DOTENV_AVAILABLE:
            return
        
        if self._dotenv_loaded:
            return
        
        if env_file:
            dotenv_path = Path(env_file)
        else:
            # 查找项目根目录的.env文件
            current_dir = Path(__file__).parent.parent
            dotenv_path = current_dir / ".env"
        
        if dotenv_path.exists():
            load_dotenv(dotenv_path, override=True)
            self._dotenv_loaded = True
            print(f"[ConfigManager] 已加载环境变量文件: {dotenv_path}")
    
    def _get_default_config_path(self) -> Optional[str]:
        """获取默认配置文件路径"""
        current_dir = Path(__file__).parent
        yaml_path = current_dir / "settings.yaml"
        json_path = current_dir / "settings.json"
        
        if yaml_path.exists():
            return str(yaml_path)
        elif json_path.exists():
            return str(json_path)
        else:
            # 如果配置文件不存在，返回None，后续会依赖环境变量
            print("[ConfigManager] 未找到配置文件，将从环境变量读取配置")
            return None
    
    def _load_config(self):
        """加载配置文件"""
        # 如果没有配置文件路径，使用默认配置
        if self.config_path is None:
            print("[ConfigManager] 使用默认配置结构")
            self._config_data = self._get_default_config_structure()
            # 设置默认环境
            self._current_env = os.getenv('TEST_ENV', self._get_default_env())
            # 应用环境变量覆盖
            self._apply_env_overrides()
            return
        
        path = Path(self.config_path)
        
        if not path.exists():
            print(f"[ConfigManager] 配置文件不存在: {self.config_path}，将使用默认配置")
            self._config_data = self._get_default_config_structure()
            # 设置默认环境
            self._current_env = os.getenv('TEST_ENV', self._get_default_env())
            # 应用环境变量覆盖
            self._apply_env_overrides()
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                self._config_data = yaml.safe_load(f)
            elif path.suffix == '.json':
                self._config_data = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {path.suffix}")
        
        # 设置默认环境
        self._current_env = os.getenv('TEST_ENV', self._config_data.get('default_env', 'dev'))
        
        # 应用环境变量覆盖
        self._apply_env_overrides()
    
    def _get_default_config_structure(self) -> Dict[str, Any]:
        """获取默认配置结构"""
        return {
            "default_env": os.getenv('TEST_ENV', 'dev'),
            "environments": {
                "dev": {
                    "name": "开发环境",
                    "base_url": os.getenv('DEV_SUPABASE_URL', ''),
                    "auth_url": f"{os.getenv('DEV_SUPABASE_URL', '')}/auth/v1" if os.getenv('DEV_SUPABASE_URL') else '',
                    "rest_url": f"{os.getenv('DEV_SUPABASE_URL', '')}/rest/v1" if os.getenv('DEV_SUPABASE_URL') else '',
                    "anon_key": os.getenv('DEV_SUPABASE_ANON_KEY', ''),
                    "timeout": 30,
                    "retry_times": 3,
                    "retry_interval": 1
                },
                "test": {
                    "name": "测试环境",
                    "base_url": os.getenv('TEST_SUPABASE_URL', ''),
                    "auth_url": f"{os.getenv('TEST_SUPABASE_URL', '')}/auth/v1" if os.getenv('TEST_SUPABASE_URL') else '',
                    "rest_url": f"{os.getenv('TEST_SUPABASE_URL', '')}/rest/v1" if os.getenv('TEST_SUPABASE_URL') else '',
                    "anon_key": os.getenv('TEST_SUPABASE_ANON_KEY', ''),
                    "timeout": 30,
                    "retry_times": 3,
                    "retry_interval": 1
                },
                "prod": {
                    "name": "生产环境",
                    "base_url": os.getenv('PROD_SUPABASE_URL', ''),
                    "auth_url": f"{os.getenv('PROD_SUPABASE_URL', '')}/auth/v1" if os.getenv('PROD_SUPABASE_URL') else '',
                    "rest_url": f"{os.getenv('PROD_SUPABASE_URL', '')}/rest/v1" if os.getenv('PROD_SUPABASE_URL') else '',
                    "anon_key": os.getenv('PROD_SUPABASE_ANON_KEY', ''),
                    "timeout": 30,
                    "retry_times": 3,
                    "retry_interval": 1
                }
            },
            "test": {
                "markers": {
                    "smoke": "冒烟测试",
                    "regression": "回归测试",
                    "api": "接口测试",
                    "auth": "认证测试",
                    "study_session": "学习会话测试",
                    "subject": "科目测试",
                    "user_settings": "用户设置测试",
                    "positive": "正向测试",
                    "negative": "负向测试",
                    "critical": "关键用例"
                }
            }
        }
    
    def _get_default_env(self) -> str:
        """获取默认环境"""
        # 优先使用TEST_ENV环境变量
        if os.getenv('TEST_ENV'):
            return os.getenv('TEST_ENV')
        # 其次检查各个环境的SUPABASE_URL是否存在
        for env in ['dev', 'test', 'prod']:
            if os.getenv(f'{env.upper()}_SUPABASE_URL'):
                return env
        # 默认使用dev
        return 'dev'
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖配置"""
        env_prefix = "TEST_API_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                keys = config_key.split('_')
                
                # 递归设置配置值
                current = self._config_data
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = self._parse_env_value(value)
    
    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为布尔值
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # 尝试解析为整数
        try:
            return int(value)
        except ValueError:
            pass
        
        # 尝试解析为浮点数
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔（如：environments.dev.base_url）
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        current = self._config_data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def get_env_config(self, env: Optional[str] = None) -> EnvironmentConfig:
        """
        获取环境配置
        
        优先级：.env文件 > 环境变量 > YAML配置文件
        
        Args:
            env: 环境名称，默认使用当前环境
        
        Returns:
            EnvironmentConfig 对象
        """
        env = env or self._current_env
        env_upper = env.upper()
        
        # 首先尝试从环境变量读取
        base_url = os.getenv(f'{env_upper}_SUPABASE_URL')
        anon_key = os.getenv(f'{env_upper}_SUPABASE_ANON_KEY')
        
        if base_url and anon_key:
            # 从环境变量构建配置
            return EnvironmentConfig(
                name=env,
                base_url=base_url,
                auth_url=f"{base_url}/auth/v1",
                rest_url=f"{base_url}/rest/v1",
                anon_key=anon_key,
                timeout=int(os.getenv(f'{env_upper}_TIMEOUT', '30')),
                retry_times=int(os.getenv(f'{env_upper}_RETRY_TIMES', '3')),
                retry_interval=int(os.getenv(f'{env_upper}_RETRY_INTERVAL', '1'))
            )
        
        # 回退到YAML配置
        env_data = self.get(f'environments.{env}')
        
        if not env_data:
            raise ValueError(f"未找到环境配置: {env}，请确保已设置环境变量 {env_upper}_SUPABASE_URL 和 {env_upper}_SUPABASE_ANON_KEY")
        
        return EnvironmentConfig(
            name=env_data.get('name', env),
            base_url=env_data.get('base_url', ''),
            auth_url=env_data.get('auth_url', ''),
            rest_url=env_data.get('rest_url', ''),
            anon_key=env_data.get('anon_key', ''),
            timeout=env_data.get('timeout', 30),
            retry_times=env_data.get('retry_times', 3),
            retry_interval=env_data.get('retry_interval', 1)
        )
    
    def get_test_config(self) -> TestConfig:
        """获取测试配置"""
        test_data = self.get('test', {})
        retry_data = test_data.get('retry', {})
        
        return TestConfig(
            markers=test_data.get('markers', {}),
            retry_enabled=retry_data.get('enabled', True),
            retry_max_times=retry_data.get('max_times', 3),
            retry_delay=retry_data.get('delay', 1),
            allure_enabled=test_data.get('allure', {}).get('enabled', True),
            screenshot_enabled=test_data.get('screenshot', {}).get('enabled', True),
            screenshot_on_failure=test_data.get('screenshot', {}).get('on_failure', True),
            log_level=test_data.get('logging', {}).get('level', 'INFO')
        )
    
    def set_env(self, env: str):
        """设置当前环境"""
        if env not in self.get('environments', {}):
            raise ValueError(f"无效的环境: {env}")
        self._current_env = env
    
    def get_current_env(self) -> str:
        """获取当前环境"""
        return self._current_env
    
    def reload(self):
        """重新加载配置"""
        self._config_data = {}
        self._load_config()
    
    def get_all_envs(self) -> list:
        """获取所有环境名称"""
        return list(self.get('environments', {}).keys())


# 全局配置管理器实例
@lru_cache()
def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """获取配置管理器实例（单例）"""
    return ConfigManager(config_path)
