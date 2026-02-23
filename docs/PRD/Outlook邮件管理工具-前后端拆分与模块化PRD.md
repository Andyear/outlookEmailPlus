# Outlook 邮件管理工具｜前后端拆分与模块化 PRD（仅需求）

- 文档状态：草案
- 版本：V0.1
- 日期：2026-02-23
- 负责人：待定
- 格式参考：`docs/PRD/Outlook邮件管理工具-重构升级PRD.md`
- 对齐 FD：`docs/FD/Outlook邮件管理工具-前后端拆分与模块化FD.md`
- 对齐 TDD：`docs/TDD/Outlook邮件管理工具-前后端拆分与模块化TDD.md`
- 对齐 TODO：`docs/TODO/Outlook邮件管理工具-前后端拆分与模块化TODO.md`

---

## 1. 背景与现状

当前工程已具备完整业务能力，但前后端代码主要集中在少数大文件中：

- 后端：`web_outlook_app.py` 约 5,071 行，包含配置/安全/DB/Graph/IMAP/GPTMail/路由/调度器/错误处理等多类职责。
- 前端：`templates/index.html` 约 5,166 行，包含大量内联脚本（UI 逻辑 + API 调用 + 业务流程）。

随着功能持续迭代，单文件体量与职责混杂带来明显的工程风险：

- **可维护性**：定位代码成本高，改动影响面大，容易误伤其它链路。
- **可测试性**：难以对“业务逻辑/数据访问/外部服务调用/HTTP 路由”进行分层隔离与 Mock。
- **协作成本**：多人改动同一大文件冲突多，review 难度高。
- **发布风险**：缺乏清晰模块边界，重构难以做到“小步可回滚”。

因此需要在**不改变对外功能与行为**的前提下，将前后端进行模块化拆分，为后续维护与扩展提供稳定结构。

---

## 2. 目标（What）

### 2.1 业务目标

> 本 PRD 的“业务目标”面向工程交付：提升迭代效率与质量，而不新增/改变现有业务功能。

- **降低维护成本**：把高内聚逻辑拆分到清晰的模块目录与文件中，减少“改一处影响一片”的情况。
- **降低回归风险**：使重构可以小步进行，每一步都有单测与验收证据支撑。
- **提升可测试性**：让关键逻辑可以在不启动完整 Web 服务、不过度依赖外部网络的前提下被测试覆盖。
- **为后续演进铺路**：后端路由/服务/存储/外部集成边界明确；前端 API 层与 UI 层职责清晰。

### 2.2 成功指标（可验收）

- 后端入口文件只保留应用装配与启动逻辑（例如 app factory / WSGI 入口），核心业务不再集中在单文件。
- 前端 `index.html` 不再承载大段内联脚本：JS/CSS 迁移到 `static/` 并按模块拆分。
- API 路径、请求/响应结构、错误结构与现有行为保持一致（对用户“无感”）。
- `python -m unittest discover -s tests -v` 全部通过，并可在 CI 中稳定运行。

---

## 3. 范围与非目标

### 3.1 本次范围

#### 后端（Flask）

- 将 `web_outlook_app.py` 按职责拆分为多个模块（建议分层：Presentation/Service/Repository/Infrastructure）。
- 路由改为 Blueprint 或等价的路由模块化组织方式（保持原有 URL 不变）。
- 抽离可复用的工具与基础设施模块（加密、错误结构、审计、调度器、DB 连接等）。
- 保持现有数据库结构与迁移策略不变（本次只做代码组织与依赖边界整理）。

#### 前端（Jinja + 原生 JS）

- 将 `templates/index.html` 的脚本按职责拆分到 `static/js/`（建议 ES module，无需引入构建链）。
- 将样式拆分到 `static/css/`（如现有样式大量内联，可先拆出主样式，再逐步细分）。
- 将模板中可复用块拆为 Jinja include（例如：模态框/侧栏/表格区域），提升可读性与局部修改效率。

#### 文档与测试

- 补充“目录结构说明/模块边界说明/开发者贡献指南”。
- 增补针对新模块边界的测试（至少覆盖：app 装配、蓝图注册、核心 service 的纯逻辑测试）。

### 3.2 非目标（本次不做）

