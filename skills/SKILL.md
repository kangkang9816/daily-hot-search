---
name: daily-hot-search
description: 每日热搜早报推送 — 通过 newsnow API 聚合11+主流平台热搜 + A股行情，推送至微信
version: 4.0.0
author: Hermes Agent
---

# 每日热搜早报 v4.0

每天早上 7:30 自动运行脚本抓取并推送。

## 数据链路升级

**v4.0 重大变更**：从浏览器抓取（Playwright）改为 newsnow API 统一获取。

### 11 个默认平台

通过 `https://newsnow.busiyi.world/api/s?id={platform_id}&latest` 获取：
- `weibo`(微博), `baidu`(百度热搜), `toutiao`(今日头条), `zhihu`(知乎),
  `douyin`(抖音), `bilibili-hot-search`(B站热搜), `thepaper`(澎湃新闻),
  `ifeng`(凤凰网), `tieba`(贴吧), `wallstreetcn-hot`(华尔街见闻), `cls-hot`(财联社热门)

### A 股行情（保持不变）
- 新浪财经 API：`curl -H "Referer: https://finance.sina.com.cn/" "https://hq.sinajs.cn/list=sh000001,sz399001"`
- 注意：返回 GBK 编码，需 `stdout.decode("gbk")`
- 字段索引：[0名称, 1开盘, 2昨收, 3当前价, 4最高, 5最低, 8成交量, 9成交额]

### 融资融券（保持不变）
- 东方财富数据中心 API：`curl -H "Referer: https://data.eastmoney.com/rzrq/total.html" "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_RZRQ_LSHJ&columns=ALL&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=DIM_DATE&source=WEB"`
- 返回 JSON，字段：DIM_DATE(日期), RZYE(融资余额/元), RQYE(融券余额/元), RZRQYE(两融合计/元), RZMRE(融资买入额/元), RZJME(融资净买入/元)

## 脚本结构

```
daily-hot-search/
├── main.py                    # 主入口
├── reporter.py                # 报告格式化
├── config.yaml                # 配置
├── requirements.txt           # 无额外依赖（Python 标准库）
├── README.md                  # 说明文档
├── scripts/
│   ├── newsnow_fetcher.py     # 🔥 新增：newsnow API 统一抓取（11+平台）
│   ├── stocks.py              # A 股行情 + 融资融券（保持不变）
│   ├── baidu.py               # 废弃保留（原浏览器抓取）
│   ├── weibo.py               # 废弃保留（原浏览器抓取）
│   └── xueqiu.py              # 废弃保留（原浏览器抓取）
└── skills/
    └── SKILL.md               # 本文件
```

## 使用方式

```bash
# 常规运行（11平台 + A股 + 两融）
python3 /path/to/main.py

# 不推送，仅输出
python3 /path/to/main.py --no-push

# 只抓取前N个平台（测试）
python3 /path/to/main.py --platforms 3

# 包含额外平台（GitHub热门/V2EX/豆瓣/虎扑）
python3 /path/to/main.py --include-extra

# JSON 格式输出
python3 /path/to/main.py --format json
```

## Cron 任务设置

```javascript
cronjob({
  schedule: "30 7 * * *",
  prompt: "运行每日热搜早报脚本并推送结果。\n\n执行：python3 /tmp/daily-hot-search/main.py",
  deliver: "origin"
})
```

### 关键原则
- cron prompt 必须自包含，直接写操作指令
- 脚本无额外依赖（纯 Python 标准库 + curl）
- 报告自动保存到 `/opt/data/cron/output/daily-hot-search-YYYYMMDD.md`

## 推送消息模板

```
🔥 **每日热搜早报 · YYYY年M月D日（周X）**

📡 聚合 11 个主流平台热搜 + A股行情

━━━━━━━━━━━━━━━━━━━
📊 全网热搜总览
━━━━━━━━━━━━━━━━━━━

🔥 **微博**（共30条）
  1. [标题](链接)
  ...

🔥 **百度热搜**（共30条）
  ...

...（11个平台依次列出）...

━━━━━━━━━━━━━━━━━━━
📊 A股市场概况
━━━━━━━━━━━━━━━━━━━
| 指数 | 最新价 | 涨跌幅 | 成交额 |

━━━━━━━━━━━━━━━━━━━
📊 融资融券概况
━━━━━━━━━━━━━━━━━━━
| 指标 | 数值 |

━━━━━━━━━━━━━━━━━━━
🕐 报告时间: YYYY-MM-DD HH:MM:SS

---
*💡 数据来源：newsnow API + 东方财富 | 由 Daily Hot Search v4.0 自动生成*
```
