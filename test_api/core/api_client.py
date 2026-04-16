"""
ApiClient - 统一的API客户端

功能：
1. Token管理和自动刷新
2. 请求签名处理
3. 统一请求/响应处理
4. 自动重试机制
5. 请求/响应日志记录
6. Allure报告集成
"""
import json
import time
import hmac
import hashlib
import base64
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import allure

from config.env_config import EnvConfig
from utils.logger import get_logger
from utils.allure_helper import AllureHelper


@dataclass
class ApiResponse:
    """API响应数据类"""
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    raw_response: requests.Response
    
    @property
    def is_success(self) -> bool:
        """是否成功响应"""
        return 200 <= self.status_code < 300
    
    @property
    def is_error(self) -> bool:
        """是否错误响应"""
        return not self.is_success


class ApiClient:
    """
    API客户端
    
    封装了所有API调用的通用逻辑：
    - Token管理
    - 请求签名
    - 重试机制
    - 日志记录
    - Allure报告
    """
    
    _instance = None
    _session: requests.Session = None
    _token: Optional[str] = None
    _token_expires_at: Optional[float] = None
    _refresh_token: Optional[str] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, env: Optional[str] = None):
        if self._session is None:
            self.logger = get_logger(__name__)
            self.env_config = EnvConfig.get_env_config()
            self.allure_helper = AllureHelper()
            
            self._init_session()
            self._setup_retry_strategy()
    
    def _init_session(self):
        """初始化HTTP会话"""
        self._session = requests.Session()
        
        # 设置默认请求头
        self._session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'apikey': self.env_config.anon_key,
            'Authorization': f'Bearer {self.env_config.anon_key}'
        })
    
    def _setup_retry_strategy(self):
        """配置重试策略"""
        retry_strategy = Retry(
            total=self.env_config.retry_times,
            backoff_factor=self.env_config.retry_interval,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
    
    def set_token(self, token: str, expires_in: Optional[int] = None):
        """
        设置访问令牌
        
        Args:
            token: 访问令牌
            expires_in: 过期时间（秒）
        """
        self._token = token
        self._session.headers['Authorization'] = f'Bearer {token}'
        
        if expires_in:
            self._token_expires_at = time.time() + expires_in
        
        self.logger.info("Token已更新")
    
    def clear_token(self):
        """清除令牌"""
        self._token = None
        self._token_expires_at = None
        self._refresh_token = None
        
        # 恢复使用anon_key
        self._session.headers['Authorization'] = f'Bearer {self.env_config.anon_key}'
        self.logger.info("Token已清除")
    
    def is_token_expired(self) -> bool:
        """检查Token是否过期"""
        if self._token_expires_at is None:
            return False
        # 提前5分钟认为过期
        return time.time() >= (self._token_expires_at - 300)
    
    def _generate_signature(self, method: str, url: str, params: Dict, body: Any) -> str:
        """
        生成请求签名
        
        使用HMAC-SHA256算法生成签名
        """
        # 构建签名字符串
        timestamp = str(int(time.time()))
        nonce = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
        
        # 按字母顺序排序参数
        sorted_params = sorted(params.items()) if params else []
        param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # 构建待签名字符串
        body_str = json.dumps(body, sort_keys=True) if body else ''
        sign_str = f"{method.upper()}&{url}&{timestamp}&{nonce}&{param_str}&{body_str}"
        
        # 使用anon_key作为密钥生成签名
        signature = hmac.new(
            self.env_config.anon_key.encode(),
            sign_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp, nonce
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        base_url: Optional[str] = None,
        params: Optional[Dict] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: Optional[int] = None,
        use_signature: bool = False,
        **kwargs
    ) -> ApiResponse:
        """
        执行HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            base_url: 基础URL（默认使用rest_url）
            params: URL参数
            data: 表单数据
            json_data: JSON数据
            headers: 额外请求头
            files: 文件数据
            timeout: 超时时间
            use_signature: 是否使用签名
        
        Returns:
            ApiResponse对象
        """
        # 构建完整URL
        base = base_url or self.env_config.rest_url
        url = urljoin(base + '/', endpoint.lstrip('/'))
        
        # 合并请求头
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # 如果需要签名
        if use_signature:
            signature, timestamp, nonce = self._generate_signature(
                method, url, params or {}, json_data
            )
            request_headers.update({
                'X-Signature': signature,
                'X-Timestamp': timestamp,
                'X-Nonce': nonce
            })
        
        # 记录请求信息到Allure
        self.allure_helper.attach_request_info(
            method=method,
            url=url,
            headers=request_headers,
            params=params,
            body=json_data or data
        )
        
        # 记录请求日志
        self.logger.info(f"请求: {method} {url}")
        self.logger.debug(f"请求头: {request_headers}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"请求体: {json_data or data}")
        
        start_time = time.time()
        
        try:
            # 执行请求
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                files=files,
                timeout=timeout or self.env_config.timeout,
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
            
            # 创建响应对象
            api_response = ApiResponse(
                status_code=response.status_code,
                data=response_data,
                headers=dict(response.headers),
                response_time=response_time,
                raw_response=response
            )
            
            # 记录响应信息到Allure
            self.allure_helper.attach_response_info(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response_data,
                response_time=response_time
            )
            
            # 记录响应日志
            self.logger.info(f"响应: {response.status_code} ({response_time:.3f}s)")
            self.logger.debug(f"响应数据: {response_data}")
            
            return api_response
            
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"连接错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"请求异常: {e}")
            raise
    
    # HTTP方法快捷方式
    def get(
        self,
        endpoint: str,
        base_url: Optional[str] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> ApiResponse:
        """GET请求"""
        return self._make_request(
            'GET', endpoint, base_url, params=params, headers=headers, **kwargs
        )
    
    def post(
        self,
        endpoint: str,
        base_url: Optional[str] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs
    ) -> ApiResponse:
        """POST请求"""
        return self._make_request(
            'POST', endpoint, base_url, json_data=json_data, data=data, 
            headers=headers, params=params, **kwargs
        )
    
    def put(
        self,
        endpoint: str,
        base_url: Optional[str] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> ApiResponse:
        """PUT请求"""
        return self._make_request(
            'PUT', endpoint, base_url, json_data=json_data, data=data,
            headers=headers, **kwargs
        )
    
    def patch(
        self,
        endpoint: str,
        base_url: Optional[str] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> ApiResponse:
        """PATCH请求"""
        return self._make_request(
            'PATCH', endpoint, base_url, json_data=json_data, data=data,
            headers=headers, **kwargs
        )
    
    def delete(
        self,
        endpoint: str,
        base_url: Optional[str] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> ApiResponse:
        """DELETE请求"""
        return self._make_request(
            'DELETE', endpoint, base_url, params=params, headers=headers, **kwargs
        )
    
    def close(self):
        """关闭会话"""
        if self._session:
            self._session.close()
            self._session = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
