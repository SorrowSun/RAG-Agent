# 企业知识库RAG问答系统 —— 后端API接口设计文档

> 文档版本：v1.0
> 编写日期：2026-06-26
> 适用前端技术栈：Vue3 + TypeScript + Vite + Ant Design Vue + Pinia + Axios + ECharts

---

## 一、全局约定

### 1.1 BASE_URL

```
开发环境：http://localhost:8080/api
生产环境：https://your-domain.com/api
```

### 1.2 请求头规范

| 请求头 | 必填 | 说明 |
|--------|------|------|
| Content-Type | 是 | `application/json` |
| Authorization | 是 | `Bearer {token}`，登录后所有接口均需携带 |

### 1.3 通用响应格式

所有接口返回统一结构：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | number | 状态码，200为成功 |
| message | string | 提示信息 |
| data | any | 响应数据，类型随接口变化 |

### 1.4 分页参数

列表查询接口统一使用以下分页参数：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 当前页码，默认1 |
| pageSize | number | 否 | 每页条数，默认10 |

分页响应统一格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```

### 1.5 错误码定义

| 状态码 | 说明 |
|--------|------|
| 200 | 操作成功 |
| 400 | 请求参数错误 |
| 401 | 未授权，token无效或过期 |
| 403 | 无权访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 1001 | 手机号已注册 |
| 1002 | 邮箱已被绑定 |
| 1003 | 验证码错误 |
| 1004 | 密码错误 |
| 1005 | 账号不存在 |
| 1006 | 邮箱未验证 |

---

## 二、认证与用户模块

### 2.1 用户注册

- **接口地址**：`POST /api/auth/register`
- **功能说明**：用户注册，默认角色为普通员工
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| phone | string | 是 | 手机号，中国大陆11位 |
| realName | string | 是 | 真实姓名，至少2个字符 |
| department | string | 是 | 工作部门 |
| password | string | 是 | 密码，至少6位 |
| confirmPassword | string | 是 | 确认密码，必须与密码一致 |

- **请求示例**：

```json
{
  "phone": "13812345678",
  "realName": "张三",
  "department": "技术研发部",
  "password": "123456",
  "confirmPassword": "123456"
}
```

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 用户ID |
| phone | string | 手机号 |
| realName | string | 真实姓名 |
| department | string | 工作部门 |
| role | string | 用户角色，固定为 `employee` |
| token | string | JWT Token |

- **响应示例**：

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": "user_001",
    "phone": "13812345678",
    "realName": "张三",
    "department": "技术研发部",
    "role": "employee",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### 2.2 用户登录（账号密码）

- **接口地址**：`POST /api/auth/login`
- **功能说明**：通过手机号或已绑定邮箱登录
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| account | string | 是 | 手机号或邮箱 |
| password | string | 是 | 密码 |

- **请求示例**：

```json
{
  "account": "13812345678",
  "password": "123456"
}
```

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| token | string | JWT Token |
| expiresAt | number | Token过期时间戳 |
| user | UserInfo | 完整用户信息 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expiresAt": 1750934400000,
    "user": {
      "id": "user_001",
      "username": "张三",
      "phone": "13812345678",
      "email": "",
      "realName": "张三",
      "avatar": "",
      "role": "employee",
      "roleName": "普通员工",
      "department": "技术研发部",
      "departmentId": "tech",
      "roles": ["employee"],
      "permissions": []
    }
  }
}
```

### 2.3 发送验证码

- **接口地址**：`POST /api/auth/send-code`
- **功能说明**：发送验证码到手机或邮箱
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| target | string | 是 | 手机号或邮箱 |
| type | string | 是 | `phone` 或 `email` |
| purpose | string | 是 | 用途：`register` / `login` / `bind_email` / `change_password` / `change_phone` |

- **请求示例**：

```json
{
  "target": "13812345678",
  "type": "phone",
  "purpose": "register"
}
```

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否发送成功 |
| expireSeconds | number | 验证码有效期（秒） |

- **响应示例**：

```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "success": true,
    "expireSeconds": 300
  }
}
```

### 2.4 退出登录

- **接口地址**：`POST /api/auth/logout`
- **功能说明**：用户退出登录，服务端使token失效
- **请求参数**：无
- **响应示例**：

```json
{
  "code": 200,
  "message": "退出成功",
  "data": null
}
```

### 2.5 获取当前用户信息

- **接口地址**：`GET /api/auth/current-user`
- **功能说明**：获取当前登录用户的完整信息
- **请求参数**：无（通过Authorization头鉴权）
- **响应参数**：UserInfo 完整对象
- **响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "user_001",
    "username": "张三",
    "phone": "13812345678",
    "email": "zhangsan@example.com",
    "emailVerified": true,
    "realName": "张三",
    "avatar": "https://example.com/avatar.jpg",
    "role": "employee",
    "roleName": "普通员工",
    "department": "技术研发部",
    "departmentId": "tech",
    "roles": ["employee"],
    "permissions": []
  }
}
```

### 2.6 获取用户列表

- **接口地址**：`GET /api/users`
- **功能说明**：管理员获取所有用户列表（支持分页和筛选）
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 当前页码，默认1 |
| pageSize | number | 否 | 每页条数，默认10 |
| name | string | 否 | 姓名 |
| phone | str | 否 | 手机号 |
| department | str | 否 | 部门（code和name都可以，看下面更新接口，有图片） |
| role | string | 否 | 按角色筛选 |
| status | string | 否 | 按状态筛选 `active` / `disabled` |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | RegisteredUser[] | 用户列表 |
| total | number | 总条数 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": "user_001",
        "username": "张三",
        "phone": "13812345678",
        "email": "zhangsan@example.com",
        "realName": "张三",
        "password": "",
        "role": "employee",
        "roleName": "普通员工",
        "department": "技术研发部",
        "departmentId": "tech",
        "avatar": "",
        "status": "active",
        "createTime": "2026-06-01 10:00:00",
        "lastLoginTime": "2026-06-26 15:30:00"
      }
    ],
    "total": 11
  }
}
```

### 2.7 保存/更新用户

- **接口地址**：`PUT /api/users/{id}`
- **功能说明**：管理员编辑用户信息（包括分配角色和部门）
- **路径参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | string | 用户ID |

- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| realName | string | 否 | 真实姓名 |
| role | string | 否 | 角色 `employee` / `manager` / `leader` / `admin` |
| department | string | 否 | 工作部门 |
| status | string | 否 | 状态 `active` / `disabled` |

- **请求示例**：

```
http://127.0.0.1:8000/api/users/{user_id}
body:
{
  "realName": "李四",
  "role": "admin",
  "department": "tech",
  "status": "active"
}
```

department:

code 和name都可以

![image-20260627150409808](C:\Users\22830\AppData\Roaming\Typora\typora-user-images\image-20260627150409808.png)

- **响应示例**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 2.8 更新用户状态

- **接口地址**：`PATCH /api/users/{id}/status`
- **功能说明**：启用或禁用用户
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 是 | `active` 或 `disabled` |

- **响应示例**：

```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null
}
```

### 2.9 删除用户

- **接口地址**：`DELETE /api/users/{id}`
- **功能说明**：删除用户（仅管理员可操作）
- **响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 2.10 绑定邮箱

- **接口地址**：`POST /api/users/bind-email`
- **请求头带token**
- **功能说明**：用户绑定邮箱
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| email | string | 是 | 邮箱地址 |
| verifyCode | string | 是 | 验证码 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "邮箱绑定成功",
  "data": {
    "email": "zhangsan@example.com",
    "emailVerified": true
  }
}
```

### 2.11 修改手机号

- **接口地址**：`POST /api/users/{id}/change-phone`
- **功能说明**：用户修改手机号
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| newPhone | string | 是 | 新手机号 |
| verifyCode | string | 是 | 验证码 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "手机号修改成功",
  "data": {
    "phone": "13912345678"
  }
}
```

### 2.12 修改密码

- **接口地址**：`POST /api/auth/change-password`
- **功能说明**：通过验证码修改密码
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| verifyType | string | 是 | 验证方式：`phone` / `email` |
| verifyCode | string | 是 | 验证码 |
| newPassword | string | 是 | 新密码 |
| confirmPassword | string | 是 | 确认新密码 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

---

## 三、模型管理模块

### 3.1 获取模型列表

- **接口地址**：`GET /api/models`
- **功能说明**：获取所有模型配置列表
- **请求参数**：无
- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | ModelConfig[] | 模型配置列表 |

ModelConfig 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 模型唯一ID |
| name | string | 模型显示名称 |
| modelIdentifier | string | 模型标识符（如 qwen2.5-72b-instruct） |
| modelType | string | 模型类型：`cloud` / `local` |
| apiUrl | string | API端点地址 |
| apiKey | string | API密钥（可选） |
| enabled | boolean | 是否启用 |
| isDefault | boolean | 是否为默认模型 |
| temperature | number | 温度参数 |
| maxTokens | number | 最大Token数 |
| maxOutputTokens | number | 最大输出Token数 |
| contextWindow | string | 上下文窗口（如 "128K"） |
| description | string | 模型描述（可选） |
| tags | string[] | 推荐标签数组 |
| sortOrder | number | 展示排序 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": "model_qwen2_5_72b",
        "name": "Qwen2.5-72B",
        "modelIdentifier": "qwen2.5-72b-instruct",
        "modelType": "cloud",
        "apiUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "apiKey": "",
        "enabled": true,
        "isDefault": true,
        "temperature": 0.7,
        "maxTokens": 8192,
        "maxOutputTokens": 4096,
        "contextWindow": "128K",
        "description": "",
        "tags": ["适合中文问答", "推荐用于复杂推理"],
        "sortOrder": 1
      }
    ]
  }
}
```

### 3.2 保存模型配置

- **接口地址**：`PUT /api/models`
- **功能说明**：保存或更新模型列表（支持批量保存）
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| models | ModelConfig[] | 是 | 模型配置数组 |
| operator | string | 是 | 操作人用户名 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "保存成功",
  "data": null
}
```

### 3.3 获取已启用模型列表

- **接口地址**：`GET /api/models/enabled`
- **功能说明**：获取所有已启用的模型（供前端下拉框使用）
- **响应参数**：ModelConfig[]（仅包含 enabled=true 的模型）

### 3.4 获取当前模型

- **接口地址**：`GET /api/models/current`
- **功能说明**：获取当前用户选中的模型
- **响应参数**：ModelConfig

### 3.5 设置当前模型

- **接口地址**：`PUT /api/models/current`
- **功能说明**：设置当前用户使用的模型
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| modelId | string | 是 | 模型ID |

- **响应示例**：

```json
{
  "code": 200,
  "message": "设置成功",
  "data": null
}
```

### 3.6 获取RAG参数

- **接口地址**：`GET /api/rag-params`
- **功能说明**：获取RAG检索参数配置
- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| maxRetrieveRounds | number | 最大检索轮次 |
| topK | number | 返回Top-K文档 |
| similarityThreshold | number | 相似度阈值（0-1） |
| enableBM25 | boolean | 是否启用BM25 |
| enableQAMatch | boolean | 是否启用QA匹配 |
| enableQueryRewrite | boolean | 是否启用查询重写 |
| enableReflection | boolean | 是否启用反思 |
| enableAttachmentPriority | boolean | 是否附件优先 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "maxRetrieveRounds": 3,
    "topK": 5,
    "similarityThreshold": 0.75,
    "enableBM25": true,
    "enableQAMatch": true,
    "enableQueryRewrite": true,
    "enableReflection": true,
    "enableAttachmentPriority": false
  }
}
```

### 3.7 保存RAG参数

- **接口地址**：`PUT /api/rag-params`
- **功能说明**：保存RAG参数配置
- **请求参数**：RagParams 对象
- **响应示例**：

```json
{
  "code": 200,
  "message": "保存成功",
  "data": null
}
```

### 3.8 获取模型操作日志

- **接口地址**：`GET /api/models/audit-logs`
- **功能说明**：获取模型配置操作日志
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | ModelAuditLog[] | 日志列表 |
| total | number | 总条数 |

ModelAuditLog 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 日志ID |
| timestamp | string | 操作时间 |
| operator | string | 操作人 |
| action | string | 操作类型：添加模型/编辑模型/删除模型/启用模型/停用模型/保存排序 |
| modelName | string | 模型名称 |
| detail | string | 操作详情 |

---

## 四、智能问答模块

### 4.1 获取推荐问题

- **接口地址**：`GET /api/qa/suggest-questions`
- **功能说明**：根据用户输入获取相关推荐问题
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | string | 是 | 用户当前输入 |
| limit | number | 否 | 返回数量，默认5 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| questions | RelatedQuestion[] | 推荐问题列表 |

RelatedQuestion 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 问题ID |
| question | string | 问题内容 |
| similarity | number | 相似度 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "questions": [
      { "id": "q1", "question": "年假天数如何计算？", "similarity": 0.92 },
      { "id": "q2", "question": "年假可以累积吗？", "similarity": 0.85 }
    ]
  }
}
```

