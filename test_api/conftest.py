"""
pytest配置文件

提供测试夹具和钩子函数
"""
import os
import sys
import pytest
import allure
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.session_manager import SessionManager
from core.api_client import ApiClient
from core.auth_manager import AuthManager
from utils.logger import setup_logging
from utils.screenshot_helper import get_screenshot_helper
from utils.allure_helper import AllureHelper


def pytest_configure(config):
    """pytest配置"""
    # 设置日志
    setup_logging()
    
    # 注册自定义标记
    markers = [
        "smoke: 冒烟测试",
        "regression: 回归测试",
        "api: 接口测试",
        "auth: 认证测试",
        "study_session: 学习会话测试",
        "subject: 科目测试",
        "user_settings: 用户设置测试",
        "positive: 正向测试",
        "negative: 负向测试",
        "critical: 关键用例"
    ]
    
    for marker in markers:
        config.addinivalue_line("markers", marker)


@pytest.fixture(scope="session")
def api_client():
    """API客户端夹具"""
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def auth_manager(api_client):
    """认证管理器夹具"""
    return AuthManager(api_client)


@pytest.fixture(scope="function")
def session():
    """测试会话夹具"""
    session = SessionManager()
    yield session
    if session.is_active:
        session.stop()


@pytest.fixture(scope="function")
def authenticated_session(auth_manager):
    """已认证会话夹具"""
    session = SessionManager()
    session.start()
    
    # 执行登录
    # 注意：实际使用时需要提供有效的测试账号
    # auth_manager.login("test@example.com", "Test123456")
    
    yield session
    
    if session.is_active:
        session.stop()


@pytest.fixture(scope="function")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent.parent / 'data'


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试报告钩子
    
    在测试失败时自动截图
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # 获取测试名称
        test_name = item.name
        
        # 获取错误信息
        error_info = str(report.longrepr) if report.longrepr else None
        
        # 截图
        try:
            from utils.screenshot_helper import take_screenshot_on_failure
            take_screenshot_on_failure(test_name, error_info)
        except Exception as e:
            print(f"截图失败: {e}")


def pytest_collection_modifyitems(config, items):
    """
    修改测试项集合
    
    自动添加标记
    """
    for item in items:
        # 根据测试名称自动添加标记
        if "auth" in item.nodeid.lower():
            item.add_marker(pytest.mark.auth)
        if "study_session" in item.nodeid.lower():
            item.add_marker(pytest.mark.study_session)
        if "subject" in item.nodeid.lower():
            item.add_marker(pytest.mark.subject)
        if "user_settings" in item.nodeid.lower():
            item.add_marker(pytest.mark.user_settings)


@pytest.fixture(scope="session", autouse=True)
def setup_allure_environment():
    """设置Allure环境信息"""
    # 创建environment.properties文件
    allure_results_dir = Path("reports/allure-results")
    allure_results_dir.mkdir(parents=True, exist_ok=True)
    
    env_file = allure_results_dir / "environment.properties"
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(f"Python={sys.version}\n")
        f.write(f"Platform={sys.platform}\n")
        f.write(f"Project=StudyStride API Test\n")
        f.write(f"Environment={os.getenv('TEST_ENV', 'dev')}\n")
