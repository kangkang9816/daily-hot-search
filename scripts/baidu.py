"""
百度热搜爬取模块

使用 Playwright 浏览器导航到百度热搜榜，通过 JS 提取热搜标题和指数。
提取策略：URL 参数法（从链接的 wd 参数解码标题）+ 数字匹配法提取热搜指数。
"""

import json

EXTRACT_TITLES_JS = """
() => {
    const items = document.querySelectorAll('a[href*="sa=fyb_news"]');
    const results = [];
    let rank = 0;
    const first = items[0];
    if (first) {
        try {
            const url = new URL(first.href);
            const wd = url.searchParams.get('wd');
            if (wd) {
                const title = decodeURIComponent(wd);
                if (title) results.push({ rank: '\u7f6e\u9876', title });
            }
        } catch(e) {}
    }
    items.forEach(a => {
        try {
            const url = new URL(a.href);
            const wd = url.searchParams.get('wd');
            if (wd) {
                const title = decodeURIComponent(wd);
                if (title && !results.some(r => r.title === title)) {
                    rank++;
                    results.push({ rank, title });
                }
            }
        } catch(e) {}
    });
    return JSON.stringify(results, null, 2);
}
"""

EXTRACT_SCORES_JS = """
() => {
    const scores = [];
    document.querySelectorAll('[class*="hot-index"], [class*="num"], [class*="count"]').forEach(el => {
        const text = el.textContent.trim();
        if (/^\\d{5,}$/.test(text)) scores.push(text);
    });
    return JSON.stringify(scores);
}
"""


def parse_baidu(titles_json: str, scores_json: str) -> list[dict]:
    try:
        titles = json.loads(titles_json)
    except (json.JSONDecodeError, TypeError):
        return []
    try:
        scores = json.loads(scores_json)
    except (json.JSONDecodeError, TypeError):
        scores = []
    results = []
    score_idx = 0
    for item in titles:
        entry = {"rank": item.get("rank", ""), "title": item.get("title", ""), "score": ""}
        if score_idx < len(scores):
            entry["score"] = scores[score_idx]
            score_idx += 1
        results.append(entry)
    return results


def format_baidu(results: list[dict], top_n: int = 10) -> str:
    if not results:
        return "❌ 百度热搜：获取失败"
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 百度热搜 Top 10", "━━━━━━━━━━━━━━━━━━━", ""]
    for item in results[:top_n]:
        rank = item["rank"]
        title = item["title"]
        score = item["score"]
        if score:
            try:
                score = f"{int(score):,}"
            except ValueError:
                pass
            lines.append(f"| {rank} | {title} | {score} |")
        else:
            lines.append(f"| {rank} | {title} |")
    return "\n".join(lines)
