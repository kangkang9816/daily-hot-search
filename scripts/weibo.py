"""
微博热搜爬取模块

通过 Playwright 导航到微博移动端内部 API 获取 JSON 数据，提取热搜标题和热度。
无需登录，内部 API 绕过登录墙。
"""

import json

EXTRACT_WEIBO_JS = """
() => {
    const body = document.querySelector('body');
    const data = JSON.parse(body.innerText);
    const cards = data?.data?.cards || [];
    const results = [];
    cards.forEach(card => {
        const groups = card?.card_group || [];
        groups.forEach((item) => {
            if (item?.desc && item?.desc !== '\u67e5\u770b\u66f4\u591a') {
                results.push({
                    rank: results.length + 1,
                    title: item.desc,
                    hot: item?.desc_extr || '',
                    label: item?.icon_desc || ''
                });
            }
        });
    });
    return JSON.stringify(results.slice(0, 10), null, 2);
}
"""


def parse_weibo(js_result: str) -> list[dict]:
    try:
        return json.loads(js_result)
    except (json.JSONDecodeError, TypeError):
        return []


def format_weibo(results: list[dict], top_n: int = 10) -> str:
    if not results:
        return "❌ 微博热搜：获取失败"
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 微博热搜 Top 10", "━━━━━━━━━━━━━━━━━━━", ""]
    for item in results[:top_n]:
        rank = item.get("rank", "")
        title = item.get("title", "")
        hot = item.get("hot", "")
        label = item.get("label", "")
        hot_str = f" \u70ed\u5ea6: {hot}" if hot else ""
        label_str = f" [{label}]" if label else ""
        lines.append(f"| {rank} | {title} |{label_str}{hot_str} |")
    return "\n".join(lines)
