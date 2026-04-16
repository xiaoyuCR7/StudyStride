# StudyStride API 自动化测试框架

企业级Python API接口自动化测试项目，支持多环境切换、数据驱动、Allure报告等功能。

## 项目结构

```
test_api/
├── config/                 # 配置模块
│   ├── __init__.py
│   ├── settings.yaml      # 主配置文件
│   ├── config_manager.py  # 配置管理器
│   └── env_config.py      # 环境配置快捷访问
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── api_client.py      # API客户端（Token、签名处理）
│   ├── auth_manager.py    # 认证管理器
│   ├── session_manager.py # 会话管理器
│   ├── request_builder.py # 请求构建器
│   └── response_handler.py # 响应处理器
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── logger.py          # 日志工具
│   ├── allure_helper.py   # Allure报告辅助
│   ├── data_provider.py   # 数据提供器
│   ├── screenshot_helper.py # 截图辅助
│   └── retry_helper.py    # 重试辅助
├── data/                   # 测试数据
│   ├── auth_data.yaml
│   ├── study_session_data.yaml
│   ├── subject_data.yaml
│   └── user_settings_data.yaml
├── testcases/              # 测试用例
│   ├── __init__.py
│   ├── conftest.py        # pytest配置
│   ├── test_auth.py       # 认证接口测试
│   ├── test_study_session.py # 学习会话测试
│   ├── test_subject.py    # 科目接口测试
│   └── test_user_settings.py # 用户设置测试
├── reports/                # 测试报告
├── logs/                   # 日志文件
├── screenshots/            # 截图文件
├── requirements.txt        # 依赖包
├── pytest.ini             # pytest配置
├── run_tests.py           # Python运行脚本
├── run.bat                # Windows批处理脚本
├── run.sh                 # Linux/Mac脚本
└── README.md              # 项目说明
```

## 功能特性

### 1. 多环境配置
- 支持 YAML/JSON 配置文件
- 环境变量覆盖
- 多环境切换（dev/test/prod）

### 2. API客户端封装
- Token 自动管理
- 请求签名处理
- 统一请求/响应处理
- 自动重试机制

### 3. 数据驱动测试
- 支持 YAML、JSON、CSV、Excel 数据格式
- 参数化测试
- 动态用例ID

### 4. 测试标记和分组
- 冒烟测试（smoke）
- 回归测试（regression）
- 正向/负向测试（positive/negative）
- 功能模块标记

### 5. 失败重试
- 自动重试机制
- 指数退避策略
- 自定义重试条件

### 6. Allure报告
- 专业的测试报告
- 请求/响应详情
- 失败自动截图
- 测试步骤追踪
- 历史趋势分析

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

项目支持两种配置方式：**`.env` 文件（推荐）** 或 `settings.yaml`

#### 方式一：使用 .env 文件（推荐）

1. 复制示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入实际配置：
```env
# 当前环境
TEST_ENV=dev

# 开发环境配置
DEV_SUPABASE_URL=https://your-project-id.supabase.co
DEV_SUPABASE_ANON_KEY=your-anon-key

# 测试环境配置
TEST_SUPABASE_URL=https://test-project-id.supabase.co
TEST_SUPABASE_ANON_KEY=test-anon-key
```

**优点：**
- 敏感信息不会提交到版本控制（`.env` 在 `.gitignore` 中）
- 每个开发者可以有独立的本地配置
- 支持环境变量覆盖

#### 方式二：使用 settings.yaml

编辑 `config/settings.yaml` 文件：

```yaml
environments:
  dev:
    base_url: "https://your-project-id.supabase.co"
    auth_url: "https://your-project-id.supabase.co/auth/v1"
    rest_url: "https://your-project-id.supabase.co/rest/v1"
    anon_key: "your-anon-key"
```

**配置优先级：** `.env` 文件 > 环境变量 > `settings.yaml`

### 3. 运行测试

**运行所有测试：**
```bash
# Windows
run.bat all

# Linux/Mac
./run.sh all

# Python
python run_tests.py all
```

**运行冒烟测试：**
```bash
run.bat smoke
./run.sh smoke
```

**运行回归测试：**
```bash
run.bat regression
./run.sh regression
```

**按标记运行：**
```bash
./run.sh marker -m "auth and smoke"
./run.sh marker -m "study_session"
```

**按关键字运行：**
```bash
./run.sh keyword -k "login"
```

### 4. 生成报告

```bash
# 生成HTML报告
run.bat report
./run.sh report

# 启动报告服务
run.bat serve
./run.sh serve -p 8080
```

## 核心组件使用

### API客户端

```python
from core.api_client import ApiClient
from core.response_handler import ResponseHandler

# 创建客户端
client = ApiClient()

# 发送请求
response = client.get(endpoint='study_sessions')

# 处理响应
handler = ResponseHandler(response)
handler.assert_success().assert_field_equals('status', 'ok')
```

### 认证管理

```python
from core.auth_manager import AuthManager

auth = AuthManager(client)

# 登录
auth.login('user@example.com', 'password')

# 获取当前用户
user = auth.get_current_user()

# 登出
auth.logout()
```

### 数据驱动测试

```python
from utils.data_provider import DataProvider, TestData
import pytest

# 加载测试数据
@pytest.mark.parametrize(
    "test_data",
    DataProvider().load_yaml("auth_data.yaml"),
    ids=lambda x: x.name
)
def test_login(test_data: TestData):
    # 使用 test_data.data 和 test_data.expected
    pass
```

### 请求构建器

```python
from core.request_builder import RequestBuilder, SortOrder

builder = RequestBuilder()
params = (builder
    .select('*')
    .eq('user_id', '123')
    .order('created_at', SortOrder.DESC)
    .limit(10)
    .build())

response = client.get(endpoint='study_sessions', params=params)
```

## 环境变量

可以通过环境变量覆盖配置：

```bash
# 设置环境
export TEST_ENV=test

# 覆盖配置
export TEST_API_BASE_URL=https://custom-url.supabase.co
export TEST_API_ANON_KEY=custom-key
export TEST_API_TIMEOUT=60
```

## 测试标记说明

| 标记 | 说明 |
|------|------|
| smoke | 冒烟测试，快速验证核心功能 |
| regression | 回归测试，完整功能验证 |
| api | 接口测试 |
| auth | 认证相关测试 |
| study_session | 学习会话测试 |
| subject | 科目测试 |
| user_settings | 用户设置测试 |
| positive | 正向测试 |
| negative | 负向测试 |
| critical | 关键用例 |

## 报告查看

测试执行后会生成Allure报告：

```bash
# 生成并打开报告
allure serve reports/allure-results

# 或生成静态报告
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

## 扩展开发

### 添加新的API接口测试

1. 在 `testcases/` 目录创建测试文件
2. 继承测试基类或使用pytest fixtures
3. 使用数据驱动加载测试数据
4. 添加适当的标记

### 添加新的数据文件

1. 在 `data/` 目录创建 YAML/JSON/CSV 文件
2. 定义测试用例数据
3. 使用 `DataProvider` 加载

## 注意事项

1. 运行测试前确保已正确配置API环境
2. 敏感信息（如API密钥）建议通过环境变量设置
3. 测试数据会根据实际情况可能需要调整
4. 截图功能需要安装 Pillow 库

## 许可证

MIT License
