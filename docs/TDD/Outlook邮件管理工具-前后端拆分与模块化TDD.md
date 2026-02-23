# Outlook 邮件管理工具｜前后端拆分与模块化 TDD（技术设计细节）

- 文档状态：草案
- 版本：V0.1
- 日期：2026-02-23
- 对齐 PRD：`docs/PRD/Outlook邮件管理工具-前后端拆分与模块化PRD.md`
- 对齐 FD：`docs/FD/Outlook邮件管理工具-前后端拆分与模块化FD.md`
- 对齐 TODO：`docs/TODO/Outlook邮件管理工具-前后端拆分与模块化TODO.md`
- 关联 CR：`docs/CR/CR-00002-Outlook邮件管理工具-前后端拆分与模块化-文档审查报告.md`

---

## 1. 文档目的

本 TDD 用于描述“为满足 PRD/FD，前后端拆分与模块化需要采用的技术设计细节”。  
重点回答：

- 拆成哪些模块、各模块职责边界是什么、依赖方向如何约束
- 如何保证 **URL/响应契约/错误结构/trace_id/调度器行为** 不回归
- 如何渐进式迁移（每阶段可回滚、可验收、可测试）

---

## 2. 设计原则与硬约束（必须满足）

### 2.1 行为兼容性（对用户无感）

- 保持现有 API 路径/方法/参数语义/响应结构不变。
- 保持统一错误结构、`trace_id` 透传、默认脱敏策略不变。
- 保持登录/会话/CSRF 行为不变。
- 保持定时刷新“推荐运行方式/自启动策略/可验证证据接口”不变。

### 2.2 渐进式拆分（可回滚、可验证）

- 任何阶段都必须可运行且可回归：至少通过 `python -m unittest discover -s tests -v` 与关键接口抽样验收。
- 允许短期存在兼容层（旧入口 facade / re-export），但每阶段要有明确的“可删除点”。

### 2.3 不引入新复杂度

- 前端不引入 React/Vue 等框架，不引入 Webpack/Vite 等构建链；以 **ES Module + 静态资源引用** 为主。
- 后端不引入新框架迁移（仍为 Flask），数据库仍为 SQLite，迁移策略保持现状。

---

## 3. 总体架构设计

### 3.1 后端分层（建议）

采用典型分层与关注点分离：

- Presentation（Routes）：参数解析/鉴权/调用 service/返回 JSON
- Service（业务编排）：回退策略/流程编排/审计触发/错误聚合
- Repository（数据访问）：SQL 与数据映射，不承载业务规则
- Infrastructure（基础设施）：配置、DB、加密、错误模型、调度器、第三方客户端

依赖方向约束（必须遵守）：

`routes -> services -> repositories -> db`  
`routes/services` 可以依赖 `errors/security/audit/utils`，但 **repositories 不能依赖 routes**。

### 3.2 前端模块化（建议）

- `api` 层：统一 `fetch` 封装、错误结构处理、trace_id 展示、CSRF/header 处理
- `ui` 层：modal/toast/loading 等通用组件
- `features` 层：groups/accounts/tags/emails/refresh/export/settings/audit/temp_emails 等业务模块
- `state` 层：当前分组/账号/分页/缓存等前端状态（可用简单对象，避免引入状态管理框架）

---

## 4. 后端技术设计细节

### 4.1 目标目录结构（建议）

新增后端包（示例命名，可在实现阶段微调）：

```
outlook_web/
  __init__.py
  app.py                  # create_app + 装配
  config.py               # 环境变量读取/默认值/运行模式
  db.py                   # 连接管理、init_db、迁移/索引
  errors.py               # error payload、trace_id、脱敏、全局异常处理
  audit.py                # log_audit + 审计查询
  security/
    __init__.py
    crypto.py             # SECRET_KEY 派生、encrypt/decrypt、hash_password
    auth.py               # login_required、session 工具、ip 获取
    csrf.py               # CSRF 集成与降级
  repositories/
    accounts.py
    groups.py
    tags.py
    temp_emails.py
  services/
    graph.py
    imap.py
    email_delete.py        # 删除邮件回退聚合（可选单独文件）
    refresh.py             # token 刷新编排（可选）
    gptmail.py
  scheduler/
    scheduler.py           # APScheduler 初始化/装配/心跳
    locks.py               # distributed_locks 抽象
    runs.py                # refresh_runs 记录/查询
  routes/
    system.py
    scheduler.py
    groups.py
    accounts.py
    tags.py
    emails.py
    oauth.py
    settings.py
    temp_emails.py
```

