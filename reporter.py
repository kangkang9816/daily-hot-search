"""
每日热搜早报 — 报告格式化模块

将各平台数据合并成一个美观的 Markdown 报告。
"""

from datetime import datetime


def build_report(
    date_str: str = None,
    weekday_str: str = None,
    baidu_text: str = "",
    weibo_text: str = "",
    xueqiu_text: str = "",
    stocks_text: str = "",
    margin_text: str = "",
) -> str:
    if not date_str:
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        weekday_str = weekdays[now.weekday()]

    parts = [
        f"🔥 **每日热搜早报 · {date_str}（周{weekday_str}）**",
        "",
    ]

    if baidu_text:
        parts.append(baidu_text)
        parts.append("")
    if weibo_text:
        parts.append(weibo_text)
        parts.append("")
    if xueqiu_text:
        parts.append(xueqiu_text)
        parts.append("")
    if stocks_text:
        parts.append(stocks_text)
    if margin_text:
        parts.append(margin_text)

    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append(f"📡 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    parts.append("")
    parts.append("---")
    parts.append("*💡 数据来源：百度热搜、微博热搜、雪球、东方财富 | 由 Daily Hot Search 自动生成*")

    return "\n".join(parts)
