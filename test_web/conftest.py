import pytest
from playwright.sync_api import Playwright, sync_playwright
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.config import config

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
