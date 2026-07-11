"""
雪球热榜爬取模块

通过 Playwright 导航到雪球首页，使用 JS 遍历表格提取热门话题和热股榜数据。
雪球页面有登录弹窗，但 JS 提取可穿透弹窗获取底层数据。
"""

import json

EXTRACT_XUEQIU_JS = """
() => {
    const tables = document.querySelectorAll('table');
    const results = [];
    tables.forEach((table, idx) => {
        const rows = table.querySelectorAll('tr');
        const sectionData = [];
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            sectionData.push(Array.from(cells).map(c => c.textContent.trim()).join(' | '));
        });
        results.push(`Section ${idx}:`, ...sectionData);
    });
    return results.join('\\n');
}
"""


def parse_xueqiu_table(raw_text: str) -> dict:
    if not raw_text:
        return {"topics": [], "stocks": []}
    lines = raw_text.strip().split("\n")
    sections = []
    current_section = None
    for line in lines:
        if line.startswith("Section "):
            if current_section:
                sections.append(current_section)
            current_section = {"name": line, "rows": []}
        elif current_section is not None and line.strip():
            current_section["rows"].append(line.strip())
    if current_section:
        sections.append(current_section)
    topics, stocks = [], []
    for sec in sections:
        combined = " ".join(sec["rows"]).lower()
        if "\u8bdd\u9898" in combined or "\u8ba8\u8bba" in combined:
            topics = sec["rows"]
        elif "\u80a1" in combined or "%" in combined:
            stocks = sec["rows"]
    if not topics and not stocks and len(sections) >= 2:
        topics = sections[0]["rows"]
        stocks = sections[1]["rows"]
    return {"topics": topics[:10], "stocks": stocks[:6]}


def format_xueqiu(data: dict) -> str:
    topics = data.get("topics", [])
    stocks = data.get("stocks", [])
    if not topics and not stocks:
        return "❌ 雪球热榜：获取失败"
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 雪球热榜", "━━━━━━━━━━━━━━━━━━━", ""]
    if topics:
        lines.append(f"🔥 **\u70ed\u95e8\u8bdd\u9898 Top {len(topics)}**")
        for t in topics:
            lines.append(f"  {t.replace(' | ', '  ').strip()}")
        lines.append("")
    if stocks:
        lines.append("📈 **\u70ed\u80a1\u699c**")
        for s in stocks:
            lines.append(f"  {s.replace(' | ', '  ').strip()}")
    return "\n".join(lines)