### 4.2 发送消息（流式SSE）

- **接口地址**：`POST /api/qa/stream`
- **功能说明**：发送用户问题，返回AI流式回答
- **Content-Type**：`text/event-stream`
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| conversationId | string | 是 | 对话ID |
| message | string | 是 | 用户输入内容 |
| model | string | 是 | 使用的模型ID |
| attachments | Attachment[] | 否 | 附件列表 |

- **SSE响应格式**：

服务端以 Server-Sent Events 格式逐字返回：

```
event: message
data: {"type": "content", "content": "年"}

event: message
data: {"type": "content", "content": "假"}

event: citation
data: {"sources": [{"documentName": "员工手册", "similarity": 0.95, "snippet": "..."}]}

event: reasoning
data: {"steps": [{"step": 1, "type": "retrieve", "description": "检索相关文档"}]}

event: done
data: {"messageId": "msg_001", "totalTokens": 256}
```

### 4.3 生成AI回答（非流式）

- **接口地址**：`POST /api/qa/answer`
- **功能说明**：生成AI回答（非流式，返回完整结果）
- **请求参数**：同 4.2
- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| message | Message | AI回复消息 |
| citations | Citation[] | 引用来源 |
| reasoning | RagReasoning[] | 推理过程 |

Message 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 消息ID |
| conversationId | string | 对话ID |
| type | string | `user` / `bot` |
| content | string | 消息内容 |
| timestamp | number | 时间戳 |
| model | string | 使用的模型 |

Citation 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 引用ID |
| messageId | string | 消息ID |
| sourceId | string | 来源文档ID |
| sourceName | string | 来源文档名称 |
| sourceType | string | `document` / `attachment` |
| content | string | 引用内容片段 |
| similarity | number | 相似度 |
| pageNumber | number | 页码（可选） |

RagReasoning 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| step | number | 步骤序号 |
| type | string | `retrieve` / `rewrite` / `generate` / `reflect` / `summarize` |
| description | string | 步骤描述 |
| timestamp | number | 时间戳 |
| detail | string | 详细内容（可选） |

---

## 五、对话管理模块

### 5.1 获取对话列表

- **接口地址**：`GET /api/conversations`
- **功能说明**：获取当前用户的对话列表
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |
| status | string | 否 | `active` / `closed` |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | Conversation[] | 对话列表 |
| total | number | 总条数 |

Conversation 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 对话ID |
| title | string | 对话标题 |
| userId | string | 用户ID |
| model | string | 使用的模型 |
| status | string | `active` / `closed` |
| createdAt | number | 创建时间戳 |
| updatedAt | number | 更新时间戳 |
| messageCount | number | 消息数量 |

### 5.2 获取对话详情

- **接口地址**：`GET /api/conversations/{id}`
- **功能说明**：获取指定对话的完整详情（含消息和附件）
- **响应参数**：ConversationDetail

### 5.3 创建对话

- **接口地址**：`POST /api/conversations`
- **功能说明**：创建新对话
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 否 | 对话标题（可选，默认取第一条消息前20字） |
| model | string | 否 | 指定模型ID（可选，默认使用当前模型） |

- **响应参数**：Conversation

### 5.4 更新对话

- **接口地址**：`PUT /api/conversations/{id}`
- **功能说明**：更新对话信息
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 否 | 新标题 |
| status | string | 否 | `active` / `closed` |

### 5.5 删除对话

- **接口地址**：`DELETE /api/conversations/{id}`
- **功能说明**：删除对话（移动到回收站）
- **响应示例**：

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 5.6 置顶/取消置顶对话

