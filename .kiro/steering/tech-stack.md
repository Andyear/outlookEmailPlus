# 技术栈详解

## 后端技术

### Web 框架
- **Flask 3.0+**
  - 轻量级 WSGI Web 框架
  - 灵活的扩展系统
  - 应用工厂模式支持
  - Blueprint 模块化

### 数据库
- **SQLite**
  - 轻量级嵌入式数据库
  - 无需独立服务器
  - 支持 WAL 模式 (并发优化)
  - 适合中小规模应用

### 安全库
- **Flask-WTF 1.2+**
  - CSRF 保护
  - 表单验证
  - 文件上传处理

- **bcrypt 4.0+**
  - 密码哈希算法
  - 自适应成本因子
  - 防止彩虹表攻击

- **cryptography 41.0+**
  - Fernet 对称加密
  - 密钥派生 (PBKDF2)
  - Token 加密存储

### HTTP 客户端
- **requests[socks] 2.25+**
  - HTTP/HTTPS 请求
  - SOCKS5 代理支持
  - 会话管理
  - 连接池

### 定时任务
- **APScheduler 3.10+**
  - 后台任务调度
  - Cron 表达式支持
  - 持久化任务状态
  - 多种触发器 (interval/cron/date)

- **croniter 1.3+**
  - Cron 表达式解析
  - 下次执行时间计算

### WSGI 服务器
- **Werkzeug 3.0+**
  - Flask 底层 WSGI 工具库
  - 开发服务器
  - 调试工具
  - 中间件支持

## 前端技术

### 基础技术
- **HTML5**
  - 语义化标签
  - 表单验证

- **CSS3**
  - Flexbox 布局
  - 响应式设计
  - 动画效果

- **JavaScript (ES6+)**
  - 异步请求 (Fetch API)
  - 事件处理
  - DOM 操作

### 第三方库
- **jQuery 3.x**
  - DOM 操作简化
  - AJAX 请求
  - 事件处理

- **DOMPurify**
  - HTML 净化
  - XSS 防护
  - 白名单过滤

### UI 组件
- 自定义 CSS 样式
- 四栏式布局
- 响应式设计

## 外部 API

### Microsoft Graph API
- **用途**: 主要邮件访问方式
- **认证**: OAuth2
- **功能**:
  - 获取邮件列表
  - 获取邮件详情
  - 删除邮件
  - 刷新 Token

### IMAP 协议
- **用途**: 备用邮件访问方式
- **服务器**:
  - 新版: `outlook.live.com:993`
  - 旧版: `outlook.office365.com:993`
- **认证**: 邮箱密码
- **功能**:
  - 获取邮件列表
  - 获取邮件详情

### GPTMail API
- **用途**: 临时邮箱服务
- **功能**:
  - 生成临时邮箱
  - 获取临时邮件

## 开发工具

### 包管理
- **pip**
  - Python 包管理器
  - requirements.txt 依赖管理

### 测试框架
- **pytest**
  - 单元测试
  - 集成测试
  - 覆盖率报告

### 代码质量
- **类型注解**
  - `from __future__ import annotations`
  - 类型提示

### 版本控制
- **Git**
  - 分支管理
  - 提交规范

## 部署技术

### 容器化
- **Docker**
  - 容器化部署
  - 环境隔离
  - 快速部署

### Web 服务器
- **Nginx** (推荐)
  - 反向代理
  - 静态文件服务
  - HTTPS 配置

### WSGI 服务器
- **Gunicorn** (推荐)
  - 多进程模式
  - 性能优化
  - 平滑重启

- **uWSGI** (备选)
  - 高性能
  - 多协议支持

## 数据库设计

### 表结构

#### accounts (邮箱账号)
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT,
    refresh_token TEXT,
    group_id INTEGER,
    status TEXT,
    remark TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

#### groups (分组)
```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT,
    proxy_type TEXT,
    proxy_host TEXT,
    proxy_port INTEGER,
    created_at TIMESTAMP
)
```

#### tags (标签)
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP
)
```

#### account_tags (账号标签关联)
```sql
CREATE TABLE account_tags (
    account_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (account_id, tag_id)
)
```

#### settings (系统设置)
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
)
```

#### refresh_logs (刷新日志)
```sql
CREATE TABLE refresh_logs (
    id INTEGER PRIMARY KEY,
    run_id TEXT,
    account_id INTEGER,
    status TEXT,
    error_message TEXT,
    created_at TIMESTAMP
)
```

#### refresh_runs (刷新运行记录)
```sql
CREATE TABLE refresh_runs (
    id TEXT PRIMARY KEY,
    total_count INTEGER,
    success_count INTEGER,
    failed_count INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
)
```

#### distributed_locks (分布式锁)
```sql
CREATE TABLE distributed_locks (
    lock_name TEXT PRIMARY KEY,
    owner TEXT,
    acquired_at TIMESTAMP,
    expires_at TIMESTAMP
)
```

#### temp_emails (临时邮箱)
```sql
CREATE TABLE temp_emails (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    created_at TIMESTAMP
)
```

## 性能优化

### 数据库优化
- 索引优化 (email, group_id, status)
- 连接池管理
- WAL 模式 (并发优化)
- 分布式锁 (避免竞态条件)

### 缓存策略
- 前端邮件列表缓存
- Token 数据库持久化
- 静态资源缓存

### 并发处理
- Flask g 对象 (请求级单例)
- APScheduler 后台调度
- 分布式锁机制

## 安全技术

### 认证授权
- 会话管理 (Flask Session)
- 密码哈希 (bcrypt)
- OAuth2 授权流程

### 数据保护
- Fernet 对称加密
- 密钥派生 (PBKDF2)
- HTTPS 传输加密

### 攻击防护
- XSS 防护 (DOMPurify + 输出转义)
- CSRF 防护 (Flask-WTF)
- SQL 注入防护 (参数化查询)
- 登录限流 (速率限制)

### 审计追踪
- 操作日志记录
- trace_id 追踪
- 敏感操作审计

## 监控与日志

### 日志系统
- Python logging 模块
- 分级日志 (DEBUG/INFO/WARNING/ERROR)
- 文件日志轮转

### 错误追踪
- 统一 trace_id
- 错误详情记录
- 审计日志

### 性能监控
- 请求响应时间
- 数据库查询性能
- 定时任务执行状态

## 扩展性

### 水平扩展
- 无状态设计
- 数据库可迁移 (PostgreSQL/MySQL)
- 负载均衡支持

### 垂直扩展
- 模块化设计
- Blueprint 独立部署
- 服务层可抽取为微服务

### 未来技术栈
- 前后端分离 (Vue.js/React)
- RESTful API
- PostgreSQL/MySQL
- Redis 缓存
- Celery 异步任务
- Docker Compose 编排
