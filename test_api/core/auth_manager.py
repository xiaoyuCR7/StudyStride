"""
认证管理器

处理用户认证相关功能：
- 用户登录
- 用户注册
- Token刷新
- 会话管理
"""
from typing import Optional, Dict, Any
import allure

from core.api_client import ApiClient, ApiResponse
from config.env_config import EnvConfig
from utils.logger import get_logger


class AuthManager:
    """认证管理器"""
    
    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client or ApiClient()
        self.env_config = EnvConfig.get_env_config()
        self.logger = get_logger(__name__)
        
        self._current_user: Optional[Dict[str, Any]] = None
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
    
    @allure.step("用户登录: {email}")
    def login(self, email: str, password: str) -> ApiResponse:
        """
        用户登录
        
        Args:
            email: 用户邮箱
            password: 用户密码
        
        Returns:
            ApiResponse对象
        """
        self.logger.info(f"用户登录: {email}")
        
        response = self.api_client.post(
            endpoint='/token',
            base_url=self.env_config.auth_url,
            json_data={
                'email': email,
                'password': password
            },
            params={
                'grant_type': 'password'    
            }
        )
        
        if response.is_success:
            # 提取token信息
            data = response.data
            if 'access_token' in data:
                self._access_token = data['access_token']
                self._refresh_token = data.get('refresh_token')
                self._current_user = data.get('user')
                
                # 设置token到api_client
                expires_in = data.get('expires_in', 3600)
                self.api_client.set_token(self._access_token, expires_in)
                
                self.logger.info(f"登录成功: {email}")
            else:
                self.logger.warning("响应中未找到access_token")
        else:
            self.logger.error(f"登录失败: {response.data}")
        
        return response
    
    @allure.step("用户注册: {email}")
    def signup(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> ApiResponse:
        """
        用户注册
        
        Args:
            email: 用户邮箱
            password: 用户密码
            user_metadata: 用户元数据
        
        Returns:
            ApiResponse对象
        """
        self.logger.info(f"用户注册: {email}")
        
        json_data = {
            'email': email,
            'password': password
        }
        
        if user_metadata:
            json_data['data'] = user_metadata
        
        response = self.api_client.post(
            endpoint='/signup',
            base_url=self.env_config.auth_url,
            json_data=json_data
        )
        
        if response.is_success:
            self.logger.info(f"注册成功: {email}")
        else:
            self.logger.error(f"注册失败: {response.data}")
        
        return response
    
    @allure.step("刷新Token")
    def refresh_token(self) -> ApiResponse:
        """
        刷新访问令牌
        
        Returns:
            ApiResponse对象
        """
        if not self._refresh_token:
            raise ValueError("没有可用的refresh_token")
        
        self.logger.info("刷新Token")
        
        response = self.api_client.post(
            endpoint='/token',
            base_url=self.env_config.auth_url,
            json_data={
                'refresh_token': self._refresh_token
            }
        )
        
        if response.is_success:
            data = response.data
            self._access_token = data.get('access_token')
            self._refresh_token = data.get('refresh_token')
            
            if self._access_token:
                expires_in = data.get('expires_in', 3600)
                self.api_client.set_token(self._access_token, expires_in)
                self.logger.info("Token刷新成功")
        else:
            self.logger.error(f"Token刷新失败: {response.data}")
        
        return response
    
    @allure.step("获取当前会话")
    def get_session(self) -> ApiResponse:
        """
        获取当前会话信息
        
        Returns:
            ApiResponse对象
        """
        self.logger.info("获取当前会话")
        
        response = self.api_client.get(
            endpoint='/session',
            base_url=self.env_config.auth_url
        )
        
        if response.is_success:
            self._current_user = response.data.get('user')
        
        return response
    
    @allure.step("用户登出")
    def logout(self) -> ApiResponse:
        """
        用户登出
        
        Returns:
            ApiResponse对象
        """
        self.logger.info("用户登出")
        
        response = self.api_client.post(
            endpoint='/logout',
            base_url=self.env_config.auth_url
        )
        
        # 清除本地状态
        self._current_user = None
        self._access_token = None
        self._refresh_token = None
        self.api_client.clear_token()
        
        self.logger.info("登出成功")
        return response
    
    @allure.step("重置密码: {email}")
    def reset_password(self, email: str) -> ApiResponse:
        """
        重置密码
        
        Args:
            email: 用户邮箱
        
        Returns:
            ApiResponse对象
        """
        self.logger.info(f"重置密码: {email}")
        
        response = self.api_client.post(
            endpoint='/recover',
            base_url=self.env_config.auth_url,
            json_data={
                'email': email
            }
        )
        
        return response
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self._access_token is not None and not self.api_client.is_token_expired()
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        return self._current_user
    
    def get_user_id(self) -> Optional[str]:
        """获取当前用户ID"""
        if self._current_user:
            return self._current_user.get('id')
        return None
    
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        return self._access_token