- **接口地址**：`PATCH /api/conversations/{id}/pin`
- **功能说明**：切换对话置顶状态
- **响应示例**：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "pinned": true
  }
}
```

### 5.7 清空回收站

- **接口地址**：`DELETE /api/conversations/recycle-bin`
- **功能说明**：永久删除回收站中的所有对话
- **响应示例**：

```json
{
  "code": 200,
  "message": "清空成功",
  "data": null
}
```

### 5.8 恢复对话

- **接口地址**：`POST /api/conversations/{id}/restore`
- **功能说明**：从回收站恢复对话
- **响应示例**：

```json
{
  "code": 200,
  "message": "恢复成功",
  "data": null
}
```

### 5.9 消息点赞/点踩

- **接口地址**：`POST /api/messages/{id}/feedback`
- **功能说明**：对AI消息进行点赞或点踩
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 是 | `like` / `dislike` |

- **响应示例**：

```json
{
  "code": 200,
  "message": "反馈成功",
  "data": {
    "hasLiked": true,
    "hasDisliked": false,
    "likes": 5,
    "dislikes": 0
  }
}
```

---

## 六、对话记录模块

### 6.1 获取问答历史记录

- **接口地址**：`GET /api/qa-history`
- **功能说明**：获取问答历史记录（按角色权限过滤）
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |
| startTime | number | 否 | 开始时间戳 |
| endTime | number | 否 | 结束时间戳 |
| department | string | 否 | 按部门筛选 |
| model | string | 否 | 按模型筛选 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | QaHistoryItem[] | 历史记录列表 |
| total | number | 总条数 |

QaHistoryItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 记录ID |
| questionSummary | string | 问题摘要 |
| answerSummary | string | 回答摘要 |
| conversationName | string | 对话名称 |
| model | string | 使用的模型 |
| knowledgeBase | string | 知识库 |
| hasAttachment | boolean | 是否有附件 |
| satisfaction | string | `liked` / `disliked` / `none` |
| askTime | number | 提问时间戳 |
| asker | string | 提问人 |
| department | string | 所属部门 |
| messages | HistoryMessage[] | 消息详情 |

### 6.2 获取单条历史详情

- **接口地址**：`GET /api/qa-history/{id}`
- **功能说明**：获取单条历史记录的完整详情
- **响应参数**：QaHistoryItem（含完整消息列表）

---

## 七、反馈中心模块

### 7.1 提交反馈

- **接口地址**：`POST /api/feedback`
- **功能说明**：用户对问答结果提交反馈
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| messageId | string | 是 | 消息ID |
| score | number | 是 | 评分 1-5 |
| feedbackType | string | 是 | `positive` / `negative` / `neutral` |
| comment | string | 否 | 评论内容 |

- **响应示例**：

```json
{
  "code": 200,
  "message": "反馈提交成功",
  "data": {
    "id": "fb_001"
  }
}
```

### 7.2 获取反馈列表

- **接口地址**：`GET /api/feedback`
- **功能说明**：获取反馈列表（按角色权限过滤）
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |
| status | string | 否 | `pending` / `adopted` / `processed` / `rejected` |
| startTime | number | 否 | 开始时间 |
| endTime | number | 否 | 结束时间 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | FeedbackItem[] | 反馈列表 |
| total | number | 总条数 |

FeedbackItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 反馈ID |
| conversationId | string | 对话ID |
| conversationTitle | string | 对话标题 |
| question | string | 用户问题 |
| answerSummary | string | 回答摘要 |
| model | string | 使用的模型 |
| department | string | 所属部门 |
| hasAttachment | boolean | 是否有附件 |
| sources | Source[] | 引用来源 |
| reason | string | 反馈原因 |
| comment | string | 评论 |
| suggestDirection | string | 建议方向 |
| submitTime | number | 提交时间 |
| submitter | string | 提交人 |
| status | string | `pending` / `adopted` / `processed` / `rejected` |
| adminNote | string | 管理员备注 |

### 7.3 更新反馈状态

- **接口地址**：`PATCH /api/feedback/{id}/status`
- **功能说明**：管理员更新反馈处理状态
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 是 | `pending` / `adopted` / `processed` / `rejected` |
| adminNote | string | 否 | 管理员备注 |

### 7.4 获取反馈统计

- **接口地址**：`GET /api/feedback/stats`
- **功能说明**：获取反馈统计数据
- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| total | number | 总反馈数 |
| positiveCount | number | 正面反馈数 |
| negativeCount | number | 负面反馈数 |
| neutralCount | number | 中性反馈数 |
| avgScore | number | 平均评分 |
| trend | TrendItem[] | 趋势数据 |

TrendItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期 |
| count | number | 数量 |
| avgScore | number | 平均评分 |

---

## 八、知识库运营模块

### 8.1 获取知识库统计

- **接口地址**：`GET /api/knowledge/stats`
- **功能说明**：获取知识库整体统计数据
- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| totalDocuments | number | 文档总数 |
| totalKnowledgePoints | number | 知识点总数 |
| totalCategories | number | 分类数 |
| totalFiles | number | 文件数 |
| pendingReview | number | 待审核数 |
| processing | number | 处理中数 |
| completed | number | 已完成数 |
| failed | number | 处理失败数 |

### 8.2 智能分类

- **接口地址**：`POST /api/knowledge/auto-classify`
- **功能说明**：上传文档后自动分类
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fileName | string | 是 | 文件名 |
| fileContent | string | 是 | 文件内容或URL |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| category | string | 推荐分类 |
| confidence | number | 置信度 |
| suggestedTags | string[] | 推荐标签 |

### 8.3 上传文件

- **接口地址**：`POST /api/knowledge/upload`
- **功能说明**：上传知识文档
- **Content-Type**：`multipart/form-data`
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 文件对象 |
| category | string | 否 | 指定分类 |
| tags | string[] | 否 | 标签数组 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 上传记录ID |
| fileName | string | 文件名 |
| fileSize | number | 文件大小 |
| status | string | `uploading` / `success` / `failed` |
| uploadedAt | number | 上传时间 |

### 8.4 获取上传记录

- **接口地址**：`GET /api/knowledge/upload-records`
- **功能说明**：获取文档上传记录列表
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |
| status | string | 否 | `uploading` / `success` / `failed` |

- **响应参数**：UploadRecord[]

UploadRecord 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 记录ID |
| fileName | string | 文件名 |
| fileType | string | 文件类型 |
| fileSize | number | 文件大小 |
| category | string | 分类 |
| tags | string[] | 标签 |
| status | string | 状态 |
| uploadedBy | string | 上传人 |
| uploadedAt | number | 上传时间 |
| processedAt | number | 处理完成时间 |

### 8.5 获取版本历史

- **接口地址**：`GET /api/knowledge/versions`
- **功能说明**：获取知识库版本历史
- **响应参数**：VersionRecord[]

VersionRecord 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 版本ID |
| version | string | 版本号 |
| description | string | 版本描述 |
| documentCount | number | 文档数 |
| createdBy | string | 创建人 |
| createdAt | number | 创建时间 |

### 8.6 获取智能分类

- **接口地址**：`GET /api/knowledge/smart-categories`
- **功能说明**：获取智能分类结果
- **响应参数**：SmartCategory[]

SmartCategory 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 分类ID |
| name | string | 分类名称 |
| documentCount | number | 文档数 |
| confidence | number | 置信度 |

---

## 九、部门看板模块（经理）

### 9.1 获取部门看板数据

- **接口地址**：`GET /api/dashboard/department/{departmentId}`
- **功能说明**：获取指定部门的看板数据
- **路径参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| departmentId | string | 部门ID |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| metrics | DepartmentMetrics | 核心指标 |
| hotQuestions | HotQuestion[] | 热门问题Top10 |
| lowHitQuestions | LowHitQuestion[] | 低命中问题Top10 |
| employeeQaList | EmployeeQa[] | 员工问答明细 |
| trendData | TrendData | 趋势数据 |

DepartmentMetrics 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| totalQuestions | number | 总提问数 |
| avgResponseTime | number | 平均响应时间 |
| satisfactionRate | number | 满意度 |
| knowledgeCoverage | number | 知识覆盖率 |
| activeEmployees | number | 活跃员工数 |
| totalEmployees | number | 总员工数 |

HotQuestion 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 问题ID |
| question | string | 问题内容 |
| count | number | 提问次数 |
| trend | string | 趋势 `up` / `down` / `stable` |

LowHitQuestion 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 问题ID |
| question | string | 问题内容 |
| hitRate | number | 命中率 |
| count | number | 提问次数 |
| suggest | string | 改进建议 |

EmployeeQa 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 员工ID |
| name | string | 员工姓名 |
| questionCount | number | 提问数 |
| avgSatisfaction | number | 平均满意度 |
| lastActive | string | 最后活跃时间 |

### 9.2 获取部门趋势数据

- **接口地址**：`GET /api/dashboard/department/{departmentId}/trend`
- **功能说明**：获取部门趋势数据
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| period | string | 否 | `day` / `week` / `month`，默认 `day` |

- **响应参数**：TrendData

TrendData 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| dates | string[] | 日期数组 |
| qaCount | number[] | 问答数量数组 |
| avgResponseTime | number[] | 平均响应时间数组 |
| satisfactionRate | number[] | 满意度数组 |

### 9.3 获取部门热门问题

- **接口地址**：`GET /api/dashboard/department/{departmentId}/hot-questions`
- **功能说明**：获取部门热门问题
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | number | 否 | 返回数量，默认10 |

- **响应参数**：HotQuestion[]

### 9.4 获取部门低命中问题

- **接口地址**：`GET /api/dashboard/department/{departmentId}/low-hit-questions`
- **功能说明**：获取部门低命中问题
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | number | 否 | 返回数量，默认10 |

- **响应参数**：LowHitQuestion[]

### 9.5 获取员工问答明细

- **接口地址**：`GET /api/dashboard/department/{departmentId}/employees`
- **功能说明**：获取部门员工问答明细
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |

- **响应参数**：EmployeeQa[]

---

## 十、高层总览模块

### 10.1 获取全公司趋势数据

- **接口地址**：`GET /api/dashboard/company/trend`
- **功能说明**：获取全公司问答趋势
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| period | string | 否 | `day` / `week` / `month` |

- **响应参数**：TrendData（含所有部门数据）

### 10.2 获取全公司热门问题

- **接口地址**：`GET /api/dashboard/company/hot-questions`
- **功能说明**：获取全公司热门问题Top15
- **响应参数**：HotQuestion[]

### 10.3 获取知识缺口列表

- **接口地址**：`GET /api/dashboard/company/knowledge-gaps`
- **功能说明**：获取全公司知识缺口Top20
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数，默认20 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | KnowledgeGap[] | 知识缺口列表 |
| total | number | 总条数 |

KnowledgeGap 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 缺口ID |
| question | string | 问题内容 |
| count | number | 提问次数 |
| departments | string[] | 涉及部门 |
| status | string | `pending` / `processing` / `resolved` |
| priority | string | `high` / `medium` / `low` |
| createdAt | string | 创建时间 |

### 10.4 获取关键洞察

- **接口地址**：`GET /api/dashboard/company/insights`
- **功能说明**：获取关键洞察
- **响应参数**：KeyInsight[]

KeyInsight 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 洞察ID |
| type | string | 洞察类型 |
| title | string | 标题 |
| description | string | 描述 |
| impact | string | 影响程度 |
| suggestedAction | string | 建议行动 |

### 10.5 获取关注项

- **接口地址**：`GET /api/dashboard/company/attention`
- **功能说明**：获取需要关注的指标
- **响应参数**：AttentionItem[]

AttentionItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 关注项ID |
| metric | string | 指标名称 |
| currentValue | number | 当前值 |
| threshold | number | 阈值 |
| status | string | `normal` / `warning` / `critical` |
| suggestion | string | 建议 |

### 10.6 获取部门雷达数据

- **接口地址**：`GET /api/dashboard/company/radar`
- **功能说明**：获取部门对比雷达图数据
- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| indicators | RadarIndicator[] | 维度指标 |
| departments | RadarDepartment[] | 部门数据 |

RadarIndicator 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 维度名称 |
| max | number | 最大值 |

RadarDepartment 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 部门名称 |
| values | number[] | 各维度得分 |

### 10.7 获取部门排行榜

- **接口地址**：`GET /api/dashboard/company/ranking`
- **功能说明**：获取部门排行榜
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| dimension | string | 否 | 排序维度：`qaCount` / `satisfaction` / `coverage` / `responseTime` |

- **响应参数**：DepartmentRank[]

DepartmentRank 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| departmentId | string | 部门ID |
| departmentName | string | 部门名称 |
| value | number | 指标值 |
| rank | number | 排名 |
| trend | string | 趋势 |

---

## 十一、系统监控模块

### 11.1 获取系统指标

- **接口地址**：`GET /api/system/metrics`
- **功能说明**：获取系统核心监控指标
- **响应参数**：SystemMetrics

SystemMetrics 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | `normal` / `warning` / `error` |
| statusText | string | 状态文本 |
| healthScore | number | 健康评分 |
| todayQaCount | number | 今日问答数 |
| yesterdayQaCount | number | 昨日问答数 |
| avgResponseTime | number | 平均响应时间(ms) |
| yesterdayAvgResponseTime | number | 昨日平均响应时间 |
| llmCallCount | number | LLM调用次数 |
| yesterdayLlmCallCount | number | 昨日LLM调用次数 |
| estimatedCost | number | 预估成本 |
| yesterdayEstimatedCost | number | 昨日预估成本 |

### 11.2 获取系统状态

- **接口地址**：`GET /api/system/status`
- **功能说明**：获取各服务运行状态
- **响应参数**：SystemStatus[]

SystemStatus 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 服务名称 |
| status | string | `online` / `warning` / `offline` |
| message | string | 状态说明 |

### 11.3 获取质量趋势

- **接口地址**：`GET /api/system/quality-trend`
- **功能说明**：获取检索质量趋势
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | number | 否 | 查询天数，默认30 |

- **响应参数**：QualityTrendItem[]

QualityTrendItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期 |
| precision | number | 精确率 |
| recall | number | 召回率 |

### 11.4 获取评分分布

- **接口地址**：`GET /api/system/score-distribution`
- **功能说明**：获取检索结果评分分布
- **响应参数**：ScoreDistributionItem[]

ScoreDistributionItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| range | string | 分数区间 |
| faithfulness | number | 忠实度得分 |
| relevance | number | 相关度得分 |

### 11.5 获取错误日志

- **接口地址**：`GET /api/system/error-logs`
- **功能说明**：获取系统错误日志
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |
| level | string | 否 | 级别筛选 `info` / `warning` / `error` / `critical` |
| status | string | 否 | 状态筛选 `pending` / `processing` / `resolved` / `ignored` |
| startTime | string | 否 | 开始时间 |
| endTime | string | 否 | 结束时间 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | SystemErrorLog[] | 错误日志列表 |
| total | number | 总条数 |

SystemErrorLog 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 日志ID |
| time | string | 发生时间 |
| service | string | 服务名称 |
| serviceName | string | 服务中文名 |
| level | string | `info` / `warning` / `error` / `critical` |
| message | string | 错误信息 |
| status | string | `pending` / `processing` / `resolved` / `ignored` |
| reason | string | 原因（可选） |
| suggestion | string | 建议（可选） |
| traceId | string | 追踪ID（可选） |

### 11.6 更新错误日志状态

- **接口地址**：`PATCH /api/system/error-logs/{id}/status`
- **功能说明**：更新错误日志处理状态
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 是 | `pending` / `processing` / `resolved` / `ignored` |
| reason | string | 否 | 处理原因 |

### 11.7 获取LLM调用统计

- **接口地址**：`GET /api/system/llm-stats`
- **功能说明**：获取LLM模型调用统计
- **响应参数**：LlmCallStats[]

LlmCallStats 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| model | string | 模型名称 |
| count | number | 调用次数 |
| token | number | Token消耗 |
| cost | number | 成本 |
| percentage | number | 占比 |
| isLocal | boolean | 是否本地部署 |

### 11.8 获取队列任务状态

- **接口地址**：`GET /api/system/queue-tasks`
- **功能说明**：获取队列任务状态
- **响应参数**：QueueTaskStatus[]

QueueTaskStatus 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| queue | string | 队列标识 |
| queueName | string | 队列名称 |
| pending | number | 待处理数 |
| processing | number | 处理中数 |
| completed | number | 已完成数 |
| failed | number | 失败数 |
| status | string | `normal` / `busy` / `blocked` |

---

## 十二、成本上限管理模块

### 12.1 获取成本预算配置

- **接口地址**：`GET /api/cost/budget-config`
- **功能说明**：获取月度预算配置
- **响应参数**：CostBudgetConfig

CostBudgetConfig 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| monthlyBudget | number | 月度总预算 |
| budgetCycle | string | `natural` / `custom` |
| usedAmount | number | 已使用金额 |
| usedPercent | number | 使用率百分比 |
| remainingAmount | number | 剩余金额 |
| monthlyCallCount | number | 本月调用次数 |
| monthlyTokenUsage | number | 本月Token使用量 |
| lastMonthCost | number | 上月成本 |
| lastMonthCallCount | number | 上月调用次数 |
| lastMonthTokenUsage | number | 上月Token使用量 |

### 12.2 获取用户限制配置

- **接口地址**：`GET /api/cost/user-limit-config`
- **功能说明**：获取单用户限制配置
- **响应参数**：UserLimitConfig

UserLimitConfig 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| monthlyCallLimit | number | 月度调用次数上限 |
| monthlyTokenLimit | number | 月度Token上限 |
| singleQaTokenLimit | number | 单次问答Token上限 |
| highConsumptionThreshold | number | 高消费阈值 |
| allowOveruseApplication | boolean | 是否允许超限申请 |

### 12.3 获取超限策略配置

- **接口地址**：`GET /api/cost/over-limit-strategy`
- **功能说明**：获取超限处理策略
- **响应参数**：OverLimitStrategy[]

OverLimitStrategy 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| strategy | string | `circuit_breaker` / `degradation` / `notification` / `approval` |
| enabled | boolean | 是否启用 |
| threshold | number | 触发阈值 |

### 12.4 获取预警阈值配置

- **接口地址**：`GET /api/cost/warning-threshold`
- **功能说明**：获取预警阈值
- **响应参数**：WarningThreshold

WarningThreshold 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| yellowWarning | number | 黄色预警阈值（如70） |
| redWarning | number | 红色预警阈值（如90） |
| overLimit | number | 超限阈值（如100） |

### 12.5 保存成本配置

- **接口地址**：`PUT /api/cost/config`
- **功能说明**：保存成本相关配置
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| budgetConfig | CostBudgetConfig | 是 | 预算配置 |
| userLimitConfig | UserLimitConfig | 是 | 用户限制 |
| overLimitStrategy | OverLimitStrategy[] | 是 | 超限策略 |
| warningThreshold | WarningThreshold | 是 | 预警阈值 |

### 12.6 重置成本配置

- **接口地址**：`POST /api/cost/config/reset`
- **功能说明**：重置为默认配置
- **响应示例**：

```json
{
  "code": 200,
  "message": "重置成功",
  "data": null
}
```

### 12.7 获取成本趋势数据

- **接口地址**：`GET /api/cost/trend`
- **功能说明**：获取成本趋势数据
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | number | 否 | 天数，默认30 |

- **响应参数**：CostTrendItem[]

CostTrendItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期 |
| cost | number | 成本金额 |
| callCount | number | 调用次数 |

### 12.8 获取模型成本分布

- **接口地址**：`GET /api/cost/model-distribution`
- **功能说明**：获取各模型成本分布
- **响应参数**：ModelCostDistribution[]

ModelCostDistribution 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| model | string | 模型名称 |
| cost | number | 成本 |
| callCount | number | 调用次数 |
| isLocal | boolean | 是否本地部署 |

### 12.9 获取成本标签列表

- **接口地址**：`GET /api/cost/tags`
- **功能说明**：获取成本分配标签
- **响应参数**：CostTag[]

CostTag 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 标签ID |
| name | string | 标签名称 |
| type | string | `department` / `project` |
| monthlyCost | number | 本月成本 |
| percentage | number | 占比 |
| owner | string | 负责人 |

### 12.10 保存成本标签

- **接口地址**：`PUT /api/cost/tags`
- **功能说明**：保存成本标签
- **请求参数**：CostTag

### 12.11 删除成本标签

- **接口地址**：`DELETE /api/cost/tags/{id}`
- **功能说明**：删除成本标签

### 12.12 获取预警记录

- **接口地址**：`GET /api/cost/alerts`
- **功能说明**：获取预警记录
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |
| level | string | 否 | 级别筛选 `yellow` / `red` / `overlimit` |
| status | string | 否 | 状态筛选 `pending` / `processed` / `ignored` |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | AlertRecord[] | 预警记录列表 |
| total | number | 总条数 |

AlertRecord 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 记录ID |
| triggerTime | string | 触发时间 |
| level | string | `yellow` / `red` / `overlimit` |
| target | string | `global` / `user` / `department` |
| targetName | string | 目标名称 |
| usageRate | number | 使用率 |
| notifyMethod | string | `inapp` / `email` |
| status | string | `pending` / `processed` / `ignored` |
| detail | string | 详情（可选） |

### 12.13 标记预警已处理

- **接口地址**：`PATCH /api/cost/alerts/{id}/process`
- **功能说明**：标记预警记录为已处理
- **响应示例**：

```json
{
  "code": 200,
  "message": "标记成功",
  "data": null
}
```

---

## 十三、敏感文档策略模块

### 13.1 获取敏感级别列表

- **接口地址**：`GET /api/sensitive/levels`
- **功能说明**：获取敏感级别定义
- **响应参数**：SensitiveLevel[]

SensitiveLevel 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 级别ID |
| name | string | 级别名称：公开/内部/保密/机密 |
| color | string | 颜色标识 |
| description | string | 说明 |
| exampleKeywords | string[] | 示例关键词 |
| controlPolicy | string | 管控策略 |
| status | string | `enabled` / `disabled` |

### 13.2 保存敏感级别

- **接口地址**：`PUT /api/sensitive/levels`
- **功能说明**：保存敏感级别配置
- **请求参数**：SensitiveLevel[]

### 13.3 获取敏感关键词列表

- **接口地址**：`GET /api/sensitive/keywords`
- **功能说明**：获取敏感关键词库
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |
| keyword | string | 否 | 搜索关键词 |
| category | string | 否 | 类别筛选 |
| matchType | string | 否 | 匹配方式筛选 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | SensitiveKeyword[] | 关键词列表 |
| total | number | 总条数 |

SensitiveKeyword 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 关键词ID |
| word | string | 关键词 |
| category | string | 类别 |
| matchType | string | `exact` / `fuzzy` / `regex` |
| status | string | `enabled` / `disabled` |
| updateTime | string | 更新时间 |

### 13.4 保存敏感关键词

- **接口地址**：`PUT /api/sensitive/keywords`
- **功能说明**：保存敏感关键词
- **请求参数**：SensitiveKeyword

### 13.5 删除敏感关键词

- **接口地址**：`DELETE /api/sensitive/keywords/{id}`
- **功能说明**：删除敏感关键词

### 13.6 获取自动识别配置

- **接口地址**：`GET /api/sensitive/auto-identify-config`
- **功能说明**：获取自动分类识别配置
- **响应参数**：AutoIdentifyConfig

AutoIdentifyConfig 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | boolean | 是否启用 |
| methods | string[] | 识别方式：`keyword` / `regex` / `semantic` / `manual` |
| confidenceThreshold | number | 置信度阈值 |
| processType | string | `auto_mark` / `manual_review` / `reject` |
| rules | Rule[] | 分类规则 |

### 13.7 保存自动识别配置

- **接口地址**：`PUT /api/sensitive/auto-identify-config`
- **功能说明**：保存自动识别配置
- **请求参数**：AutoIdentifyConfig

### 13.8 获取访问控制矩阵

- **接口地址**：`GET /api/sensitive/access-control`
- **功能说明**：获取文档访问控制矩阵
- **响应参数**：AccessControlItem[]

AccessControlItem 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| levelId | string | 敏感级别ID |
| levelName | string | 敏感级别名称 |
| role | string | 用户角色 |
| permissions | string[] | 权限：`view` / `qa` / `manage` / `approve` / `none` |

### 13.9 保存访问控制项

- **接口地址**：`PUT /api/sensitive/access-control`
- **功能说明**：保存访问控制配置
- **请求参数**：AccessControlItem

### 13.10 获取脱敏规则列表

- **接口地址**：`GET /api/sensitive/desensitize-rules`
- **功能说明**：获取脱敏规则列表
- **响应参数**：DesensitizationRule[]

DesensitizationRule 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 规则ID |
| name | string | 规则名称 |
| type | string | `regex` |
| pattern | string | 正则表达式 |
| replacement | string | 替换方式 |
| example | string | 示例 |
| description | string | 描述 |
| status | string | `enabled` / `disabled` |

### 13.11 保存脱敏规则

- **接口地址**：`PUT /api/sensitive/desensitize-rules`
- **功能说明**：保存脱敏规则
- **请求参数**：DesensitizationRule

### 13.12 删除脱敏规则

- **接口地址**：`DELETE /api/sensitive/desensitize-rules/{id}`
- **功能说明**：删除脱敏规则

### 13.13 切换脱敏规则状态

- **接口地址**：`PATCH /api/sensitive/desensitize-rules/{id}/toggle`
- **功能说明**：启用/停用脱敏规则

### 13.14 执行脱敏测试

- **接口地址**：`POST /api/sensitive/desensitize-test`
- **功能说明**：测试文本脱敏效果
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| text | string | 是 | 待脱敏文本 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| original | string | 原文 |
| result | string | 脱敏结果 |
| hits | Hit[] | 命中规则列表 |

Hit 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| ruleId | string | 规则ID |
| ruleName | string | 规则名称 |
| matchedText | string | 命中文本 |
| replacedText | string | 替换后文本 |

### 13.15 获取敏感审计日志

- **接口地址**：`GET /api/sensitive/audit-logs`
- **功能说明**：获取敏感操作审计日志
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页条数 |

- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| list | SensitiveAuditLog[] | 日志列表 |
| total | number | 总条数 |

SensitiveAuditLog 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 日志ID |
| timestamp | string | 操作时间 |
| operator | string | 操作人 |
| action | string | 操作类型 |
| target | string | 操作对象 |
| detail | string | 详情 |
| ip | string | IP地址 |
| status | string | `pending` / `processed` / `ignored` |

### 13.16 保存所有敏感策略配置

- **接口地址**：`PUT /api/sensitive/policies/all`
- **功能说明**：批量保存所有敏感策略配置
- **请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| levels | SensitiveLevel[] | 是 | 敏感级别 |
| keywords | SensitiveKeyword[] | 是 | 关键词 |
| autoIdentify | AutoIdentifyConfig | 是 | 自动识别配置 |
| accessControl | AccessControlItem[] | 是 | 访问控制 |
| desensitizeRules | DesensitizationRule[] | 是 | 脱敏规则 |

### 13.17 获取敏感统计

- **接口地址**：`GET /api/sensitive/stats`
- **功能说明**：获取敏感策略统计数据
- **响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| levelCount | number | 敏感级别数 |
| keywordCount | number | 关键词数 |
| ruleCount | number | 规则数 |
| monthlyAccessCount | number | 本月访问次数 |

---

## 十四、系统配置模块

### 14.1 获取系统配置

- **接口地址**：`GET /api/system/config`
- **功能说明**：获取系统全局配置
- **响应参数**：SystemConfig

SystemConfig 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| siteName | string | 站点名称 |
| logo | string | Logo URL |
| copyright | string | 版权信息 |
| enableRegister | boolean | 是否开放注册 |
| enableFeedback | boolean | 是否启用反馈 |
| maxUploadSize | number | 最大上传大小（MB） |
| allowedFileTypes | string[] | 允许的文件类型 |

### 14.2 保存系统配置

- **接口地址**：`PUT /api/system/config`
- **功能说明**：保存系统全局配置
- **请求参数**：SystemConfig

---

## 附录A：数据类型定义汇总

### A.1 用户相关

```typescript
interface UserInfo {
  id: string
  username: string
  phone: string
  email?: string
  emailVerified?: boolean
  realName: string
  avatar: string
  role: 'employee' | 'manager' | 'leader' | 'admin'
  roleName: string
  department: string
  departmentId: string
  roles: string[]
  permissions: string[]
}
```

### A.2 模型相关

```typescript
interface ModelConfig {
  id: string
  name: string
  modelIdentifier: string
  modelType: 'cloud' | 'local'
  apiUrl: string
  apiKey?: string
  enabled: boolean
  isDefault: boolean
  temperature: number
  maxTokens: number
  maxOutputTokens: number
  contextWindow: string
  description?: string
  tags: string[]
  sortOrder: number
}
```

### A.3 对话相关

```typescript
interface Message {
  id: string
  conversationId: string
  type: 'user' | 'bot'
  content: string
  timestamp: number
  model?: string
  citations?: Citation[]
  reasoning?: RagReasoning[]
}

