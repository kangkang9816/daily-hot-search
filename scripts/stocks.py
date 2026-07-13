"""
A股行情 & 融资融券爬取模块

数据源：
- 指数行情：新浪财经 API（curl，需设置 Referer）
- 融资融券：东方财富数据中心 API（curl，需设置 Referer）

验证时间：2026年7月
"""

import json
import re


def get_sina_stock_url() -> str:
    """返回新浪财经 API URL"""
    return "https://hq.sinajs.cn/list=sh000001,sz399001"


def parse_sina_result(api_result: str) -> dict:
    """
    解析新浪财经 API 返回数据。
    
    返回格式：
    var hq_str_sh000001="上证指数,开盘价,昨收价,当前价,最高价,最低价,0,0,成交量(手),成交额(元),...,日期,时间"
    
    字段索引：[0名称, 1开盘, 2昨收, 3当前价, 4最高, 5最低, 8成交量(手), 9成交额(元)]
    两市成交额=(上证成交额+深证成交额)/1e8亿
    """
    if not api_result:
        return {"sh": None, "sz": None, "total_amount_yi": 0}
    
    result = {"sh": None, "sz": None, "total_amount_yi": 0}
    total_amount = 0
    
    for line in api_result.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 解析每个指数行
        m = re.search(r'hq_str_(\w+)="(.+)"', line)
        if not m:
            continue
        
        code = m.group(1)
        fields = m.group(2).split(',')
        
        if len(fields) < 10:
            continue
        
        name = fields[0]
        open_price = fields[1]
        prev_close = fields[2]
        current = fields[3]
        high = fields[4]
        low = fields[5]
        volume = fields[8]  # 成交量(手)
        amount = fields[9]  # 成交额(元)
        
        # 计算涨跌幅
        change_pct = ''
        try:
            cur = float(current)
            prev = float(prev_close)
            if prev > 0:
                change_pct = f"{(cur - prev) / prev * 100:.2f}%"
        except (ValueError, IndexError):
            pass
        
        # 成交额转亿
        amount_yi = ''
        try:
            amount_f = float(amount)
            amount_yi = f"{amount_f / 1e8:.0f}亿"
            total_amount += amount_f
        except (ValueError, IndexError):
            amount_yi = amount
        
        index_data = {
            'name': name,
            'code': code,
            'current': current,
            'change_pct': change_pct,
            'high': high,
            'low': low,
            'volume': volume,
            'amount_yi': amount_yi,
        }
        
        if code == 'sh000001':
            result['sh'] = index_data
        elif code == 'sz399001':
            result['sz'] = index_data
    
    result['total_amount_yi'] = f"{total_amount / 1e8:.0f}亿" if total_amount > 0 else '0亿'
    return result


def get_margin_api_url() -> str:
    """返回东方财富融资融券 API URL"""
    return ("https://datacenter-web.eastmoney.com/api/data/v1/get"
            "?reportName=RPTA_RZRQ_LSHJ&columns=ALL"
            "&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=DIM_DATE&source=WEB")


def parse_margin_result(api_result: str) -> dict:
    """
    解析东方财富融资融券 API 返回数据。
    
    返回JSON字段：
    DIM_DATE(交易日), RZYE(融资余额/元), RQYE(融券余额/元),
    RZRQYE(两融合计/元), RZMRE(融资买入额/元), RZJME(融资净买入/元),
    RZYEZB(融资余额占流通市值比%)
    """
    if not api_result:
        return {}
    
    try:
        data = json.loads(api_result)
    except json.JSONDecodeError:
        return {}
    
    try:
        items = data.get('result', {}).get('data', [])
        if not items:
            return {}
        d = items[0]
        
        def yuan_to_yi(val) -> str:
            try:
                return f"{float(val) / 1e8:.2f}亿"
            except (ValueError, TypeError):
                return str(val)
        
        def format_date(val) -> str:
            s = str(val)
            if len(s) == 8:
                return f"{s[:4]}-{s[4:6]}-{s[6:]}"
            return s
        
        return {
            '交易日期': format_date(d.get('DIM_DATE', '')),
            '融资余额': yuan_to_yi(d.get('RZYE', 0)),
            '融券余额': yuan_to_yi(d.get('RQYE', 0)),
            '两融余额合计': yuan_to_yi(d.get('RZRQYE', 0)),
            '融资买入额': yuan_to_yi(d.get('RZMRE', 0)),
            '融资净买入': yuan_to_yi(d.get('RZJME', 0)),
            '余额占比': f"{d.get('RZYEZB', '')}%" if d.get('RZYEZB') else '',
        }
    except (KeyError, TypeError, IndexError):
        return {}


def format_stocks(data: dict) -> str:
    """格式化A股行情为 Markdown"""
    sh = data.get('sh')
    sz = data.get('sz')
    total = data.get('total_amount_yi', '')
    
    if not sh and not sz:
        return "━━━━━━━━━━━━━━━━━━━\n📊 A股市场概况\n━━━━━━━━━━━━━━━━━━━\n❌ A股行情：获取失败"
    
    lines = ["━━━━━━━━━━━━━━━━━━━", "📊 A股市场概况", "━━━━━━━━━━━━━━━━━━━",
             "| 指数 | 最新价 | 涨跌幅 | 成交额 |",
             "|------|--------|--------|--------|"]
    if sh:
        lines.append(f"| {sh['name']} | {sh['current']} | {sh['change_pct']} | {sh['amount_yi']} |")
    if sz:
        lines.append(f"| {sz['name']} | {sz['current']} | {sz['change_pct']} | {sz['amount_yi']} |")
    lines.append(f"| **两市合计** | | | **{total}** |")
    
    return "\n".join(lines)


def format_margin(data: dict) -> str:
    """格式化融资融券数据为 Markdown"""
    if not data:
        return "\n━━━━━━━━━━━━━━━━━━━\n📊 融资融券概况\n━━━━━━━━━━━━━━━━━━━\n❌ 融资融券：获取失败"
    
    lines = ["\n━━━━━━━━━━━━━━━━━━━", "📊 融资融券概况", "━━━━━━━━━━━━━━━━━━━",
             "| 指标 | 数值 |", "|------|------|"]
    
    key_order = ['交易日期', '融资余额', '融券余额', '两融余额合计', '融资买入额', '融资净买入', '余额占比']
    for key in key_order:
        if key in data:
            lines.append(f"| {key} | {data[key]} |")
    
    return "\n".join(lines)
