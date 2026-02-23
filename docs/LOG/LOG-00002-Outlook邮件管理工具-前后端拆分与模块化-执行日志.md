# 执行日志：Outlook邮件管理工具-前后端拆分与模块化（00002）

- 日期：2026-02-23
- 目的：按 `docs/TODO/Outlook邮件管理工具-前后端拆分与模块化TODO.md` 推进“前后端拆分与模块化”，确保 **URL/响应契约/错误结构/trace_id/调度器行为** 不回归，并在每阶段提供可回滚点与可验证证据（测试/文档）。

---

## 2026-02-23

### 启动记录

- 本轮开始依据的目标文档：`docs/TODO/Outlook邮件管理工具-前后端拆分与模块化TODO.md`
- 约束：不引入前端构建链；后端仍为 Flask；数据库仍为 SQLite；行为兼容优先。

### 阶段 0：基线冻结（门禁）

- 决策：先补齐“接口契约抽样验收口径 + smoke tests”，作为后续拆分的门禁；后续每次大拆分都必须通过该门禁再继续推进。

#### 产出

- 接口契约抽样验收口径文档：
  - `docs/QA/前后端拆分-接口契约抽样验收口径.md`
- Smoke/契约抽样单测：
  - `tests/test_smoke_contract.py`

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（34/34）。

### 阶段 0（补充）：回滚点与静态资源 Smoke 覆盖

- 补充：将门禁项的“回滚点/静态资源可访问”也纳入可验证资产，并同步在 TODO 勾选完成状态。

#### 产出

- 回滚点与切换方式文档：
  - `docs/RUN/00002-前后端拆分-回滚点与切换方式.md`
- 最小静态资源基线：
  - `static/health.txt`
- Smoke/契约抽样单测增强：
  - `tests/test_smoke_contract.py`（新增页面可访问与静态资源可访问检查）

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（36/36）。

### 阶段 4（完成）：Routes 模块化（Blueprint 化，URL 不变）

- 决策：采用“Blueprint 仅做 URL->view_func 映射，view_func 复用 legacy 实现”的迁移方式，优先保证接口契约不回归；所有 blueprint 注册集中到 `create_app()`，并修复兼容入口被 `import *` 覆盖 `app` 的问题，确保部署入口 `web_outlook_app:app` 真正暴露装配后的 factory app。

#### 产出

- Blueprint 路由模块（按领域拆分）：  
  - `outlook_web/routes/pages.py`（/ /login /logout /api/csrf-token）  
  - `outlook_web/routes/groups.py`、`outlook_web/routes/tags.py`、`outlook_web/routes/accounts.py`、`outlook_web/routes/emails.py`  
  - `outlook_web/routes/temp_emails.py`、`outlook_web/routes/oauth.py`、`outlook_web/routes/settings.py`  
  - `outlook_web/routes/scheduler.py`、`outlook_web/routes/system.py`、`outlook_web/routes/audit.py`
- 统一注册路由（集中在工厂内注册 blueprint，URL 不变）：  
  - `outlook_web/app.py`
- 入口修复（避免 `from outlook_web.legacy import *` 覆盖 factory app）：  
  - `web_outlook_app.py`（使用 `_factory_app` 并在 import * 后恢复 `app` 绑定）
- 重定向端点对齐（Blueprint 化后登录端点为 `pages.login`）：  
  - `outlook_web/security/auth.py`、`outlook_web/legacy.py`

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（37/37）。

### 阶段 6（完成）：文档与维护指南（面向开发者）

- 决策：把“入口保持不变 + 内部模块化结构 + 新增 API 的推荐路径”文档化，避免后续继续拆分时出现认知偏差；同时同步回归清单/验收映射对入口的描述，明确 `web_outlook_app.py` 为兼容 facade、真实装配入口为 `create_app()`。

#### 产出

- README 补充模块结构与新增 API 指南：
  - `README.md`
- 开发者指南（模块边界/依赖方向/测试运行/常见坑）：
  - `docs/DEV/00002-前后端拆分-开发者指南.md`
- 更新回归清单与验收映射的入口说明：
  - `docs/QA/回归验证清单.md`
  - `docs/QA/P0验收对照表.md`
- 回滚点文档与实现对齐（阶段 5 描述修正为外链 CSS/JS，零构建）：
  - `docs/RUN/00002-前后端拆分-回滚点与切换方式.md`

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（37/37）。

### 阶段 5（完成）：前端静态资源拆分（零构建）

- 决策：不引入任何前端构建链，先把 `templates/index.html` 的内联 CSS/JS 迁出到 `static/css` 与 `static/js`；JS 拆分以“按 feature 分文件 + 仍保持全局函数供内联 onclick 调用”的方式推进，避免一次性改为 ESModule 导致全量重写与行为回归风险。

#### 产出

- CSS 迁出：
  - `static/css/main.css`
  - `templates/index.html` 引入 `css/main.css`（Jinja `url_for('static', ...)`）
- JS 迁出与拆分：
  - `static/js/main.js`（保留全局状态、CSRF、初始化与部分通用逻辑）
  - `static/js/features/groups.js`、`static/js/features/accounts.js`、`static/js/features/emails.js`、`static/js/features/temp_emails.js`
  - `templates/index.html` 增加对上述脚本的顺序加载（保持行为不变）
- Smoke/契约单测增强（静态资源与“无内联 style/script”门禁）：
  - `tests/test_smoke_contract.py`

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（37/37）。

