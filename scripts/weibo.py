"""
微博热搜爬取模块

通过 Playwright 导航到微博网页版公开热搜页面，使用 innerText 提取热搜标题、热度值和排名。

验证时间：2026年7月
注意：m.weibo.cn API 已全面失效（HTTP 432 访客验证），weibo.com/ajax/side/hotSearch 返回 403
当前方案：weibo.com/newlogin?tabtype=search 网页版公开页面（无需登录）
"""

import re
import json


EXTRACT_WEIBO_JS = """
() => {
    const body = document.body.innerText;
    const idx = body.indexOf('微博热搜');
    if (idx < 0) return '';
    // 从'微博热搜'往后取2000字符
    return body.substring(idx, idx + 2000);
}
"""


def parse_weibo(raw_text: str, top_n: int = 10) -> list[dict]:
    """
    解析微博热搜文本。
    
    页面结构：
    `微博热搜` → 一个个条目，格式为：
    标签(热/沸/新/荐) 空格 热度值(数字) 空格 排名(数字)  标题
    
    例如：热 939146 2  沈阳将在全市实行紧急避险措施
    标题在排名数字之后，用双空格或换行分隔
    """
    if not raw_text:
        return []
    
    results = []
    # 查找所有匹配模式：标签(热/沸/新/荐/..) + 空格 + 数字(热度) + 空格 + 数字(排名)
    # 模式: (标签) (热度) (排名)
    pattern = r'(热|沸|新|荐|爆|剧)\s+(\d{4,})\s+(\d{1,2})'
    
    # 先找到"微博热搜"起始位置
    idx = raw_text.find('微博热搜')
    if idx < 0:
        idx = 0
    text = raw_text[idx:]
    
    # 逐行解析
    lines = text.split('\n')
    parsed = []
    current_entry = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 尝试匹配标签+热度+排名模式
        m = re.search(pattern, line)
        if m:
            # 如果已经有了一个未完成的条目，先保存
            if current_entry.get('title'):
                parsed.append(current_entry)
            
            tag = m.group(1)
            hot = int(m.group(2))
            rank = int(m.group(3))
            
            # 排名数字之后的内容即为标题
            # 找排名数字后面的部分
            after_rank = line[m.end():].strip()
            title = after_rank.lstrip()
            
            current_entry = {
                'rank': rank,
                'title': title,
                'hot': hot,
                'tag': tag
            }
        elif current_entry.get('title') is None and '热搜' not in line:
            # 可能是标题行但没匹配到模式，尝试宽泛匹配
            pass
    
    # 保存最后一个条目
    if current_entry.get('title'):
        parsed.append(current_entry)
    
    # 按排名排序去重
    seen_titles = set()
    for item in sorted(parsed, key=lambda x: x['rank']):
        if item['title'] and item['title'] not in seen_titles:
            results.append(item)
            seen_titles.add(item['title'])
    
    return results[:top_n]


def format_weibo(results: list[dict]) -> str:
    """格式化微博热搜为 Markdown"""
    if not results:
        return "━━━━━━━━━━━━━━━━━━━\n📊 微博热搜 Top 10\n━━━━━━━━━━━━━━━━━━━\n❌ 微博热搜：获取失败"
    
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 微博热搜 Top 10", "━━━━━━━━━━━━━━━━━━━",
             "| # | 热搜词 | 热度 | 标签 |",
             "|:--:|------|:----:|:----:|"]
    for item in results:
        rank = item['rank']
        title = item['title']
        hot = f"{item['hot']:,}" if isinstance(item.get('hot'), int) else str(item.get('hot', ''))
        tag = item.get('tag', '')
        lines.append(f"| {rank} | {title} | {hot} | {tag} |")
    return "\n".join(lines)