interface Citation {
  id: string
  messageId: string
  sourceId: string
  sourceName: string
  sourceType: 'document' | 'attachment'
  content: string
  similarity: number
  pageNumber?: number
}

interface RagReasoning {
  step: number
  type: 'retrieve' | 'rewrite' | 'generate' | 'reflect' | 'summarize'
  description: string
  timestamp: number
  detail?: string
}
```

### A.4 成本相关

```typescript
interface CostBudgetConfig {
  monthlyBudget: number
  budgetCycle: 'natural' | 'custom'
  usedAmount: number
  usedPercent: number
  remainingAmount: number
  monthlyCallCount: number
  monthlyTokenUsage: number
  lastMonthCost: number
  lastMonthCallCount: number
  lastMonthTokenUsage: number
}

interface AlertRecord {
  id: string
  triggerTime: string
  level: 'yellow' | 'red' | 'overlimit'
  target: 'global' | 'user' | 'department'
  targetName: string
  usageRate: number
  notifyMethod: 'inapp' | 'email'
  status: 'pending' | 'processed' | 'ignored'
  detail?: string
}
```

### A.5 敏感策略相关

```typescript
interface SensitiveLevel {
  id: string
  name: string
  color: string
  description: string
  exampleKeywords: string[]
  controlPolicy: string
  status: string
}

