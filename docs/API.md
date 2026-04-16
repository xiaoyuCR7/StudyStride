# StudyStride 后端接口说明（Supabase / PostgREST）

本文档面向**接口自动化测试**：说明认证方式、REST 路径、请求头、请求体字段及典型响应结构。  
项目 URL 以实际环境为准，下文中 `{SUPABASE_URL}` 表示形如 `https://<project-ref>.supabase.co` 的根地址。

---

## 1. 公共约定

### 1.1 请求头（访问数据库 REST）

| Header | 说明 |
|--------|------|
| `apikey` | 匿名（anon）或 publishable 公钥，与前端 `VITE_SUPABASE_ANON_KEY` 一致 |
| `Authorization` | `Bearer <access_token>`，登录后由 Auth 接口返回的 `access_token` |
| `Content-Type` | `application/json`（POST/PATCH 时） |
| `Prefer` | 可选：`return=representation` 使 INSERT/PATCH 返回行数据 |

未登录仅带 `apikey` 时，受 RLS 限制，**无法**读写 `subjects` / `study_sessions` / `user_settings`（策略要求 `auth.uid()`）。

### 1.2 错误响应（PostgREST）

HTTP 非 2xx 时，body 多为 JSON 数组，元素含 `message`、`code`、`hint` 等，例如：

```json
{
  "code": "42501",
  "details": null,
  "hint": null,
  "message": "new row violates row-level security policy"
}
```

---

## 2. 认证（Supabase Auth）

根路径：`{SUPABASE_URL}/auth/v1/`

### 2.1 邮箱注册

- **方法 / 路径**：`POST /auth/v1/signup`
- **请求头**：`apikey: <anon key>`，`Content-Type: application/json`
- **请求体**：

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

- **成功响应**（约 200）：包含 `access_token`、`refresh_token`、`user` 等（若项目开启邮箱确认，`access_token` 可能为空直至验证完成）。

### 2.2 邮箱密码登录

- **方法 / 路径**：`POST /auth/v1/token?grant_type=password`
- **请求头**：`apikey: <anon key>`，`Content-Type: application/json`
- **请求体**：

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

- **成功响应**（约 200）：

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "<refresh>",
  "user": {
    "id": "<uuid>",
    "email": "user@example.com",
    "aud": "authenticated",
    "role": "authenticated",
    "created_at": "2026-01-01T00:00:00.000Z",
    "updated_at": "2026-01-01T00:00:00.000Z"
  }
}
```

自动化测试中：保存 `access_token`，后续请求数据库 REST 时置于 `Authorization: Bearer <access_token>`。

### 2.3 刷新令牌（可选）

- **方法 / 路径**：`POST /auth/v1/token?grant_type=refresh_token`
- **请求体**：`{ "refresh_token": "<refresh_token>" }`

### 2.4 登出（服务端撤销 refresh token，可选）

- **方法 / 路径**：`POST /auth/v1/logout`
- **请求头**：`Authorization: Bearer <access_token>`，`apikey: <anon key>`

---

## 3. 数据库 REST（PostgREST）

根路径：`{SUPABASE_URL}/rest/v1/`  
以下均需：`apikey` + `Authorization: Bearer <access_token>`（已登录用户）。

### 3.1 `subjects`（科目）

| 列名 | 类型 | 说明 |
|------|------|------|
| `id` | uuid | 主键，默认 `gen_random_uuid()` |
| `user_id` | uuid | 关联 `auth.users`，插入时必须等于当前用户 |
| `name` | text | 科目名称 |
| `created_at` | timestamptz | 默认 `now()` |

#### 查询列表

- **方法 / 路径**：`GET /rest/v1/subjects?select=*&order=created_at.asc`
- **成功响应**（约 200）：JSON 数组。

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "…",
    "name": "数学",
    "created_at": "2026-04-02T08:00:00.000Z"
  }
]
```

#### 单条插入

- **方法 / 路径**：`POST /rest/v1/subjects`
- **请求体**（可显式传 `id`，否则由数据库生成）：

