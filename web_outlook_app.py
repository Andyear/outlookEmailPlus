#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outlook 邮件 Web 应用（兼容入口）

目标：
- 保持部署入口兼容：`web_outlook_app:app`
- 内部实现逐步迁移到 `outlook_web/`（后续将继续模块化/Blueprint 化）

关联文档：
- PRD：docs/PRD/Outlook邮件管理工具-前后端拆分与模块化PRD.md
- FD：docs/FD/Outlook邮件管理工具-前后端拆分与模块化FD.md
- TDD：docs/TDD/Outlook邮件管理工具-前后端拆分与模块化TDD.md
- DEV：docs/DEV/00002-前后端拆分-开发者指南.md
"""

import os

from outlook_web import legacy as impl
from outlook_web.app import create_app

# 在脚本运行场景（__main__）中，调度器由 main block 统一控制，
# 避免 debug reloader 父进程误启后台线程。
app = create_app(autostart_scheduler=None if __name__ != "__main__" else False)


__all__ = ["app", "impl"]


def __getattr__(name: str):
    """
    迁移期兼容：将历史上从 `web_outlook_app` 直接访问的符号代理到 legacy 实现。

    - 避免 `from outlook_web.legacy import *` 造成命名污染/覆盖（例如覆盖 `app`）。
    - 保持 `from web_outlook_app import some_function` 的兼容性（PEP 562）。
    """
    return getattr(impl, name)


def __dir__():
    return sorted(set(globals().keys()) | set(dir(impl)))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_ENV", "production") != "production"

    print("=" * 60)
    print("Outlook 邮件 Web 应用")
    print("=" * 60)
    print(f"访问地址: http://{host}:{port}")
    print(f"运行模式: {'开发' if debug else '生产'}")
    print("=" * 60)

    # 初始化定时任务（与旧版行为保持一致）
    if not debug or os.getenv("WERKZEUG_RUN_MAIN") == "true":
        impl.init_scheduler()
    else:
        print("✓ 调试重载器父进程：跳过启动调度器")

    app.run(debug=debug, host=host, port=port)