- 不引入新的前端框架（React/Vue）或打包构建体系（Webpack/Vite）。保持“零构建/轻依赖”优先。
- 不改变现有业务功能与交互（除非是明确的 bug 修复且有回归用例）。
- 不进行数据库大迁移/大重写（以现有 SQLite + 迁移策略为准）。

---

## 4. 用户与场景

### 4.1 用户画像

- **维护者/开发者**
  - 需要快速定位某个功能点对应的后端/前端代码位置
  - 需要在不理解整个 5k+ 行文件的情况下安全地做小改动
  - 需要更容易写单测/集成测试来防回归

### 4.2 关键使用场景（User Stories）

- 作为维护者，我希望修改某个 API 的校验/错误提示时，只需要改动 route + service 的有限范围，而不影响调度器/其它业务。
- 作为维护者，我希望新增一个“只读”查询接口时，有固定位置放 route/SQL/序列化逻辑，避免散落。
- 作为维护者，我希望调整某个前端弹窗的交互时，只需要改动对应的 UI 模块文件，而不需要在超大 HTML 中查找与回归全局脚本。

---

## 5. 功能需求（工程交付要求）

> 说明：这里定义“拆分后必须满足的能力与约束”，以确保重构不改变现有产品行为。

### 5.1 行为兼容性（必须）

- 所有现有 API 的路径、方法、参数语义保持不变。
- 统一错误结构、`trace_id` 透传、默认脱敏等行为保持不变。
- 登录/CSRF/会话机制保持不变。
- 定时刷新/调度器自启动策略保持不变（仅移动代码位置，不改变默认行为）。

### 5.2 后端模块边界（建议目标结构）

建议以包结构承载模块（示例命名，可在 FD 中最终确定）：

```
outlook_web/
  app.py                 # create_app / 装配
  config.py              # 环境变量与配置
  db.py                  # 连接管理、init_db、迁移
  errors.py              # error payload、全局异常处理、脱敏
  security/
    crypto.py            # SECRET_KEY 派生、encrypt/decrypt、hash
    auth.py              # login_required、会话工具
    csrf.py              # CSRF 集成与降级策略
  audit.py               # log_audit 与审计查询
  scheduler/
    scheduler.py         # APScheduler 初始化/配置/心跳
    locks.py             # distributed_locks 抽象
    runs.py              # refresh_runs 记录与查询
  services/
    graph.py             # Graph API 访问与错误聚合
    imap.py              # IMAP（新/旧）访问与错误聚合
    gptmail.py           # 临时邮箱第三方交互（可 mock）
  repositories/
    accounts.py          # accounts/tags/group 数据访问（SQL）
    groups.py
    tags.py
    temp_emails.py
  routes/
    groups.py            # Blueprint: /api/groups...
    accounts.py
    tags.py
    emails.py
    temp_emails.py
    oauth.py
    settings.py
    system.py
```

要求：

- route 层只做：参数解析/鉴权/调用 service/统一返回。
- service 层做：业务编排/回退策略/错误聚合/审计触发。
- repository 层做：SQL 与数据映射（尽量不引入业务规则）。

### 5.3 前端模块边界（建议目标结构）

建议把 `index.html` 中的脚本拆为：

```
static/
  js/
    main.js              # 入口：初始化、路由绑定、全局事件
    api.js               # fetch 封装、统一错误处理、trace_id 展示
    state.js             # 前端状态（当前组/当前账号/分页/缓存）
    ui/
      modal.js           # 通用弹窗
      toast.js           # 通知/提示
    features/
      groups.js
      accounts.js
      tags.js
      emails.js
      refresh.js
      export.js
      settings.js
      audit.js
      temp_emails.js
  css/
    main.css
templates/
  index.html             # 仅保留结构与容器，脚本改为引用 static/js/main.js
  partials/              # 逐步抽离可复用模板块（可选）
```

要求：

- API 调用集中在 `api.js`，避免散落重复。
- UI 组件（modal/toast）与业务 feature 分离，减少跨域依赖。

### 5.4 渐进式迁移（必须）

- 拆分必须支持“阶段性交付”：每个阶段都可运行、可回归、可回滚。
- 允许短期“兼容层”存在（例如旧函数在新模块中 re-export），但需要明确淘汰计划。

---

