# StudyStride 文档站

欢迎来到 **StudyStride** 项目文档站。本站点由 MkDocs 构建，并通过 GitHub Actions 自动部署到 GitHub Pages。

## 项目简介

StudyStride 是一个简便的学习打卡软件，用于记录每日学习时长与科目，帮助使用者坚持学习计划。

## 主要功能

- 学习记录：按日期、科目记录学习时长
- 统计面板：总时长、平均时长、连续打卡天数
- 等级体系：按累计学习时长划分 LV1 ~ LV4 等级

## 文档导航

| 页面 | 内容 |
| ---- | ---- |
| [使用指南](guide.md) | 安装、运行与日常使用 |
| [实验二说明](lab2.md) | GitHub Actions 与 GitHub Pages 自动化流程说明 |

## 自动化部署

每次向 `main` 分支推送代码，`.github/workflows/ci.yml` 中的 `deploy` job 会：

1. 构建 Vite 前端产物到 `dist/`；
2. 使用 MkDocs 构建本文档站到 `dist/docs-site/`；
3. 通过 `actions/upload-pages-artifact` 与 `actions/deploy-pages` 发布到 GitHub Pages。

站点地址：<https://xiaoyucr7.github.io/StudyStride/docs-site/>
