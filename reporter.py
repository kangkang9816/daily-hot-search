"""
每日热搜早报 — 报告格式化模块

将所有数据合并成一个美观的 Markdown 报告。
"""

from datetime import datetime


def build_report(
    date_str: str = None,
    weekday_str: str = None,
    multi_platform_text: str = "",
    stocks_text: str = "",
    margin_text: str = "",
) -> str:
    """
    构建完整的每日热搜早报报告。

    参数可传入各模块预格式化的文本块，直接拼接。
    """
    now = datetime.now()
    if not date_str:
        date_str = now.strftime("%Y年%m月%d日")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        weekday_str = weekdays[now.weekday()]

    parts = [
        f"🔥 **每日热搜早报 · {date_str}（周{weekday_str}）**",
        "",
        f"📡 聚合 11 个主流平台热搜 + A股行情",
        "",
    ]

    # 多平台热搜总览
    if multi_platform_text:
        parts.append(multi_platform_text)
        parts.append("")

    # A股行情
    if stocks_text:
        parts.append(stocks_text)
    if margin_text:
        parts.append(margin_text)

    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append(f"🕐 报告时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    parts.append("")
    parts.append("---")
    parts.append("*💡 数据来源：newsnow API（微博/百度/知乎/抖音/B站/头条/澎湃/凤凰网/贴吧/华尔街见闻/财联社）+ 东方财富 | 由 Daily Hot Search v4.0 自动生成*")

    return "\n".join(parts)
