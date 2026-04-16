#!/usr/bin/env python3
"""
配置检查工具

验证环境配置是否正确加载
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.env_config import EnvConfig
from config.config_manager import get_config


def print_separator(title: str = ""):
    """打印分隔线"""
    width = 60
    if title:
        print(f"\n{'=' * width}")
        print(f" {title}")
        print(f"{'=' * width}")
    else:
        print(f"{'=' * width}")


def check_env_file():
    """检查.env文件"""
    print_separator("检查 .env 文件")
    
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if env_file.exists():
        print(f"✓ .env 文件存在: {env_file}")
        
        # 读取.env文件内容
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 统计配置项
        config_count = sum(1 for line in lines if '=' in line and not line.strip().startswith('#'))
        print(f"  包含 {config_count} 个配置项")
        
        return True
    else:
        print(f"✗ .env 文件不存在")
        
        if env_example.exists():
            print(f"\n  提示: 可以复制 .env.example 文件创建 .env:")
            print(f"    cp .env.example .env")
        
        return False


def check_yaml_config():
    """检查YAML配置"""
    print_separator("检查 YAML 配置")
    
    config_file = project_root / "config" / "settings.yaml"
    
    if config_file.exists():
        print(f"✓ settings.yaml 文件存在: {config_file}")
        
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            envs = config.get('environments', {})
            print(f"  配置了 {len(envs)} 个环境: {', '.join(envs.keys())}")
            
            return True
        except Exception as e:
            print(f"✗ 读取 YAML 配置失败: {e}")
            return False
    else:
        print(f"✗ settings.yaml 文件不存在")
        return False


def check_current_config():
    """检查当前加载的配置"""
    print_separator("当前加载的配置")
    
    try:
        config = get_config()
        env_config = EnvConfig.get_env_config()
        current_env = EnvConfig.get_current_env()
        
        print(f"当前环境: {current_env}")
        print(f"配置来源: {'环境变量/.env' if _is_from_env() else 'settings.yaml'}")
        print()
        print(f"Base URL: {env_config.base_url}")
        print(f"Auth URL: {env_config.auth_url}")
        print(f"REST URL: {env_config.rest_url}")
        print(f"Timeout: {env_config.timeout}s")
        print(f"Retry Times: {env_config.retry_times}")
        
        # 检查密钥是否已设置
        if env_config.anon_key and env_config.anon_key not in ['your-anon-key', 'test-anon-key', 'prod-anon-key']:
            print(f"\n✓ API Key 已配置")
        else:
            print(f"\n✗ API Key 未配置或使用了默认值")
        
        return True
        
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        return False


def _is_from_env() -> bool:
    """检查配置是否来自环境变量"""
    import os
    current_env = EnvConfig.get_current_env().upper()
    return bool(os.getenv(f'{current_env}_SUPABASE_URL'))


def check_dependencies():
    """检查依赖包"""
    print_separator("检查依赖包")
    
    required_packages = [
        'pytest',
        'requests',
        'yaml',
        'dotenv',
        'allure'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            elif package == 'dotenv':
                __import__('dotenv')
            elif package == 'allure':
                __import__('allure_pytest')
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (未安装)")
            missing.append(package)
    
    if missing:
        print(f"\n  提示: 运行以下命令安装依赖:")
        print(f"    pip install -r requirements.txt")
    
    return len(missing) == 0


def main():
    """主函数"""
    print_separator("StudyStride API 测试配置检查")
    
    results = []
    
    # 检查依赖
    results.append(("依赖包", check_dependencies()))
    
    # 检查配置文件
    has_env = check_env_file()
    has_yaml = check_yaml_config()
    results.append((".env 文件", has_env))
    results.append(("YAML 配置", has_yaml))
    
    # 检查当前配置
    config_ok = check_current_config()
    results.append(("配置加载", config_ok))
    
    # 总结
    print_separator("检查结果")
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    print()
    
    if all_passed:
        print("🎉 所有检查通过！可以开始运行测试。")
        print()
        print("运行测试命令:")
        print("  ./run.sh all       # Linux/Mac")
        print("  run.bat all        # Windows")
        print("  python run_tests.py all")
        return 0
    else:
        print("⚠️  部分检查未通过，请根据提示修复问题。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