```json
{
  "name": "英语"
}
```

注意：PostgREST 需在请求中带上 `user_id` **或** 由触发器/默认值写入；当前表无默认值，**客户端应传入** `user_id` 为当前用户 UUID（与 JWT `sub` 一致）。

#### 更新

- **方法 / 路径**：`PATCH /rest/v1/subjects?id=eq.<uuid>`
- **请求体**：`{ "name": "新名称" }`

#### 删除

- **方法 / 路径**：`DELETE /rest/v1/subjects?id=eq.<uuid>`

---

### 3.2 `study_sessions`（学习记录）

| 列名 | 类型 | 说明 |
|------|------|------|
| `id` | uuid | 主键 |
| `user_id` | uuid | 当前用户 |
| `subject` | text | 科目名称 |
| `content` | text | 学习内容 |
| `duration` | int | 时长（秒）≥ 0 |
| `start_time` | timestamptz | 开始时间 |
| `end_time` | timestamptz | 结束时间，可 `null` |
| `session_date` | date | 学习日期（YYYY-MM-DD） |

#### 查询列表

- **方法 / 路径**：`GET /rest/v1/study_sessions?select=*&order=start_time.desc`

#### 插入

- **方法 / 路径**：`POST /rest/v1/study_sessions`
- **请求体示例**：

```json
{
  "subject": "数学",
  "content": "习题第3章",
  "duration": 3600,
  "start_time": "2026-04-02T09:00:00.000Z",
  "end_time": "2026-04-02T10:00:00.000Z",
  "session_date": "2026-04-02"
}
```

需包含 `user_id`（当前用户），或与策略一致的字段。

#### 更新

- **方法 / 路径**：`PATCH /rest/v1/study_sessions?id=eq.<uuid>`
- **请求体示例**：`{ "duration": 1800, "content": "修订" }`

#### 删除

- **方法 / 路径**：`DELETE /rest/v1/study_sessions?id=eq.<uuid>`

#### 按用户清空（测试用）

- **方法 / 路径**：`DELETE /rest/v1/study_sessions?user_id=eq.<当前用户uuid>`

---

### 3.3 `user_settings`（用户设置）

| 列名 | 类型 | 说明 |
|------|------|------|
| `user_id` | uuid | 主键，关联用户 |
| `reminder_interval` | int | 休息提醒间隔（分钟）> 0 |

#### 查询当前用户设置

- **方法 / 路径**：`GET /rest/v1/user_settings?select=*&user_id=eq.<uuid>`

#### 插入或更新（Upsert）

- **方法 / 路径**：`POST /rest/v1/user_settings`
- **请求头**附加：`Prefer: resolution=merge-duplicates`
- **请求体**：

```json
{
  "user_id": "<当前用户uuid>",
  "reminder_interval": 45
}
```

---

## 4. 与前端行为的对应关系

| 前端操作 | 数据落点 |
|----------|----------|
| 未登录 | `localStorage`（`studySessions`、`studySubjects`、`reminderInterval`） |
| 已登录 | 上述三张表；会话与科目保存时由前端执行「删后全量插入」同步（与自动化单条 REST 调用等价效果为最终一致） |

---

## 5. 自动化测试建议顺序

1. `POST /auth/v1/token?grant_type=password` 获取 `access_token`。  
2. 使用 `access_token` 调用 `GET /rest/v1/subjects` 等验证 200。  
3. 对 `study_sessions`、`subjects` 做增删改查后断言状态码与 body。  
4. 使用错误/未授权 token 断言 401 或 RLS 拒绝（如 403/42501）。

---

## 6. 项目实例（开发环境）

- **REST 根**：`https://mrabnfywybyseoswlcjv.supabase.co/rest/v1/`  
- **Auth 根**：`https://mrabnfywybyseoswlcjv.supabase.co/auth/v1/`  

公钥请使用 Supabase 控制台 **Project Settings → API** 中的 anon / publishable key，勿将 **service_role** 密钥写入前端或公开仓库。