interface DesensitizationRule {
  id: string
  name: string
  type: string
  pattern: string
  replacement: string
  example: string
  description: string
  status: string
}
```

---

## 附录B：前端与后端对接注意事项

### B.1 接口路径映射

前端当前使用 `src/api/mockApi.ts` 中的函数名，对接后端时需要：

1. 将 `mockApi.ts` 中的函数改为真实的 `axios` 请求
2. 保持函数签名不变（参数和返回值类型一致）
3. 前端调用方式无需修改

### B.2 认证机制

1. 登录成功后后端返回 `token` 和 `expiresAt`
2. 前端将 `token` 存入 `localStorage`
3. 后续请求在 `Authorization` 头中携带：`Bearer {token}`
4. Token 过期时返回 401，前端自动跳转登录页

### B.3 部门统一

系统中统一使用以下 6 个业务部门：

| 部门ID | 部门名称 |
|--------|----------|
| tech | 技术研发部 |
| product | 产品运营部 |
| hr | 人力资源部 |
| marketing | 市场营销部 |
| sales | 销售部 |
| finance | 财务部 |

### B.4 角色统一

| 角色Key | 角色名称 |
|---------|----------|
| employee | 普通员工 |
| manager | 部门经理 |
| leader | 高层领导 |
| admin | 系统管理员 |

### B.5 SSE流式响应

智能问答接口 `/api/qa/stream` 使用 Server-Sent Events 格式：

```
Content-Type: text/event-stream

event: message
data: {"type": "content", "content": "..."}

event: citation
data: {"sources": [...]}

event: reasoning
data: {"steps": [...]}

event: done
data: {"messageId": "...", "totalTokens": 256}
```

### B.6 文件上传

文件上传接口 `/api/knowledge/upload` 使用 `multipart/form-data`：

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

[文件二进制内容]
------WebKitFormBoundary--
```

---

> 文档结束。如有疑问或需要调整，请联系前端开发同学确认数据结构和字段要求。
