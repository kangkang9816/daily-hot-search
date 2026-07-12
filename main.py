"""
每日热搜早报 — 主入口

支持两种运行模式：
1. 命令行模式：直接运行 python main.py，自动使用 Playwright 抓取并输出报告
2. 模块模式：作为 Hermes Agent cron 任务的 skill 加载执行

使用方式：
    python main.py                     # 抓取所有平台并输出报告
    python main.py --platform baidu    # 只抓取百度
    python main.py --format json       # JSON 格式输出

依赖环境：需要 Hermes Agent 内置浏览器工具（browser_navigate, browser_console 等）
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from reporter import build_report


def fetch_baidu() -> str:
    """获取百度热搜 Top 10（通过浏览器提取）"""
    return "（需要 Hermes Agent 浏览器环境执行）"


def fetch_weibo() -> str:
    """获取微博热搜 Top 10
    
    注意：m.weibo.cn API 已全面失效（HTTP 432 访客验证）
    改用 weibo.com/newlogin 网页版公开页面提取
    """
    return "（需要 Hermes Agent 浏览器环境执行）"


def fetch_xueqiu() -> str:
    """获取雪球热股榜（通过浏览器提取）"""
    return "（需要 Hermes Agent 浏览器环境执行）"


def fetch_stocks() -> str:
    """获取A股行情数据（通过新浪财经 API）"""
    return "（需要 Hermes Agent 环境执行）"


def fetch_margin_trading() -> str:
    """获取融资融券数据（通过东方财富数据中心 API）"""
    return "（需要 Hermes Agent 环境执行）"


def main():
    parser = argparse.ArgumentParser(description="每日热搜早报 — Daily Hot Search")
    parser.add_argument("--platform", choices=["baidu", "weibo", "xueqiu", "stocks", "all"],
                       default="all", help="抓取平台")
    parser.add_argument("--format", choices=["markdown", "json", "text"],
                       default="markdown", help="输出格式")
    parser.add_argument("--no-push", action="store_true", help="不推送，仅输出")
    args = parser.parse_args()

    print("📡 Daily Hot Search — 每日热搜早报")
    print("   请使用 Hermes Agent 的 cronjob 或 Playwright 浏览器环境运行本程序。")
    print(f"   详情请参考 README.md\n")
    
    report = build_report()
    print(report)


if __name__ == "__main__":
    main()
