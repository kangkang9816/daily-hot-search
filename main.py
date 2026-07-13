"""
每日热搜早报 — 主入口

支持两种运行模式：
1. CLI 模式：直接运行 python main.py（需要在有 Playwright 浏览器的环境下）
2. 模块模式：作为 Hermes Agent cron 任务的 skill 加载执行

使用方式：
    python main.py                          # 抓取所有平台并输出报告
    python main.py --platform baidu         # 只抓取百度
    python main.py --format json            # JSON 格式输出
    python main.py --no-push                # 不推送，仅输出

依赖环境（CLI 模式）：Playwright 浏览器、curl、网络访问外部 API
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from reporter import build_report


def fetch_baidu() -> str:
    """获取百度热搜 Top 10（需要 Hermes Agent 浏览器环境执行）"""
    return "（需要 Hermes Agent 浏览器环境执行）"


def fetch_weibo() -> str:
    """获取微博热搜 Top 10（需要 Hermes Agent 浏览器环境执行）"""
    return "（需要 Hermes Agent 浏览器环境执行）"


def fetch_xueqiu() -> str:
    """获取雪球热股榜（需要 Hermes Agent 浏览器环境执行）"""
    return "（需要 Hermes Agent 浏览器环境执行）"


def fetch_stocks() -> str:
    """获取A股行情数据（通过新浪财经 API / curl）"""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10",
             "-H", "Referer: https://finance.sina.com.cn/",
             "https://hq.sinajs.cn/list=sh000001,sz399001"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            from stocks import parse_sina_result, format_stocks
            data = parse_sina_result(result.stdout)
            return format_stocks(data)
    except Exception:
        pass
    return "（A股行情获取失败）"


def fetch_margin_trading() -> str:
    """获取融资融券数据（通过东方财富数据中心 API / curl）"""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10",
             "-H", "Referer: https://data.eastmoney.com/rzrq/total.html",
             "https://datacenter-web.eastmoney.com/api/data/v1/get"
             "?reportName=RPTA_RZRQ_LSHJ&columns=ALL"
             "&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=DIM_DATE&source=WEB"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            from stocks import parse_margin_result, format_margin
            data = parse_margin_result(result.stdout)
            return format_margin(data)
    except Exception:
        pass
    return "\n（融资融券获取失败）"


def main():
    parser = argparse.ArgumentParser(description="每日热搜早报 — Daily Hot Search")
    parser.add_argument("--platform", choices=["baidu", "weibo", "xueqiu", "stocks", "all"],
                        default="all", help="抓取平台")
    parser.add_argument("--format", choices=["markdown", "json", "text"],
                        default="markdown", help="输出格式")
    parser.add_argument("--no-push", action="store_true", help="不推送，仅输出")
    args = parser.parse_args()

    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    
    report = build_report(
        date_str=now.strftime("%Y年%m月%d日"),
        weekday_str=weekdays[now.weekday()],
    )
    print(report)


if __name__ == "__main__":
    main()
