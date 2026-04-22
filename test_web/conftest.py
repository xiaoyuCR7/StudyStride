import pytest
from playwright.sync_api import Playwright, sync_playwright
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.config import config
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


@pytest.fixture(scope="session", autouse=True)
def session_logger():
    """会话级别的日志记录"""
    logger.info("=" * 60)
    logger.info("测试会话开始")
    logger.info(f"基础URL: {config.BASE_URL}")
    logger.info(f"浏览器: {config.BROWSER}")
    logger.info(f"无头模式: {config.HEADLESS}")
    logger.info("=" * 60)
    yield
    logger.info("=" * 60)
    logger.info("测试会话结束")
    logger.info("=" * 60)


@pytest.fixture(scope="function", autouse=True)
def test_logger(request):
    """测试函数级别的日志记录"""
    test_name = request.node.name
    logger.info(f"开始测试: {test_name}")
    yield
    logger.info(f"结束测试: {test_name}")

@pytest.fixture(scope="session")
def playwright():
    """Playwright会话"""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright):
    """浏览器实例"""
    browser_launch_options = config.get_browser_launch_options()
    
    if config.BROWSER == 'chromium':
        browser = playwright.chromium.launch(**browser_launch_options)
    elif config.BROWSER == 'firefox':
        browser = playwright.firefox.launch(**browser_launch_options)
    elif config.BROWSER == 'webkit':
        browser = playwright.webkit.launch(**browser_launch_options)
    else:
        raise ValueError(f"不支持的浏览器: {config.BROWSER}")
    
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def page(browser):
    """页面实例"""
    page = browser.new_page()
    page.goto(config.BASE_URL)
    page.wait_for_load_state("networkidle")
    yield page
    page.close()

@pytest.fixture(scope="session")
def base_url():
    """基础URL"""
    return config.BASE_URL
