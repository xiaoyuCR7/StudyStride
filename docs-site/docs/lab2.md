# 实验二：GitHub Actions 与 GitHub Pages

## 任务一：GitHub Actions 自动化测试

- Python 项目位于仓库 `python_lab/` 目录，包含学习统计模块与 pytest 单元测试；
- 工作流配置文件为 `.github/workflows/ci.yml`，其中 `python-test` job 在每次 push / pull_request 时：
  1. `actions/checkout` 检出代码；
  2. `actions/setup-python` 安装 Python 3.13；
  3. `pip install -r requirements.txt` 安装 pytest；
  4. `pytest -v` 运行单元测试并在 Actions 页面查看结果。

## 任务二：MkDocs + GitHub Pages 自动部署

- 文档源位于 `docs-site/`（`mkdocs.yml` + `docs/`）；
- `ci.yml` 的 `deploy` job 使用 `actions/configure-pages` 开启 Pages，
  构建 Vite 前端与 MkDocs 文档后，经 `upload-pages-artifact` / `deploy-pages` 发布；
- 部署完成后访问：<https://xiaoyucr7.github.io/StudyStride/docs-site/>

## 触发方式

```bash
git add .
git commit -m "docs: update docs-site"
git push origin main   # 推送后自动触发 CI/CD Pipeline
```

在仓库的 **Actions** 页签可观察工作流执行过程与各 job 日志。
