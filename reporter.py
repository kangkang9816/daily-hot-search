"""
每日热搜早报 — 报告格式化模块 v4.1

板块重组：国内热点 / 国际热点 / A股市场
"""

from datetime import datetime

# 国内平台列表（按顺序显示）
DOMESTIC_PLATFORMS = [
    "weibo", "baidu", "toutiao", "zhihu", "douyin",
    "bilibili-hot-search", "thepaper", "ifeng", "tieba",
]

# 国际/财经平台列表
GLOBAL_PLATFORMS = [
    "wallstreetcn-hot", "cls-hot",
]


def should_global(title: str) -> bool:
    """判断标题是否偏向国际/财经话题，用于国内平台中筛选出国际内容"""
    global_keywords = [
        "美国", "特朗普", "伊朗", "美联储", "美股", "原油", "黄金",
        "全球", "国际", "欧盟", "欧洲", "韩国", "日本", "英国",
        "法国", "德国", "俄罗斯", "乌克兰", "北约", "美元", "油价",
        "关税", "半导体", "芯片", "韩国", "纳斯达克", "标普", "道指",
        "中东", "海湾", "霍尔木兹", "伊战", "战事", "战争",
        "出口", "进口", "外贸", "A股", "股市", "涨停", "跌停",
        "港股", "外资", "央行", "加息", "降息", "通胀",
        "沙特", "阿联酋", "以色列", "巴勒斯坦", "哈马斯",
        "美伊", "对伊", "制裁", "封锁", "海峡",
    ]
    for kw in global_keywords:
        if kw in title:
            return True
    return False


def build_report(
    date_str: str = None,
    weekday_str: str = None,
    results: dict = None,
    stocks_text: str = "",
    margin_text: str = "",
) -> str:
    """构建三板块报告"""
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

    # ============ 板块一：国内热点 ============
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("🇨🇳 **国内热点**")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("")

    has_domestic = False
    for pid in DOMESTIC_PLATFORMS:
        data = results.get(pid)
        if not data or not data["success"] or not data["items"]:
            continue
        has_domestic = True
        items = data["items"]
        pname = data["name"]
        parts.append(f"**{pname}** (Top 5)")
        count = 0
        for item in items:
            title = item.get("title", "")
            # 国内平台中如果标题明显是国际话题，跳过不放国内板块
            if should_global(title):
                continue
            count += 1
            if count > 5:
                break
            parts.append(f"  {count}. {title}")
        if count > 0:
            parts.append("")

    if not has_domestic:
        parts.append("暂无数据")
        parts.append("")

    # ============ 板块二：国际/财经热点 ============
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("🌍 **国际 / 财经热点**")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("")

    has_global = False

    # 先从国内平台中提取国际话题
    global_items = []
    for pid in DOMESTIC_PLATFORMS:
        data = results.get(pid)
        if not data or not data["success"] or not data["items"]:
            continue
        pname = data["name"]
        for item in data["items"]:
            title = item.get("title", "")
            if should_global(title):
                global_items.append((pname, title))
                has_global = True

    if global_items:
        parts.append(f"**各平台焦点** (国内平台中的国际话题)")
        for i, (src, title) in enumerate(global_items[:10], 1):
            parts.append(f"  {i}. [{src}] {title}")
        parts.append("")

    # 国际/财经平台
    for pid in GLOBAL_PLATFORMS:
        data = results.get(pid)
        if not data or not data["success"] or not data["items"]:
            continue
        has_global = True
        items = data["items"]
        pname = data["name"]
        parts.append(f"**{pname}** (Top 5)")
        for i, item in enumerate(items[:5], 1):
            title = item.get("title", "")
            parts.append(f"  {i}. {title}")
        parts.append("")

    if not has_global:
        parts.append("暂无数据")
        parts.append("")

    # ============ 板块三：A股 + 融资融券 ============
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("📈 **A股市场**")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("")

    # A股行情
    if stocks_text and "获取失败" not in stocks_text:
        # 从stocks_text提取核心数据
        for line in stocks_text.split("\n"):
            stripped = line.strip()
            if "|" in stripped and ("上证" in stripped or "深证" in stripped):
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                if len(cells) >= 4:
                    parts.append(f"  {cells[0]}：**{cells[1]}**（{cells[2]}）成交额 {cells[3]}")
            if "两市" in stripped:
                # 格式: | **两市合计** | | | **27040亿** |
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                total = cells[-1] if cells else ""
                if total:
                    parts.append(f"  两市合计成交额：**{total}**")
        parts.append("")

    # 融资融券
    if margin_text and "获取失败" not in margin_text:
        parts.append("**融资融券概况**")
        margin_lines = []
        for line in margin_text.split("\n"):
            stripped = line.strip()
            if "|" in stripped and "指标" not in stripped and "------" not in stripped:
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                if len(cells) >= 2:
                    margin_lines.append(f"  {cells[0]}：{cells[1]}")
        if margin_lines:
            parts.extend(margin_lines)
            parts.append("")

    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append(f"🕐 报告时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    parts.append("")
    parts.append("---")
    parts.append("*💡 聚合11个主流平台热搜 + A股行情 | 由 Daily Hot Search v4.1 自动生成*")

    return "\n".join(parts)
