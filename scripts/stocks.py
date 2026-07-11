"""
A股行情 & 融资融券爬取模块

- 上证指数：东方财富 push2 API（curl 可访问）
- 深证成指：新浪财经行情页面（Playwright 备选）
- 融资融券：东方财富数据页面（Playwright 表格提取）
"""

import json
import re

EXTRACT_SZZS_TITLE_JS = """
() => { return document.title; }
"""

EXTRACT_SZZS_BODY_JS = """
() => {
    const allText = document.body.innerText;
    const lines = allText.split('\\n').filter(l => l.includes('\u6210\u4ea4\u91cf') || l.includes('\u6210\u4ea4\u989d'));
    return JSON.stringify(lines.slice(0, 5));
}
"""

EXTRACT_MARGIN_JS = """
() => {
    const tables = document.querySelectorAll('table');
    const results = [];
    tables.forEach((table, idx) => {
        const rows = table.querySelectorAll('tr');
        const tableData = [];
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            tableData.push(Array.from(cells).map(c => c.textContent.trim()).join(' | '));
        });
        results.push(`Table ${idx}:`, ...tableData);
    });
    return results.join('\\n');
}
"""


def parse_shanghai(api_result: str) -> dict:
    try:
        data = json.loads(api_result)
        if data.get("data"):
            d = data["data"]
            return {
                "name": d.get("f58", "\u4e0a\u8bc1\u6307\u6570"),
                "code": d.get("f57", "000001"),
                "price": d.get("f43", ""),
                "change_pct": d.get("f3", ""),
                "high": d.get("f44", ""),
                "low": d.get("f45", ""),
                "volume": d.get("f47", ""),
                "amount": d.get("f48", ""),
            }
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass
    return {}


def parse_shenzhen(title: str, body_text: str) -> dict:
    result = {"name": "\u6df1\u8bc1\u6210\u6307"}
    if title:
        m = re.search(r"([\d,.]+)\(([+-]?[\d.]+%)\)", title)
        if m:
            result["price"] = m.group(1)
            result["change_pct"] = m.group(2)
    if body_text:
        vol_m = re.search(r"\u6210\u4ea4\u91cf[\uff1a:]\s*([\d.]+\u4ebf?\u624b?)", body_text)
        amt_m = re.search(r"\u6210\u4ea4\u989d[\uff1a:]\s*([\d.]+\u4ebf?\u5143?)", body_text)
        if vol_m:
            result["volume"] = vol_m.group(1)
        if amt_m:
            result["amount"] = amt_m.group(1)
    return result


def parse_margin_trading(raw_text: str) -> dict:
    if not raw_text:
        return {}
    lines = raw_text.strip().split("\n")
    data_rows = [l for l in lines if not l.startswith("Table ")]
    result = {}
    for row in data_rows[:15]:
        parts = [p.strip() for p in row.split("|")]
        if len(parts) >= 2:
            result[parts[0]] = parts[1]
        elif len(parts) >= 1:
            result[f"col_{len(result)}"] = parts[0]
    return result


def format_stocks(sh_data: dict, sz_data: dict) -> str:
    if not sh_data and not sz_data:
        return "❌ A股行情：获取失败"
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 A股市场概况", "━━━━━━━━━━━━━━━━━━━", ""]
    lines.append("| 指数 | 最新价 | 涨跌幅 | 成交额 |")
    lines.append("|------|--------|--------|--------|")
    total_amount = 0
    if sh_data:
        name = sh_data.get("name", "\u4e0a\u8bc1\u6307\u6570")
        price = sh_data.get("price", "-")
        change = sh_data.get("change_pct", "-")
        amount = sh_data.get("amount", "0")
        try:
            amount_yi = f"{float(amount) / 1e8:.0f}\u4ebf}" if amount else "-"
            total_amount += float(amount or 0)
        except ValueError:
            amount_yi = amount
        lines.append(f"| {name} | {price} | {change}% | {amount_yi} |")
    if sz_data:
        name = sz_data.get("name", "\u6df1\u8bc1\u6210\u6307")
        price = sz_data.get("price", "-")
        change = sz_data.get("change_pct", "-")
        amount = sz_data.get("amount", "-")
        lines.append(f"| {name} | {price} | {change} | {amount} |")
    if total_amount > 0:
        lines.append(f"| 两市合计 | | | **{total_amount / 1e8:.0f}\u4ebf** |")
    return "\n".join(lines)


def format_margin(data: dict) -> str:
    if not data:
        return "❌ 融资融券：获取失败"
    lines = ["", "━━━━━━━━━━━━━━━━━━━", "📊 融资融券概况", "━━━━━━━━━━━━━━━━━━━", ""]
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    field_map = {
        "\u878d\u8d44\u4f59\u989d": "\u878d\u8d44\u4f59\u989d",
        "\u878d\u5238\u4f59\u989d": "\u878d\u5238\u4f59\u989d",
        "\u4e24\u878d\u4f59\u989d": "\u878d\u8d44\u878d\u5238\u4f59\u989d\u5408\u8ba1",
        "\u878d\u8d44\u4e70\u5165\u989d": "\u878d\u8d44\u4e70\u5165\u989d",
        "\u878d\u8d44\u507f\u8fd8\u989d": "\u878d\u8d44\u507f\u8fd8\u989d",
        "\u878d\u8d44\u51c0\u4e70\u5165": "\u878d\u8d44\u51c0\u4e70\u5165",
        "\u878d\u8d44\u4f59\u989d\u5360\u6d41\u901a\u5e02\u503c\u6bd4": "\u4f59\u989d\u5360\u6d41\u901a\u5e02\u503c\u6bd4",
        "\u65e5\u671f": "\u4ea4\u6613\u65e5\u671f",
    }
    output_fields = ["\u4ea4\u6613\u65e5\u671f", "\u878d\u8d44\u4f59\u989d", "\u878d\u5238\u4f59\u989d",
                     "\u878d\u8d44\u878d\u5238\u4f59\u989d\u5408\u8ba1",
                     "\u878d\u8d44\u4e70\u5165\u989d", "\u878d\u8d44\u507f\u8fd8\u989d",
                     "\u878d\u8d44\u51c0\u4e70\u5165", "\u4f59\u989d\u5360\u6d41\u901a\u5e02\u503c\u6bd4"]
    for field in output_fields:
        for key, val in field_map.items():
            if val == field:
                for dk, dv in data.items():
                    if key in dk:
                        lines.append(f"| {field} | {dv} |")
                        break
                break
    return "\n".join(lines)