## 6. 非功能需求

### 6.1 可靠性与可回滚

- 任何一次拆分阶段都必须保持可运行（至少能通过现有单测与基础验收接口）。
- 需要提供拆分阶段的回滚策略（例如保留旧入口文件，或提供快速切换开关/分支）。

### 6.2 性能

- 拆分不能引入明显性能退化（主要是导入时间/启动时间/关键接口耗时）。
- 静态资源拆分后应支持浏览器缓存（相比内联脚本更易缓存）。

### 6.3 安全

- 不引入新的敏感信息暴露路径（尤其是静态 JS 不得包含任何密钥/令牌）。
- 保持现有脱敏策略与审计策略。

---

## 7. 交付物与验收清单

### 7.1 交付物

- 新的目录结构与模块拆分后的代码。
- 开发者文档：
  - 目录结构说明
  - 模块边界与依赖约束
  - 如何新增/修改一个 API 的推荐路径
- 单测与 CI：保证拆分后仍可一键运行测试。

### 7.2 验收清单（核心）

- 现有回归清单可按原路径执行：`docs/QA/回归验证清单.md`
- 单测通过：`python -m unittest discover -s tests -v`
- 核心接口契约不变（抽样验收即可）：
  - `/healthz`
  - `/api/system/health`
  - `/api/scheduler/status`
  - `/api/system/upgrade-status`
  - `/api/accounts` `/api/groups` `/api/tags` 等核心管理接口

---

## 8. 实施建议（阶段/里程碑）

> 说明：本节为工程实施建议，用于确保“可回滚的小步重构”，不强制但强烈推荐按阶段推进。

### 8.1 后端拆分顺序（低风险优先）

1) **骨架与兼容层**
   - 新增 `outlook_web/app.py`（`create_app()`），并让旧入口仍可 `from outlook_web.app import app` 或保持 `web_outlook_app.py` 作为兼容 facade
2) **基础设施先拆（最容易单测）**
   - `config.py` / `security/crypto.py` / `errors.py` / `db.py`
3) **数据访问层拆分**
   - `repositories/*`：把 SQL 与 dict 映射集中
4) **服务层拆分**
   - `services/*`：Graph/IMAP/GPTMail、回退聚合、审计触发
5) **路由层拆分**
   - `routes/*`：Blueprint 化（URL 不变），最后再移除旧路由定义
6) **调度器拆分**
   - `scheduler/*`：锁、运行记录、job 装配统一管理

### 8.2 前端拆分顺序（无构建优先）

1) 先把内联脚本整体迁移到 `static/js/main.js`（保持功能一致）
2) 再逐步按 feature 拆分到 `static/js/features/*`
3) 最后再做模板 partials（降低大文件冲突）

---

## 附录 A：现有单文件章节 → 建议模块映射（草案）

> 依据 `web_outlook_app.py` 的章节标识（`# ==================== ... ====================`）拟定迁移去向。

- 配置 → `outlook_web/config.py`
- 登录速率限制 / 登录验证 / 请求上下文工具 → `outlook_web/security/auth.py`
- 密码安全工具 / 数据加密工具 → `outlook_web/security/crypto.py`
- 错误处理工具 / 错误处理 → `outlook_web/errors.py`
- 数据库操作 / 应用初始化 / 设置操作 / 导出二次验证 Token（持久化）→ `outlook_web/db.py` + `outlook_web/audit.py` + `outlook_web/security/*`
- 分组/账号/标签（DB 操作）→ `outlook_web/repositories/groups.py`、`outlook_web/repositories/accounts.py`、`outlook_web/repositories/tags.py`
- Graph API / IMAP 方式 → `outlook_web/services/graph.py`、`outlook_web/services/imap.py`
- 邮件 API / 删除 helpers → `outlook_web/routes/emails.py` + `outlook_web/services/*`
- 临时邮箱（GPTMail）→ `outlook_web/services/gptmail.py`、`outlook_web/repositories/temp_emails.py`、`outlook_web/routes/temp_emails.py`
- OAuth Token API → `outlook_web/routes/oauth.py`
- 设置 API / 系统 API → `outlook_web/routes/settings.py`、`outlook_web/routes/system.py`
- 定时任务调度器 → `outlook_web/scheduler/*`
