"""
雪球热股榜爬取模块

通过 Playwright 导航到雪球行情中心，使用 browser_snapshot 提取热股榜和市场一览数据。

验证时间：2026年7月
页面结构：xueqiu.com/hq 在"热股榜"区域找listitem，格式"1. 赛力斯 +1.58%"
市场一览也在同一页面：上证/深证/创业板/科创50
"""

import re


def parse_xueqiu_snapshot(snapshot_text: str) -> dict:
    """
    从 browser_snapshot 文本中解析雪球数据。
    
    页面有两个主要区域：
    1. 市场一览 — 显示主要指数
    2. 热股榜 — 排名股票列表
    """
    if not snapshot_text:
        return {"indices": [], "stocks": []}
    
    indices = []
    stocks = []
    
    lines = snapshot_text.split('\n')
    
    # 标记当前正在解析的区域
    in_stock_section = False
    in_index_section = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检测区域标题
        if '热股榜' in line:
            in_stock_section = True
            in_index_section = False
            continue
        if '市场一览' in line or ('上证' in line and '指数' in line):
            in_index_section = True
            in_stock_section = False
            # 指数行也收集
        if '热门话题' in line or '要闻' in line:
            in_stock_section = False
            in_index_section = False
            continue
        
        # 解析股票行：排名. 股票名 涨跌幅
        stock_match = re.match(r'(\d+)\.\s*([\u4e00-\u9fffA-Za-z]+)\s*([+-]\d+\.\d+%)', line)
        if stock_match and in_stock_section:
            stocks.append({
                'rank': int(stock_match.group(1)),
                'name': stock_match.group(2),
                'change': stock_match.group(3)
            })
            continue
        
        # 解析指数行：指数名 数值 涨跌幅
        index_match = re.match(r'([\u4e00-\u9fffA-Za-z0-9]+(?:指数)?)\s+(\d+[\.\d,]*)\s*([+-]?\d+\.\d+%)', line)
        if index_match:
            indices.append({
                'name': index_match.group(1),
                'value': index_match.group(2),
                'change': index_match.group(3)
            })
            continue
    
    return {"indices": indices[:6], "stocks": stocks[:6]}


def format_xueqiu(data: dict) -> str:
    """格式化雪球数据为 Markdown"""
    indices = data.get("indices", [])
    stocks = data.get("stocks", [])
    
    if not indices and not stocks:
        return "━━━━━━━━━━━━━━━━━━━\n📊 雪球热榜\n━━━━━━━━━━━━━━━━━━━\n❌ 雪球热榜：获取失败"
    
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 雪球热榜", "━━━━━━━━━━━━━━━━━━━", ""]
    
    if indices:
        lines.append("📈 **市场一览**")
        for idx in indices:
            lines.append(f"| {idx['name']} | {idx['value']} | {idx['change']} |")
        lines.append("")
    
    if stocks:
        lines.append("🔥 **热股榜**")
        for s in stocks:
            symbol = "🔴" if s['change'].startswith('+') else "🟢"
            lines.append(f"{symbol} {s['rank']}. {s['name']} {s['change']}")
    
    return "\n".join(lines)
