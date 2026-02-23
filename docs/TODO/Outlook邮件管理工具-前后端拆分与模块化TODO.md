# Outlook 邮件管理工具｜前后端拆分与模块化 TODO（待办清单，仅说明要完成什么）

- 文档状态：草案
- 版本：V0.1
- 日期：2026-02-23
- 对齐 PRD：`docs/PRD/Outlook邮件管理工具-前后端拆分与模块化PRD.md`
- 对齐 FD：`docs/FD/Outlook邮件管理工具-前后端拆分与模块化FD.md`
- 对齐 TDD：`docs/TDD/Outlook邮件管理工具-前后端拆分与模块化TDD.md`

---

## P0（必须完成）

### 0) 文档与基线准备（拆分前门禁）

- [x] PRD/FD/TDD 已产出并互相对齐
- [x] 明确“接口契约不变”的抽样验收口径（关键接口清单 + 预期结构）：`docs/QA/前后端拆分-接口契约抽样验收口径.md`
- [x] 增加“拆分阶段 smoke tests”（应用装配/关键路由/静态资源可访问）：`tests/test_smoke_contract.py`
- [x] 明确每阶段回滚点（保留旧入口/兼容层/切换方式）：`docs/RUN/00002-前后端拆分-回滚点与切换方式.md`

### 1) 后端骨架 + 入口兼容（create_app）

- [x] 新增后端包结构（例如 `outlook_web/`）并提供 `create_app()`：`outlook_web/app.py`
- [x] 保持部署入口兼容：Gunicorn/Docker 仍可用 `web_outlook_app:app`：`web_outlook_app.py`
- [x] 控制 import-time 副作用：禁止在 import 时启动调度器/线程（迁移到 `create_app()` 受控启动）：`outlook_web/legacy.py`
- [x] 拆分后单测仍可跑（`python -m unittest discover -s tests -v`）通过（36/36）

### 2) 拆基础设施模块（低风险优先）

- [x] 配置集中化：环境变量读取与默认值集中管理（`outlook_web/config.py`）
- [x] 错误模型集中化：统一错误结构/trace_id/默认脱敏/全局异常处理保持一致：`outlook_web/errors.py`
- [x] 安全模块化：加密/鉴权/CSRF 分离，行为保持一致（`outlook_web/security/*`）
- [x] DB 模块化：连接管理 + `init_db()`/迁移逻辑集中，行为保持一致（`outlook_web/db.py`）
- [x] 审计模块化：`log_audit` 与审计查询入口保持一致（`outlook_web/audit.py`）

### 3) 拆 repositories（SQL）与 services（业务编排）

- [x] repositories：accounts/groups/tags/temp_emails 等 SQL 与数据映射集中（`outlook_web/repositories/*`）
- [x] services：Graph/IMAP/GPTMail/刷新编排/删除回退聚合等逻辑集中（`outlook_web/services/*`）
- [x] 多方式回退聚合错误结构保持一致（前端展示不回归）（`outlook_web/services/email_delete.py`）
- [x] 为 service/repository 补充单元测试（优先覆盖回退聚合/脱敏/边界条件）（`tests/test_error_and_trace.py`）

### 4) Routes 模块化（Blueprint 化，URL 不变）

- [x] 按领域拆路由模块：system/scheduler/groups/accounts/tags/emails/oauth/settings/temp_emails
- [x] 统一注册路由（create_app 内集中 register blueprint）
- [x] URL/方法/响应结构不变（以抽样契约测试与回归清单验证）

### 5) 前端静态资源拆分（零构建）

- [x] 新增 `static/js` 与 `static/css` 目录
- [x] `templates/index.html` 脚本整体迁出到 `static/js/main.js`（行为不变）
- [x] JS 再逐步按 feature 拆分（api/state/ui/features/*）
- [x] CSS 至少拆出主样式文件（避免模板内联堆叠）
- [x] 前端关键路径抽样回归（登录/分组/账号/刷新/删除/导出/审计/临时邮箱/设置）

### 6) 文档与维护指南（面向开发者）

- [x] README 增加“目录结构/模块职责/如何新增 API”说明
- [x] 增加或更新开发者文档：模块边界、依赖方向、测试运行方式
- [x] 更新回归清单与验收映射中涉及的入口说明（若存在兼容层则说明迁移路径）

---

## P1（强烈建议完成）

### 7) 清理兼容层与技术债

- [ ] 移除不再需要的旧入口/旧函数 re-export（确保无外部依赖后再删）
- [x] 替换 `from outlook_web.legacy import *` 为 `__getattr__` 代理（避免命名污染/覆盖 `app`）
- [ ] 收敛跨模块全局变量（逐步减少 `window.*` 与隐式依赖）
- [x] 为模块依赖加门禁（避免 routes/repo 循环依赖再次出现）（`tests/test_module_boundaries.py`）

### 8) 模板与 UI 结构进一步瘦身

- [x] 把 `templates/index.html` 按区域拆为 Jinja partials（降低冲突、提升可读性）（`templates/partials/*`）
- [ ] 通用 UI（modal/toast）标准化，减少 feature 之间复制粘贴
