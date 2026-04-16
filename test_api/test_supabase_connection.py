#!/usr/bin/env python3
"""
Supabase 连接测试脚本

测试 Supabase 认证和数据存储功能
"""
import os
import sys
import json
import requests
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.env_config import EnvConfig

def print_separator(title: str = ""):
    """打印分隔线"""
    width = 60
    if title:
        print(f"\n{'=' * width}")
        print(f" {title}")
        print(f"{'=' * width}")
    else:
        print(f"{'=' * width}")

def test_supabase_connection():
    """测试 Supabase 连接"""
    print_separator("测试 Supabase 连接")
    
    try:
        # 获取配置
        base_url = EnvConfig.get_base_url()
        auth_url = EnvConfig.get_auth_url()
        rest_url = EnvConfig.get_rest_url()
        anon_key = EnvConfig.get_anon_key()
        
        print(f"Base URL: {base_url}")
        print(f"Auth URL: {auth_url}")
        print(f"REST URL: {rest_url}")
        print(f"Anon Key: {anon_key[:20]}...")
        
        # 测试 API 连接
        headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json'
        }
        
        # 测试认证端点
        auth_test_url = f"{auth_url}/session"
        print(f"\n测试认证端点: {auth_test_url}")
        
        response = requests.get(auth_test_url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json() if response.ok else response.text}")
        
        if response.status_code == 200:
            print("✓ 认证端点连接成功")
        else:
            print("✗ 认证端点连接失败")
        
        # 测试 REST 端点
        rest_test_url = f"{rest_url}/subjects?select=*&limit=1"
        print(f"\n测试 REST 端点: {rest_test_url}")
        
        response = requests.get(rest_test_url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json() if response.ok else response.text}")
        
        if response.status_code == 200:
            print("✓ REST 端点连接成功")
        else:
            print("✗ REST 端点连接失败")
        
        return True
        
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

def test_user_signup():
    """测试用户注册"""
    print_separator("测试用户注册")
    
    try:
        auth_url = EnvConfig.get_auth_url()
        anon_key = EnvConfig.get_anon_key()
        
        # 生成随机邮箱
        import uuid
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test123456"
        
        print(f"测试注册邮箱: {email}")
        
        # 注册请求
        signup_url = f"{auth_url}/signup"
        headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'email': email,
            'password': password
        }
        
        print(f"发送注册请求到: {signup_url}")
        response = requests.post(signup_url, headers=headers, json=data, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2) if response.ok else response.text}")
        
        if response.status_code == 200:
            print("✓ 用户注册成功")
            # 提取 token
            data = response.json()
            if 'access_token' in data:
                print("✓ 成功获取 access_token")
                return data['access_token']
            else:
                print("✗ 响应中未找到 access_token")
                return None
        else:
            print("✗ 用户注册失败")
            return None
            
    except Exception as e:
        print(f"✗ 注册测试失败: {e}")
        return None

def test_user_login(token: str):
    """测试用户登录"""
    print_separator("测试用户登录")
    
    try:
        auth_url = EnvConfig.get_auth_url()
        anon_key = EnvConfig.get_anon_key()
        
        # 登录请求
        login_url = f"{auth_url}/token"
        headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'email': 'test@example.com',
            'password': 'Test123456'
        }
        
        print(f"发送登录请求到: {login_url}")
        response = requests.post(login_url, headers=headers, json=data, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2) if response.ok else response.text}")
        
        if response.status_code == 200:
            print("✓ 用户登录成功")
            return True
        else:
            print("✗ 用户登录失败")
            return False
            
    except Exception as e:
        print(f"✗ 登录测试失败: {e}")
        return False

def test_data_storage(access_token: str):
    """测试数据存储"""
    print_separator("测试数据存储")
    
    if not access_token:
        print("✗ 没有访问令牌，跳过数据存储测试")
        return False
    
    try:
        rest_url = EnvConfig.get_rest_url()
        
        # 测试存储学习会话
        session_url = f"{rest_url}/study_sessions"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        import uuid
        from datetime import datetime
        
        data = {
            'id': str(uuid.uuid4()),
            'user_id': 'test-user-id',  # 这里需要使用实际的用户ID
            'subject': '测试科目',
            'content': '测试内容',
            'duration': 3600,
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'session_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        print(f"发送数据存储请求到: {session_url}")
        response = requests.post(session_url, headers=headers, json=data, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2) if response.ok else response.text}")
        
        if response.status_code in [200, 201]:
            print("✓ 数据存储成功")
            return True
        else:
            print("✗ 数据存储失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据存储测试失败: {e}")
        return False

def main():
    """主函数"""
    print_separator("Supabase 连接测试")
    
    # 测试连接
    connection_ok = test_supabase_connection()
    
    # 测试注册
    access_token = test_user_signup()
    
    # 测试登录
    login_ok = test_user_login(access_token)
    
    # 测试数据存储
    storage_ok = test_data_storage(access_token)
    
    # 总结
    print_separator("测试结果")
    
    tests = [
        ("API 连接", connection_ok),
        ("用户注册", access_token is not None),
        ("用户登录", login_ok),
        ("数据存储", storage_ok)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 所有测试通过！Supabase 连接正常。")
        print("\n可能的前端问题：")
        print("1. 前端 API 调用代码错误")
        print("2. 前端环境配置错误")
        print("3. CORS 跨域问题")
        print("4. 前端表单验证问题")
    else:
        print("⚠️  部分测试未通过，Supabase 后端可能存在问题。")
        print("\n可能的后端问题：")
        print("1. Supabase 项目配置错误")
        print("2. API Key 无效")
        print("3. 数据库表结构问题")
        print("4. 认证服务未启用")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
