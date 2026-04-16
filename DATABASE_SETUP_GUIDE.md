# StudyStride 数据库设置指南

## 概述

本文档将指导您如何在 Supabase 控制台中设置 StudyStride 应用的完整数据库结构，以解决前端无法注册和登录的问题。

## 问题原因分析

之前的问题是：
- ❌ 注册时出现错误：`Database error saving new user`
- ❌ 缺少 `public.users` 表，导致触发器失败
- ❌ 缺少必要的数据库表结构

## 解决方案

我们已经为您创建了完整的 SQL 脚本文件 `database_setup.sql`，它包含：

✅ `public.users` 表（解决注册错误）
✅ `study_sessions` 表（学习会话记录）
✅ `subjects` 表（学习科目管理）
✅ `user_settings` 表（用户设置）
✅ 完整的行级安全策略（RLS）
✅ 自动同步 `auth.users` 到 `public.users` 的触发器
✅ 更新时间戳触发器

## 操作步骤

### 第一步：打开 Supabase 控制台

1. 访问 https://supabase.com/dashboard
2. 登录您的账户
3. 选择您的 StudyStride 项目
   - 项目 ID：`juxaojqqosinnvfzfqfo`

### 第二步：打开 SQL 编辑器

1. 在左侧导航栏中，点击 **SQL Editor**（SQL 编辑器）
2. 点击 **New query**（新建查询）按钮
3. 您会看到一个空白的 SQL 编辑器窗口

### 第三步：复制并运行 SQL 脚本

1. 在项目目录中找到 `database_setup.sql` 文件
   - 路径：`d:\trae\项目\StudyStride\database_setup.sql`
2. 打开该文件，复制所有内容
3. 将内容粘贴到 Supabase 的 SQL 编辑器中
4. 点击 **Run**（运行）按钮（▶️）
5. 等待脚本执行完成

### 第四步：验证设置

脚本运行成功后，您可以：

1. 在左侧导航栏中点击 **Table Editor**（表编辑器）
2. 您应该能看到以下表：
   - `users`
   - `study_sessions`
   - `subjects`
   - `user_settings`

### 第五步：测试注册功能

现在您可以测试注册功能了：

1. 确保您的前端开发服务器正在运行：
   ```bash
   npm run dev
   ```
2. 在浏览器中打开 http://localhost:5174
3. 导航到登录/注册页面
4. 尝试注册一个新用户
5. 现在注册应该可以成功了！

## 脚本内容说明

### 1. 表结构

#### `public.users` 表
- 存储用户基本信息
- 与 `auth.users` 表同步
- 包含字段：id, email, created_at, updated_at

#### `public.study_sessions` 表
- 存储学习会话记录
- 包含字段：id, user_id, subject, content, duration, start_time, end_time, session_date

#### `public.subjects` 表
- 存储学习科目
- 包含字段：id, user_id, name, created_at, updated_at

#### `public.user_settings` 表
- 存储用户设置
- 包含字段：user_id, reminder_interval, created_at, updated_at

### 2. 安全策略 (RLS)

所有表都启用了行级安全策略，确保：
- 用户只能查看和修改自己的数据
- 数据完全隔离，保护用户隐私

### 3. 触发器

- `on_auth_user_created`：在用户注册时自动同步到 `public.users` 表
- 所有表都有自动更新 `updated_at` 字段的触发器

## 故障排除

### 如果脚本运行失败

1. 检查是否有语法错误
2. 确保您有足够的权限
3. 尝试分批运行脚本（先运行创建表的部分，再运行策略和触发器）

### 如果注册仍然失败

1. 确认 SQL 脚本已完整运行
2. 查看 Supabase 控制台的 **Logs**（日志）页面
3. 检查 **Auth**（认证）页面的设置

## 下一步

数据库设置完成后，您的 StudyStride 应用应该可以正常使用了！

✅ 用户可以正常注册和登录
✅ 学习数据可以保存到云端
✅ 数据在用户之间完全隔离

祝您学习愉快！🚀