### 阶段 3（完成）：拆 repositories（SQL）与 services（业务编排）

- 决策：采用“先抽模块 + legacy re-export 接入”的方式推进，优先保证 URL/响应契约/trace_id/错误结构不回归；在关键链路（删除回退、刷新编排）先补边界单测再继续拆 routes。

#### 产出

- repositories（SQL 与数据映射）：
  - `outlook_web/repositories/accounts.py`（账号读写、批量 tags 聚合与敏感字段解密）
  - `outlook_web/repositories/groups.py`（分组 CRUD、默认分组与账号迁移）
  - `outlook_web/repositories/tags.py`（标签 CRUD、账号标签关联）
  - `outlook_web/repositories/temp_emails.py`（临时邮箱与邮件落库查询）
  - `outlook_web/repositories/settings.py`（settings 读取/写入、默认值兜底）
  - `outlook_web/repositories/distributed_locks.py`、`outlook_web/repositories/refresh_runs.py`、`outlook_web/repositories/refresh_logs.py`（刷新相关表操作）
- services（Graph/IMAP/GPTMail/刷新/删除回退）：
  - `outlook_web/services/graph.py`、`outlook_web/services/imap.py`、`outlook_web/services/http.py`
  - `outlook_web/services/gptmail.py`
  - `outlook_web/services/email_delete.py`（删除回退聚合与摘要）
  - `outlook_web/services/refresh.py`（刷新编排：manual_all/scheduled_manual 流式 + retry_failed）
- legacy 接入（兼容旧调用点）：
  - `outlook_web/legacy.py` 通过 re-export 覆盖原同名函数，使 routes 默认走 repositories/services 实现
  - `/api/emails/delete` 迁移为调用 `outlook_web/services/email_delete.py`（Graph 优先、IMAP 回退与错误聚合保持一致）
  - `/api/accounts/refresh-all`、`/api/accounts/trigger-scheduled-refresh` 迁移为调用 `outlook_web/services/refresh.py`（SSE 输出结构不变）

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（37/37）。
- 新增边界单测：ProxyError 场景不回退 IMAP（`tests/test_error_and_trace.py`）。
- 备注：Python 3.13 下静态文件响应会触发 `ResourceWarning`，已在测试中对响应显式 `close()` 消除告警。

### 阶段 1：后端骨架 + 入口兼容（create_app）

- 决策：先落地 `create_app()` 与后端包结构，保持 `web_outlook_app:app` 启动入口不变；同时把 init_db/调度器启动从模块 import-time 副作用迁移到 `create_app()` 受控执行。

#### 产出

- 后端包与应用工厂：
  - `outlook_web/app.py`（`create_app()`）
  - `outlook_web/__init__.py`
- 单体实现迁移（迁移期 legacy）：
  - `outlook_web/legacy.py`（原 `web_outlook_app.py` 迁入；移除 `init_app()` 与调度器的 import-time 自动执行点）
- 入口兼容 facade：
  - `web_outlook_app.py`（`app = create_app(...)`，并暴露 `impl` 便于测试打补丁）
- 单测兼容调整：
  - 将 `patch.object(self.module, ...)` 改为 `patch.object(self.module.impl, ...)`，确保对 legacy 逻辑打补丁生效

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（36/36）。

### 阶段 2（完成）：基础设施模块化 - 配置/安全/DB/审计

- 决策：在不改变接口契约的前提下，先把“配置/安全/DB/审计”等基础能力抽到独立模块；legacy 仅保留兼容导出与路由绑定，降低后续拆 routes/services/repositories 的耦合风险。

#### 产出

- 配置集中化：
  - `outlook_web/config.py`（环境变量读取与默认值集中）
  - `outlook_web/legacy.py` 将调度器 autostart 相关读取改为 `config.get_scheduler_autostart_default()`
- 安全模块化：
  - `outlook_web/security/crypto.py`（密码哈希 + 敏感数据加密解密）
  - `outlook_web/security/auth.py`（鉴权装饰器 + 速率限制 + 导出二次验证 token）
  - `outlook_web/security/csrf.py`（可选 CSRF：存在依赖则启用，否则显式禁用）
- DB 模块化：
  - `outlook_web/db.py`（连接管理、`init_db()`、schema 版本/迁移记录、敏感字段加密迁移）
  - `outlook_web/legacy.py` 通过 re-export 兼容旧调用点（迁移期保留函数名，真实实现位于 `outlook_web/db.py`）
- 审计模块化：
  - `outlook_web/audit.py`（`log_audit` 与审计查询 `query_audit_logs`）
  - `/api/audit-logs` 改为调用 `query_audit_logs`（响应结构保持一致）

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（36/36）。

### 阶段 2（完成）：基础设施模块化 - 错误模型集中化

- 决策：优先抽离“错误结构/脱敏/trace_id 生成”的公共能力，降低后续 routes/services/repositories 迁移时的耦合与重复。

#### 产出

- 错误模型模块：
  - `outlook_web/errors.py`（`generate_trace_id/sanitize_error_details/build_error_payload`）
- legacy 迁移：
  - `outlook_web/legacy.py` 改为统一引用 `outlook_web/errors.py`（保持对外错误结构与脱敏行为一致）

#### 验证

- 本地执行：`python -m unittest discover -s tests -v` 通过（36/36）。