约束：

- `outlook_web/app.py` 只负责装配与注册，不承载大段业务代码。
- `init_db()` 与 schema 迁移逻辑集中在 `db.py`，避免散落。

### 4.2 应用装配（create_app）与入口兼容

#### 4.2.1 目标

- 支持 `create_app()`（便于测试与复用）。
- 同时保持部署入口兼容：现有 `gunicorn ... web_outlook_app:app` 不需要立即改动。

#### 4.2.2 设计

- `outlook_web/app.py`：
  - `create_app()`：创建 Flask app、加载 config、注册 blueprint、注册 error handler、初始化 db/scheduler（按环境变量开关）。
- `web_outlook_app.py` 在迁移阶段变为 facade：
  - `from outlook_web.app import create_app`
  - `app = create_app()`
  - 继续保留必要的兼容导出（避免影响 tests/与外部启动方式）

**禁止**：在模块 import 时启动后台线程（调度器必须在 `create_app()` 内按开关启动）。

### 4.3 配置与环境变量

`outlook_web/config.py` 负责集中读取并提供类型安全的配置：

- `SECRET_KEY`（必填，且变更会影响历史加密数据）
- `DATABASE_PATH`（默认 `data/outlook_accounts.db`）
- `LOGIN_PASSWORD`（初始登录密码）
- `SCHEDULER_AUTOSTART`（是否在 WSGI 导入场景自启动调度器）
- 其它现有设置项保持原名与语义

### 4.4 错误模型、trace_id、脱敏（统一入口）

`outlook_web/errors.py`：

- `generate_trace_id()`：若请求头带 `X-Trace-Id` 则复用，否则生成。
- `build_error_payload(code, message, type, status, details)`：默认对 message/details 脱敏。
- 全局异常处理：
  - `HTTPException` → `HTTP_ERROR`
  - 未捕获异常 → `UNCAUGHT_EXCEPTION`
- `after_request`：
  - 统一补 `X-Trace-Id`
  - legacy `{success:false,error:"..."}` 归一化为结构化 error（保持现有兼容策略）

### 4.5 数据库与迁移（init_db）

`outlook_web/db.py`：

- `create_sqlite_connection()`：统一设置 row_factory、busy_timeout、foreign_keys。
- `get_db()`：基于 `flask.g` 的连接生命周期管理。
- `init_db()`：
  - 幂等建表、缺列补齐、索引创建、schema 版本写入与迁移记录（保持现有逻辑与表结构）
  - 并发迁移使用 `BEGIN IMMEDIATE`（保持一致性）

### 4.6 Repository（SQL）设计

Repository 层只做“数据访问与映射”，以函数形式即可（不强制类）：

- `repositories/accounts.py`
  - `get_account_by_id(db, account_id)` / `add_account(db, ...)` / `update_account(db, ...)` / `search_accounts(db, q)` 等
- 统一约束：
  - 不返回敏感字段明文（若业务需要解密，放在 service 层做）
  - 所有 SQL 参数化，禁止字符串拼接注入

### 4.7 Service（业务编排）设计

Service 层负责：

- Graph/IMAP/GPTMail 调用与错误聚合
- Token 刷新/删除邮件等“多方式回退策略”
- 审计触发（不记录敏感明文）

建议把“聚合错误”的结构保持与现有一致（前端依赖 `error.details` 展示）。

### 4.8 Routes（Blueprint）设计

每个路由文件暴露一个 blueprint：

- `bp = Blueprint("groups", __name__)`
- 使用 `@login_required` 等装饰器保持一致
- 注册：`app.register_blueprint(groups.bp)`（不使用 `url_prefix` 或用空前缀，确保 URL 不变）

### 4.9 调度器（Scheduler）与 import-time 副作用控制

目标：避免“import 就启动线程”，但保持既有运行方式下的定时刷新能力。

策略：

- `create_app()` 内：
  - 先 `init_db()`，再根据 `SCHEDULER_AUTOSTART`（或 TESTING 环境）决定是否 `init_scheduler()`
