"""
newsnow 数据获取模块

通过 newsnow 免费 API 获取多平台热搜数据。
API 地址: https://newsnow.busiyi.world/api/s?id={platform_id}&latest
数据来源：https://github.com/ourongxing/newsnow

验证时间：2026年7月14日
"""

import json
import urllib.request
import ssl
from typing import Optional

# 默认支持的热榜平台配置
# id: newsnow API 平台唯一标识
# name: 显示名称
# max_items: 最多获取多少条
DEFAULT_PLATFORMS = [
    {"id": "weibo",              "name": "微博",         "max_items": 10},
    {"id": "baidu",              "name": "百度热搜",     "max_items": 10},
    {"id": "toutiao",            "name": "今日头条",     "max_items": 10},
    {"id": "zhihu",              "name": "知乎",         "max_items": 10},
    {"id": "douyin",             "name": "抖音",         "max_items": 10},
    {"id": "bilibili-hot-search","name": "B站热搜",      "max_items": 10},
    {"id": "thepaper",           "name": "澎湃新闻",     "max_items": 10},
    {"id": "ifeng",              "name": "凤凰网",       "max_items": 10},
    {"id": "tieba",              "name": "贴吧",         "max_items": 10},
    {"id": "wallstreetcn-hot",   "name": "华尔街见闻",   "max_items": 10},
    {"id": "cls-hot",            "name": "财联社热门",   "max_items": 10},
]

# 可选用平台（newsnow API 也支持）
EXTRA_PLATFORMS = [
    {"id": "github",             "name": "GitHub 热门",   "max_items": 10},
    {"id": "v2ex",               "name": "V2EX",         "max_items": 10},
    {"id": "douban",             "name": "豆瓣",         "max_items": 10},
    {"id": "hupu",               "name": "虎扑",         "max_items": 10},
]

API_BASE_URL = "https://newsnow.busiyi.world/api/s"
TIMEOUT = 15  # 每个请求超时秒数


def fetch_platform(platform_id: str) -> Optional[list[dict]]:
    """
    获取单个平台热搜数据。

    Args:
        platform_id: 平台 ID（如 "weibo", "zhihu"）

    Returns:
        成功返回热搜条目列表，每条含 title/url/mobileUrl；
        失败返回 None。
    """
    url = f"{API_BASE_URL}?id={platform_id}&latest"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
    }

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        status = data.get("status", "")
        if status not in ("success", "cache"):
            return None

        items = data.get("items", [])
        return items

    except Exception:
        return None


def fetch_all_platforms(
    platforms: Optional[list[dict]] = None,
) -> dict[str, dict]:
    """
    批量获取多平台热搜数据。

    Args:
        platforms: 平台配置列表，默认使用 DEFAULT_PLATFORMS

    Returns:
        { "platform_id": { "name": "显示名", "items": [...], "success": True/False }, ... }
    """
    if platforms is None:
        platforms = DEFAULT_PLATFORMS

    results = {}
    for p in platforms:
        pid = p["id"]
        pname = p["name"]
        max_items = p.get("max_items", 10)

        items = fetch_platform(pid)
        if items:
            results[pid] = {
                "name": pname,
                "success": True,
                "items": items[:max_items],
                "total": len(items),
            }
        else:
            results[pid] = {
                "name": pname,
                "success": False,
                "items": [],
                "total": 0,
            }

    return results


def format_platform_section(
    results: dict[str, dict],
    platforms: Optional[list[dict]] = None,
) -> str:
    """
    将所有平台热搜格式化为 Markdown 文本块。

    Args:
        results: fetch_all_platforms 的返回值
        platforms: 平台配置列表（用于控制显示顺序）

    Returns:
        Markdown 格式的完整热搜板块
    """
    if platforms is None:
        platforms = DEFAULT_PLATFORMS

    parts = []
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("📊 全网热搜总览")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("")

    for p in platforms:
        pid = p["id"]
        data = results.get(pid)
        if not data or not data["success"]:
            parts.append(f"❌ **{p['name']}**：获取失败")
            parts.append("")
            continue

        items = data["items"]
        if not items:
            parts.append(f"📭 **{p['name']}**：暂无数据")
            parts.append("")
            continue

        parts.append(f"🔥 **{p['name']}**（共{data['total']}条）")
        for idx, item in enumerate(items, 1):
            title = item.get("title", "?")
            url = item.get("url", "")
            if url:
                parts.append(f"  {idx}. [{title}]({url})")
            else:
                parts.append(f"  {idx}. {title}")
        parts.append("")

    return "\n".join(parts)


if __name__ == "__main__":
    # 简单测试
    import sys

    test_id = sys.argv[1] if len(sys.argv) > 1 else "weibo"
    test_items = fetch_platform(test_id)
    if test_items:
        print(f"✅ {test_id}: 获取到 {len(test_items)} 条")
        for i, item in enumerate(test_items[:5], 1):
            print(f"  {i}. {item.get('title', '?')}")
    else:
        print(f"❌ {test_id}: 获取失败")
