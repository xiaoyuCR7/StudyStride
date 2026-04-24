import pytest
from playwright.sync_api import Playwright, sync_playwright
import sys
import os
import traceback

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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """记录测试结果"""
    outcome = yield
    rep = outcome.get_result()
    
    # 为测试项添加测试结果属性
    setattr(item, "rep_call", rep)


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
def page(browser, request):
    """页面实例"""
    # 设置视频录制目录
    video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
    os.makedirs(video_dir, exist_ok=True)
    logger.info(f"视频录制目录: {video_dir}")
    
    # 为每个测试创建新的 context，并启用视频录制
    test_name = request.node.name
    context = browser.new_context(
        record_video_dir=video_dir,
        record_video_size={"width": 1280, "height": 720}
    )
    
    page = context.new_page()
    page.goto(config.BASE_URL)
    page.wait_for_load_state("networkidle")
    
    # 返回一个包装的 page 对象，包含测试名称信息
    page._test_name = test_name
    page._context = context
    
    yield page
    
    # 检查测试是否失败
    has_failed = request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False
    logger.info(f"测试 {test_name} 失败: {has_failed}")
    
    if has_failed:
        # 在测试失败时，获取视频并添加到 allure 报告
        try:
            import allure
            logger.info("开始处理失败测试的视频")
            
            # 先关闭 context 确保视频保存
            context.close()
            
            # 尝试获取视频路径
            video_path = None
            try:
                video = page.video
                if video:
                    video_path = video.path()
                    logger.info(f"视频文件路径: {video_path}")
                else:
                    logger.error("页面没有视频对象")
            except Exception as e:
                logger.error(f"获取视频路径失败: {e}")
                logger.error(traceback.format_exc())
            
            if video_path and os.path.exists(video_path):
                logger.info(f"视频文件存在，大小: {os.path.getsize(video_path)} bytes")
                
                try:
                    with open(video_path, 'rb') as f:
                        video_data = f.read()
                    logger.info(f"读取视频文件成功，大小: {len(video_data)} bytes")
                    
                    logger.info("开始附加视频到 Allure 报告")
                    logger.info(f"视频数据大小: {len(video_data)} bytes")
                    logger.info(f"视频文件名: {test_name}_failure_video.webm")
                    
                    try:
                        allure.attach(
                            video_data, 
                            name=f"{test_name}_failure_video",
                            attachment_type=allure.attachment_type.WEBM,
                            extension="webm"
                        )
                        logger.info("✅ 视频附加成功！")
                    except Exception as attach_error:
                        logger.error(f"❌ 视频附加失败: {attach_error}")
                        logger.error(traceback.format_exc())
                    
                    logger.info("视频附加操作完成")
                except Exception as e:
                    logger.error(f"读取或附加视频失败: {e}")
                    logger.error(traceback.format_exc())
            else:
                logger.error(f"视频文件不存在: {video_path}")
        except Exception as e:
            logger.error(f"添加视频到报告失败: {e}")
            logger.error(traceback.format_exc())
    else:
        # 测试通过时，删除视频文件以节省空间
        try:
            context.close()
            
            video_path = None
            try:
                video = page.video
                if video:
                    video_path = video.path()
                    logger.info(f"删除通过测试的视频: {video_path}")
            except Exception as e:
                logger.error(f"获取视频路径失败: {e}")
            
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"已删除通过测试的视频: {video_path}")
            else:
                logger.info("没有视频文件需要删除")
        except Exception as e:
            logger.error(f"删除视频失败: {e}")
            logger.error(traceback.format_exc())
