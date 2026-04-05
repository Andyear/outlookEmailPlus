# Changelog

All notable changes to OutlookMail Plus are documented in this file.

## [v1.12.0] - 2026-04-05

### 新功能 / New Features

- **PRD-00011 Telegram 代理支持**：Telegram 通知现在支持通过系统级 HTTP/SOCKS5 代理发送，可在设置页「通知」Tab 配置代理地址，并支持一键测试代理连通性（内联显示延迟 ms 或错误原因）
- **PRD-00011 IMAP Token 代理透传**：`get_emails_imap_with_server`、`get_email_detail_imap`、`get_imap_new_access_token`、`search_emails_imap_server` 等 IMAP 相关 Token 获取请求现已支持透传分组代理（`proxy_url`），覆盖 emails、external_api 全部调用路径
- **设置页 Tab 化 UI 重构**：设置页面拆分为 4 个 Tab（通知、轮询、系统、临时邮箱），引入 `card-shell` 视觉外壳，临时邮箱 Provider 配置独立分离，界面更清晰

### 修复 / Bug Fixes

- **Bug #28**：修复 `release` 后账号依旧不可用的问题：`release` 时同步清理 `account_project_usage` 记录
- **emails.py detail 代理透传遗漏**：补充 `get_email_detail_imap` 和 `extract_verification` 中遗漏的 `proxy_url` 参数透传
- **安全修复**：移除测试文件中硬编码的真实代理凭据，改为 `TEST_PROXY_URLS` 环境变量注入，外网直连测试默认 skip（需 `ENABLE_PROXY_LIVE_TEST=1`）

### 重要变更

- 新增 settings K-V 存储键：`telegram_proxy_url`，用于 Telegram 代理配置（无需 DB Schema 迁移，settings 表自动兼容）
- 新增 API 接口：`POST /api/settings/test-telegram-proxy`，传入 `{"proxy_url": "..."}` 测试代理连通性，返回 `{success, latency_ms?, error?}`
- 版本号从 `1.10.2` 提升到 `1.12.0`

### 测试/验证

- 自动化测试（核心）：`python -m unittest tests.test_module_boundaries tests.test_error_and_trace tests.test_prd00011_proxy_live -v`
  - 模块边界测试：3/3 通过
  - PRD-00011 集成测试：7/7 通过（1 skipped，需 `ENABLE_PROXY_LIVE_TEST=1` 才运行外网测试）
- 历史测试基准：failures=144, errors=433（与 v1.11.0 基准完全一致，本次改动无回归）
- 代理连通性验证：本机 Clash Verge（127.0.0.1:7890）实测 Telegram 代理测试按钮返回 ✅（2544ms）；Graph Token 刷新通过代理成功（951ms）

---



### 新功能 / New Features

- **邮箱池项目隔离（PR#27）**：在 `claim-random` 时支持传入 `project_key`，同一 `caller_id + project_key` 下已使用的账号不会被重复领取（DB 迁移 v17）
- **CF Worker 临时邮箱多域支持**：可在设置页配置多个 CF Worker 域名；新增"同步域名"按钮，支持前端一键刷新域名列表
- **CF Worker Admin Key 加密存储**：`cf_worker_admin_key` 现在以 `enc:` 前缀加密写入数据库，不再以明文存储（DB 迁移 v18）
- **账号列表前端分页**：每页展示 50 条账号，大量账号时滚动加载更流畅
- **统一轮询引擎**：将标准模式与简洁模式的双轮询系统合并为单一 `poll-engine`（4 阶段重构），消除轮询竞争与状态积压

### 修复 / Bug Fixes

- **BUG-06**：生成或删除临时邮箱后，列表中已选中的邮箱状态得到正确保留，不再因刷新而丢失选中高亮
- **BUG-07**：临时邮箱面板在刷新邮件列表后，域名下拉选择不再被意外重置回默认值
- **Issue #24**：修复邮件展开/激活状态在列表重渲染后丢失、i18n 语言切换后账号列表不刷新、视口高度链路断裂、缺失翻译词条等问题
- **轮询 BUG**：修复页面初始加载时触发的批量邮件拉取、分组切换重复启动轮询、跨视图切换时轮询状态积压等问题
- **Graph API 401 静默回退**：修复 token 轮换时 Graph API 401 被静默吞掉导致的 token 丢失问题

### i18n

- 临时邮箱面板域名提示文字（`domain_hint_xxx`）新增中英双语翻译
- CF Worker 域名同步按钮 (`sync_cf_domains`)、提示文字 (`cf_domain_hint`) 新增双语支持
- 补充设置页与轮询指示器等处的缺失翻译词条

### CI / 代码质量修复

- 修复 `pool.py` 中存在的重复函数定义（`release`、`complete`、`expire_stale_claims`、`recover_cooldown`、`get_stats`）
- 修复 `pool.py` `get_stats()` 后的死代码（`return` 之后的不可达 `claim` 函数体）
- 修复 `RESULT_TO_POOL_STATUS` 中 `"success"` 映射：由旧的 `"cooldown"` 改为正确的 `"used"`
- 修复 `get_stats()` 的 `pool_counts` 字典，补充缺失的 `"used": 0` 键
- 修复 `pool.py` `claim_atomic()` 中 black 格式化问题（`cutoff`、`lease_expires_at_str` 多行表达式）
- 在 `external_api.py` 中添加 `# noqa: E203`、`# noqa: C901` 压制 flake8 误报
- 对齐 `test_pool.py` 和 `test_pool_flow_suite.py` 中的测试断言，统一期望 `success` 完成后状态为 `"used"`
- 全量 `black --line-length 127` 与 `isort --profile black` 格式化

---

## [v1.10.0] - 2026-03-26

- OAuth 回归修复与认证后工作区重构

## [v1.9.2] - 2026-03-24

- 小版本修复

## [v1.9.0] - 2026-03-20

- 双语界面、统一通知分发与演示站点保护

## [v1.7.0] - 2026-03-15

- 第二次发布：README 交付口径补全

## [v1.6.1] - 2026-03-15

- 发布质量闸门清理与发布内容精简
