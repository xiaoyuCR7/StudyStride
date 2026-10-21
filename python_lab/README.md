# python_lab

开源软件实验二任务一的 Python 演示项目：学习时长统计模块 + pytest 单元测试。

- `study_stats.py`：学习记录统计（总时长、平均时长、按科目过滤、连续打卡天数、等级划分）
- `test_study_stats.py`：pytest 单元测试
- 由 `.github/workflows/ci.yml` 中的 `python-test` job 在每次 push/PR 时自动运行

本地运行：

```bash
cd python_lab
pip install -r requirements.txt
pytest -v
```
