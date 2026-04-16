"""
会话管理器

管理测试会话的生命周期：
- 会话创建和销毁
- 上下文管理
- 资源清理
"""
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import allure

from core.api_client import ApiClient
from core.auth_manager import AuthManager
from utils.logger import get_logger


class SessionManager:
    """
    会话管理器
    
    管理测试会话的完整生命周期
    """
    
    _sessions: Dict[str, 'SessionManager'] = {}
    _active_session: Optional[str] = None
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.logger = get_logger(__name__)
        
        # 初始化组件
        self.api_client = ApiClient()
        self.auth_manager = AuthManager(self.api_client)
        
        # 会话状态
        self._is_active = False
        self._test_data: Dict[str, Any] = {}
        self._cleanup_tasks: List[callable] = []
        
        # 注册会话
        SessionManager._sessions[self.session_id] = self
    
    @classmethod
    def _generate_session_id(cls) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    @classmethod
    def get_session(cls, session_id: Optional[str] = None) -> 'SessionManager':
        """
        获取会话实例
        
        Args:
            session_id: 会话ID，默认获取当前活动会话
        
        Returns:
            SessionManager实例
        """
        if session_id:
            return cls._sessions.get(session_id)
        
        if cls._active_session:
            return cls._sessions.get(cls._active_session)
        
        # 创建新会话
        return cls()
    
    @classmethod
    def set_active_session(cls, session_id: str):
        """设置当前活动会话"""
        if session_id in cls._sessions:
            cls._active_session = session_id
    
    @allure.step("启动测试会话")
    def start(self, login: bool = False, email: Optional[str] = None, password: Optional[str] = None):
        """
        启动会话
        
        Args:
            login: 是否自动登录
            email: 登录邮箱
            password: 登录密码
        """
        self.logger.info(f"启动会话: {self.session_id}")
        self._is_active = True
        SessionManager._active_session = self.session_id
        
        if login and email and password:
            self.auth_manager.login(email, password)
        
        return self
    
    @allure.step("结束测试会话")
    def stop(self):
        """结束会话"""
        self.logger.info(f"结束会话: {self.session_id}")
        
        # 执行清理任务
        self._run_cleanup_tasks()
        
        # 登出
        if self.auth_manager.is_authenticated():
            try:
                self.auth_manager.logout()
            except Exception as e:
                self.logger.warning(f"登出时出错: {e}")
        
        # 关闭API客户端
        self.api_client.close()
        
        self._is_active = False
        
        # 从注册表中移除
        if self.session_id in SessionManager._sessions:
            del SessionManager._sessions[self.session_id]
        
        if SessionManager._active_session == self.session_id:
            SessionManager._active_session = None
    
    def _run_cleanup_tasks(self):
        """执行清理任务"""
        self.logger.info(f"执行 {len(self._cleanup_tasks)} 个清理任务")
        
        for task in reversed(self._cleanup_tasks):
            try:
                task()
            except Exception as e:
                self.logger.error(f"清理任务执行失败: {e}")
        
        self._cleanup_tasks.clear()
    
    def add_cleanup_task(self, task: callable):
        """
        添加清理任务
        
        Args:
            task: 清理函数
        """
        self._cleanup_tasks.append(task)
    
    def set_test_data(self, key: str, value: Any):
        """
        设置测试数据
        
        Args:
            key: 数据键
            value: 数据值
        """
        self._test_data[key] = value
    
    def get_test_data(self, key: str, default: Any = None) -> Any:
        """
        获取测试数据
        
        Args:
            key: 数据键
            default: 默认值
        
        Returns:
            数据值
        """
        return self._test_data.get(key, default)
    
    def clear_test_data(self):
        """清除所有测试数据"""
        self._test_data.clear()
    
    @property
    def is_active(self) -> bool:
        """会话是否处于活动状态"""
        return self._is_active
    
    @contextmanager
    def context(self, login: bool = False, email: Optional[str] = None, password: Optional[str] = None):
        """
        会话上下文管理器
        
        使用示例：
            with SessionManager().context(login=True, email='test@example.com', password='123456'):
                # 执行测试
                pass
        """
        try:
            self.start(login=login, email=email, password=password)
            yield self
        finally:
            self.stop()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
