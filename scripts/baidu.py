"""
百度热搜爬取模块

通过 Playwright 浏览器导航到百度热搜榜，使用 innerText 提取热搜标题和指数。
提取策略：全量文本提取 → 按行解析（热搜指数 + 标题 + 标签）。

验证时间：2026年7月
"""

import re
import json


def extract_baidu_js() -> str:
    """返回用于在浏览器中提取百度热搜的 JS 代码"""
    return """
() => {
    const text = document.body.innerText;
    const idx = text.indexOf('热搜榜');
    if (idx < 0) return '';
    return text.substring(idx, idx + 3000);
}
"""


def parse_baidu(raw_text: str, top_n: int = 10) -> list[dict]:
    """
    解析百度热搜文本。
    
    页面结构规律：
    `热搜榜` → 置顶(无排名号) → 7位数热搜指数 → 标题 → 排名1 → 7位数指数 → 标题+标签(热/沸/新)
    标签在数字后的同一行用双空格隔开，如"沈阳将在全市实行紧急避险措施  新"
    """
    if not raw_text:
        return []
    
    results = []
    # 切分行
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    
    i = 0
    pinned = None
    while i < len(lines):
        line = lines[i]
        # 跳过标题行
        if line == '热搜榜' or '热搜指数' in line:
            i += 1
            continue
        
        # 检查是否为数字行（热搜指数，7位以上数字）
        if re.match(r'^\d{5,}$', line):
            score = int(line)
            # 下一行应该是标题
            if i + 1 < len(lines):
                title_line = lines[i + 1]
                # 处理标题+标签（双空格分隔）
                parts = re.split(r'  +', title_line)
                title = parts[0].strip()
                tag = parts[1].strip() if len(parts) > 1 else ''
                
                if not pinned:
                    pinned = {'rank': '🔴', 'title': title, 'score': score, 'tag': tag}
                else:
                    results.append({'rank': len(results) + 1, 'title': title, 'score': score, 'tag': tag})
                i += 2
                continue
        i += 1
    
    # 置顶放最前面
    final = []
    if pinned:
        final.append(pinned)
    final.extend(results[:top_n])
    return final


def format_baidu(results: list[dict]) -> str:
    """格式化百度热搜为 Markdown"""
    if not results:
        return "━━━━━━━━━━━━━━━━━━━\n📊 百度热搜 Top 10\n━━━━━━━━━━━━━━━━━━━\n❌ 百度热搜：获取失败"
    
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 百度热搜 Top 10", "━━━━━━━━━━━━━━━━━━━",
             "| # | 热搜词 | 指数 | 标签 |",
             "|:--:|------|------:|:----:|"]
    for item in results:
        rank = item['rank']
        title = item['title']
        score = f"{item['score']:,}" if item.get('score') else ''
        tag = item.get('tag', '')
        lines.append(f"| {rank} | {title} | {score} | {tag} |")
    return "\n".join(lines)