- 测试环境默认禁用自启动（现有 `tests/_import_app.py` 已采用环境变量方式）

---

## 5. 前端技术设计细节

### 5.1 静态资源拆分与引用

新增目录：

```
static/
  js/
  css/
```

`templates/index.html`：

- 移除大段内联脚本，改为引用：
  - `<script type="module" src="/static/js/main.js"></script>`
- CSS 迁移到 `/static/css/main.css`

### 5.2 API 封装（api.js）

提供统一方法：

- `apiGet(path, opts)` / `apiPost(path, body, opts)` / `apiDelete(...)`
- 统一处理：
  - JSON parse
  - `success=false` 的结构化 error 展示（复用现有 `handleApiError()` 语义）
  - `X-Trace-Id` 的获取与展示（用于排障复制）
  - CSRF token/header（保持现有策略）

### 5.3 Feature 模块拆分

每个 feature 文件负责：

- UI 事件绑定（按钮/表单/表格交互）
- 调用 `api.js` 与更新 `state`
- 只依赖 `ui/*` 与 `api.js/state.js`，避免 feature 互相调用导致耦合

### 5.4 渐进迁移策略（避免一次性大改）

- 第一步允许把原来所有脚本“整体搬到 main.js”以保持行为一致；
- 第二步再从 main.js 中按 feature 拆分导出函数/类；
- 第三步再考虑把 HTML 结构拆成 Jinja partials（减少冲突）。

---

## 6. 迁移阶段与验收（每阶段必做）

> 每个阶段都必须：单测通过 + 抽样接口验收通过 + 可回滚。

### 阶段 0：基线冻结

- 锁定现有接口契约与关键行为（以现有 tests + QA 文档为证据）。

### 阶段 1：后端骨架 + 兼容入口

- 引入 `outlook_web/create_app()`，`web_outlook_app.py` 变为 facade 并继续导出 `app`。
- 验收：
  - Docker/Gunicorn 启动命令不变
  - 单测全过

### 阶段 2：拆基础设施（低风险）

- 拆 `config/errors/security/crypto/db/audit`，旧文件只转发调用。
- 增补单测：错误结构/trace_id/脱敏不回归。

### 阶段 3：拆 repositories + services

- SQL 下沉 repositories，回退策略与业务编排上移 services。
- 增补单测：纯逻辑单测（不依赖 Flask app）。

### 阶段 4：拆 routes（Blueprint 化）

- 分模块路由文件并注册蓝图，URL 不变。
- 增补测试：关键路由存在性与响应结构抽样。

### 阶段 5：前端静态资源拆分

- 先整体迁移脚本到 `static/js/main.js`，再按 feature 拆分。
- 抽样回归：登录/分组/账号/导出/审计/临时邮箱/设置等关键路径。

---

## 7. 测试策略（TDD/回归保障）

### 7.1 单元测试（优先补 service/repository）

- repository：SQL 结果映射、边界条件（空/不存在/重复）
- service：回退聚合、错误结构、脱敏、审计 details 生成

### 7.2 集成测试（保契约）

- 使用 Flask `test_client` 验证关键接口：
  - `/healthz`
  - `/api/system/health`
  - `/api/system/upgrade-status`
  - `/api/audit-logs`
  - `/api/scheduler/status`
- 对“拆分后的装配”增加 smoke test（蓝图是否注册、静态资源是否可访问）。

### 7.3 变更门禁

- CI 必跑：`python -m unittest discover -s tests -v`

---

## 8. 风险与缓解

- 循环依赖风险：通过分层约束与“只从上往下依赖”解决；必要时引入 `types.py` 放共享数据结构。
- import-time 副作用：调度器启动必须延迟到 `create_app()`，测试环境必须禁用自启动。
- 契约漂移：每阶段用“抽样契约测试 + QA 清单”兜底；禁止随手改接口字段名。
- 前端全局变量依赖：第一阶段允许保留 `window.*`，后续再逐步收敛成模块内部状态。

---

## 9. 交付验收（技术侧）

- FD 2.x 清单项全部满足。
- 单测与 CI 通过。
- 关键抽样接口契约不变。
- 迁移过程中每阶段的“回滚点”清晰可执行。
