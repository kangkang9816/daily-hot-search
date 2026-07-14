"""
每日热搜早报 — 主入口 v4.0.0

数据源全面升级：使用 newsnow API 替代原先的浏览器抓取模式。
- 11+ 主流平台热搜数据（统一 API，稳定可靠）
- A股行情 + 融资融券（新浪财经 + 东方财富，保持不变）

使用方式：
    python main.py                          # 抓取所有平台并推送
    python main.py --no-push                # 不推送，仅输出报告
    python main.py --platforms 3            # 只抓取前3个平台测试
    python main.py --include-extra          # 包含 GitHub/V2EX/豆瓣/虎扑

依赖：Python 3.12+, urllib（标准库），无需浏览器、无需 Docker
"""

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from newsnow_fetcher import (
    fetch_all_platforms,
    format_platform_section,
    DEFAULT_PLATFORMS,
    EXTRA_PLATFORMS,
)
from reporter import build_report


def fetch_stocks() -> str:
    """获取A股行情数据（通过新浪财经 API）"""
    from stocks import parse_sina_result, format_stocks

    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10",
             "-H", "Referer: https://finance.sina.com.cn/",
             "https://hq.sinajs.cn/list=sh000001,sz399001"],
            capture_output=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            # 新浪返回 GBK 编码，需要转码
            text = result.stdout.decode("gbk", errors="replace")
            data = parse_sina_result(text)
            return format_stocks(data)
    except Exception:
        pass
    return (
        "━━━━━━━━━━━━━━━━━━━\n"
        "📊 A股市场概况\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "❌ 行情获取失败"
    )


def fetch_margin_trading() -> str:
    """获取融资融券数据（通过东方财富数据中心 API）"""
    from stocks import parse_margin_result, format_margin

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
            data = parse_margin_result(result.stdout)
            return format_margin(data)
    except Exception:
        pass
    return (
        "\n━━━━━━━━━━━━━━━━━━━\n"
        "📊 融资融券概况\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "❌ 融资融券获取失败"
    )


def main():
    parser = argparse.ArgumentParser(description="每日热搜早报 — Daily Hot Search v4.0")
    parser.add_argument("--no-push", action="store_true", help="不推送，仅输出")
    parser.add_argument("--platforms", type=int, default=None,
                        help="只抓取前N个平台（用于快速测试）")
    parser.add_argument("--include-extra", action="store_true",
                        help="包含额外平台（GitHub/V2EX/豆瓣/虎扑）")
    parser.add_argument("--format", choices=["markdown", "json"],
                        default="markdown", help="输出格式")
    args = parser.parse_args()

    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]

    print(f"🔥 每日热搜早报 · 开始抓取...")
    print(f"📡 时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 抓取多平台热搜
    platforms = DEFAULT_PLATFORMS.copy()
    if args.platforms:
        platforms = platforms[:args.platforms]
    if args.include_extra:
        platforms.extend(EXTRA_PLATFORMS)

    print(f"📊 正在抓取 {len(platforms)} 个平台热搜...")
    results = fetch_all_platforms(platforms)

    # 输出抓取状态
    success_count = sum(1 for v in results.values() if v["success"])
    fail_count = len(platforms) - success_count
    for pid, data in results.items():
        status = "✅" if data["success"] else "❌"
        count = len(data["items"]) if data["success"] else 0
        print(f"  {status} {data['name']}: {count}条")
    print(f"  成功: {success_count}/{len(platforms)}")

    multi_platform_text = format_platform_section(results, platforms)

    # 2. 抓取 A 股行情
    print(f"\n📈 正在抓取 A 股行情...")
    stocks_text = fetch_stocks()
    print(f"  ✅ A股行情获取完成")

    # 3. 抓取融资融券
    print(f"📊 正在抓取融资融券...")
    margin_text = fetch_margin_trading()
    print(f"  ✅ 融资融券获取完成")

    # 4. 构建报告（新版三板块格式）
    report = build_report(
        date_str=now.strftime("%Y年%m月%d日"),
        weekday_str=weekdays[now.weekday()],
        results=results,
        stocks_text=stocks_text,
        margin_text=margin_text,
    )

    if args.format == "json":
        # JSON 输出
        json_output = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": weekdays[now.weekday()],
            "platforms": {
                pid: {
                    "name": data["name"],
                    "success": data["success"],
                    "count": data["total"],
                    "items": data["items"],
                }
                for pid, data in results.items()
            },
            "stocks": stocks_text,
            "margin": margin_text,
            "report_markdown": report,
        }
        print("=" * 60)
        print(json.dumps(json_output, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print(report)

    # 5. 保存报告到本地
    output_dir = "/opt/data/cron/output"
    os.makedirs(output_dir, exist_ok=True)
    today_str = now.strftime("%Y%m%d")
    report_path = os.path.join(output_dir, f"daily-hot-search-{today_str}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n📄 报告已保存: {report_path}")

    return report


if __name__ == "__main__":
    report = main()
    # 如果命令行直接运行，输出报告到 stdout
    if "--no-push" not in sys.argv:
        print("\n" + "=" * 60)
        print("💡 提示: 用 -h 查看参数选项")
