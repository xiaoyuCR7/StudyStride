# 使用指南

## 环境要求

- Node.js 24+
- Python 3.13+（用于 API/Web 测试与文档构建）

## 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/xiaoyuCR7/StudyStride.git
cd StudyStride

# 2. 安装依赖并启动前端
npm ci
npm run dev
```

启动后访问终端提示的本地地址（默认 `http://localhost:5173/`）。

## 学习记录说明

在学习页面选择科目、填写学习时长并提交，系统会自动累计：

- **总时长**：所有记录分钟数之和；
- **平均时长**：总时长 / 记录条数；
- **连续打卡**：按日期计算的最长连续天数；
- **等级**：LV1（<60 分钟）→ LV2（<300 分钟）→ LV3（<1000 分钟）→ LV4。

## 本地构建文档站

```bash
pip install mkdocs
cd docs-site
mkdocs serve
```

浏览器打开 `http://127.0.0.1:8000/` 即可预览本文档站。
