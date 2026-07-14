"""
每日热搜早报 — 报告格式化模块 v4.2

恢复完整展示风格：11个平台每条热搜展示，不加筛选。
"""

from datetime import datetime


def build_report(
    date_str: str = None,
    weekday_str: str = None,
    results: dict = None,
    stocks_text: str = "",
    margin_text: str = "",
) -> str:
    """构建完整每日热搜早报"""
    now = datetime.now()
    if not date_str:
        date_str = now.strftime("%Y年%m月%d日")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        weekday_str = weekdays[now.weekday()]

    if results is None:
        results = {}

    parts = [
        f"🔥 **每日热搜早报 · {date_str}（周{weekday_str}）**",
        "",
    ]

    # ============ 11个平台热搜完整展示 ============
    platform_order = [
        "weibo", "baidu", "toutiao", "zhihu", "douyin",
        "bilibili-hot-search", "thepaper", "ifeng", "tieba",
        "wallstreetcn-hot", "cls-hot",
    ]

    for pid in platform_order:
        data = results.get(pid)
        parts.append("━━━━━━━━━━━━━━━━━━━")
        if data and data["success"] and data["items"]:
            parts.append(f"📊 **{data['name']}**（共{data['total']}条）")
            parts.append("━━━━━━━━━━━━━━━━━━━")
            for idx, item in enumerate(data["items"], 1):
                title = item.get("title", "?")
                parts.append(f"  {idx}. {title}")
        else:
            name = data["name"] if data and "name" in data else pid
            parts.append(f"📊 **{name}**")
            parts.append("━━━━━━━━━━━━━━━━━━━")
            parts.append(f"  ❌ 获取失败")
        parts.append("")

    # ============ A股行情 ============
    if stocks_text and "获取失败" not in stocks_text:
        parts.append("━━━━━━━━━━━━━━━━━━━")
        parts.append("📈 **A股市场概况**")
        parts.append("━━━━━━━━━━━━━━━━━━━")
        for line in stocks_text.split("\n"):
            stripped = line.strip()
            if stripped and "━━" not in stripped and "📊" not in stripped:
                # 提取关键数据
                if "上证指数" in stripped:
                    cells = [c.strip() for c in stripped.split("|") if c.strip()]
                    parts.append(f"  上证指数：**{cells[1]}**（{cells[2]}）成交额 {cells[3]}")
                elif "深证成指" in stripped:
                    cells = [c.strip() for c in stripped.split("|") if c.strip()]
                    parts.append(f"  深证成指：**{cells[1]}**（{cells[2]}）成交额 {cells[3]}")
                elif "两市" in stripped:
                    cells = [c.strip() for c in stripped.split("|") if c.strip()]
                    if cells:
                        total = cells[-1].replace("**", "")
                        parts.append(f"  两市合计成交额：**{total}**")
        parts.append("")

    # ============ 融资融券 ============
    if margin_text and "获取失败" not in margin_text:
        parts.append("━━━━━━━━━━━━━━━━━━━")
        parts.append("📊 **融资融券概况**")
        parts.append("━━━━━━━━━━━━━━━━━━━")
        for line in margin_text.split("\n"):
            stripped = line.strip()
            if stripped and "━━" not in stripped and "📊" not in stripped and "❌" not in stripped:
                if "|" in stripped and "指标" not in stripped and "----" not in stripped:
                    cells = [c.strip() for c in stripped.split("|") if c.strip()]
                    if len(cells) >= 2:
                        parts.append(f"  {cells[0]}：{cells[1]}")
        parts.append("")

    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append(f"🕐 报告时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    parts.append("")
    parts.append("---")
    parts.append("*💡 数据来源：newsnow API（微博/百度/知乎/抖音/B站/头条/澎湃/凤凰网/贴吧/华尔街见闻/财联社）+ 东方财富 | 由 Daily Hot Search v4.2 自动生成*")

    return "\n".join(parts)
