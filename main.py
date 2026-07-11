"""
每日热搜早报 — 主入口

支持两种运行模式：
1. 命令行模式：直接运行 python main.py，自动使用 Playwright 抓取并输出报告
2. 模块模式：作为 Hermes Agent cron 任务的 skill 加载执行

使用方式：
    python main.py                     # 抓取所有平台并输出报告
    python main.py --platform baidu    # 只抓取百度
    python main.py --format json       # JSON 格式输出
"""

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from reporter import build_report


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


if __name__ == "__main__":
    main()
