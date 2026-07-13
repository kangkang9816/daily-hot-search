# 🔥 Daily Hot Search — 每日热搜早报

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 自动抓取 **百度热搜、微博热搜、雪球热榜、A股行情、融资融券** 五大模块数据，每天定时推送早报到你的微信/Telegram 等平台。

## ✨ 功能

- 📊 **百度热搜** Top 10 — 标题 + 热搜指数（浏览器 innerText 提取）
- 🔥 **微博热搜** Top 10 — 标题 + 热度值 + 标签（网页版公开页面，无需登录）
- 📈 **雪球热股榜** — 热股榜 Top 6 + 市场一览（上证/深证/创业板/科创50）
- 💹 **A股行情** — 上证指数 & 深证成指实时数据（新浪财经 API）
- 💰 **融资融券** — 两融余额、净买入、占比等指标（东方财富数据中心 API）
- ⏰ **定时推送** — 通过 Cron 每天早上 7:30 自动发送
- 📤 **多平台** — 微信、Telegram、Discord 等

## 🚀 快速开始

### 方式一：Hermes Agent（推荐）

如果你运行的是 Hermes Agent，直接用 cron 技能加载即可：

```bash
cronjob create \
  schedule="30 7 * * *" \
  skills="[\"daily-hot-search\"]" \
  prompt="（精简的完整操作指令，含URL和提取方法）" \
  deliver="origin"
```

**关键原则：**
- skills 只加载 `daily-hot-search` **一个**即可，浏览器工具和 mcp_fetch 在 cron 会话中默认可用
- cron 的 prompt 必须**自包含**（直接写操作步骤和URL），不要依赖AI阅读长文档
- 详情见 `skills/SKILL.md`

### 方式二：Docker 部署

```bash
docker compose up -d
```

### 方式三：直接运行

```bash
pip install -r requirements.txt
python main.py
```

## 📁 项目结构

```
daily-hot-search/
├── main.py                  # 主入口
├── config.yaml              # 配置文件
├── scripts/
│   ├── baidu.py             # 百度热搜爬取
│   ├── weibo.py             # 微博热搜爬取（网页版公开提取）
│   ├── xueqiu.py            # 雪球热股榜爬取
│   └── stocks.py            # A股行情 & 融资融券
├── reporter.py              # 报告格式化输出
├── skills/
│   └── SKILL.md             # Hermes Agent 技能配置
├── docker-compose.yaml      # Docker 部署
├── requirements.txt         # Python 依赖
└── README.md
```

## 🔧 配置

编辑 `config.yaml` 配置你的推送渠道和数据源。

## 📦 模块说明

| 模块 | 方法 | 数据源 |
|------|------|--------|
| **百度热搜** | 浏览器 innerText 提取 | `top.baidu.com/board?tab=realtime` |
| **微博热搜** ✅ | 网页版公开页面提取（无需登录） | `weibo.com/newlogin?tabtype=search` |
| **雪球热股榜** | 浏览器 snapshot 提取 | `xueqiu.com/hq` |
| **A股行情** | curl + 新浪财经 API（需 Referer） | `hq.sinajs.cn` |
| **融资融券** | curl + 东方财富数据中心 API（需 Referer） | `datacenter-web.eastmoney.com` |

## 📊 推送消息模板

```
🔥 每日热搜早报 · 2026年7月14日（二）

━━━━━━━━━━━━━━━━━━━
📊 百度热搜 Top 10
━━━━━━━━━━━━━━━━━━━
| # | 热搜词 | 指数 | 标签 |
| 🔴 | 置顶标题 | 7,xxx,xxx | |
| 1 | 标题 | 7,xxx,xxx | 热 |

━━━━━━━━━━━━━━━━━━━
📊 微博热搜 Top 10
━━━━━━━━━━━━━━━━━━━
| # | 热搜词 | 热度 | 标签 |

━━━━━━━━━━━━━━━━━━━
📊 雪球热股榜 Top 6
━━━━━━━━━━━━━━━━━━━
1. 赛力斯 +1.58%

━━━━━━━━━━━━━━━━━━━
📊 A股市场概况
━━━━━━━━━━━━━━━━━━━
| 指数 | 最新价 | 涨跌幅 | 成交额 |
| 上证指数 | x,xxx.xx | ±x.xx% | x,xxx亿 |

━━━━━━━━━━━━━━━━━━━
📊 融资融券概况
━━━━━━━━━━━━━━━━━━━
| 指标 | 数值 |
| 融资余额 | xx,xxx亿 |
| 两融余额合计 | xx,xxx亿 |

📌 热点总结
```

## ⚠️ 注意事项

- 百度热搜：CSS类名可能变化，用 `document.body.innerText` 提取最稳定
- 微博热搜：2026年7月起 `m.weibo.cn` 内部 API 已全面失效（HTTP 432），改用 `weibo.com/newlogin?tabtype=search` 网页版公开页面
- 融资融券：T+1 公布，最新数据为前一个交易日
- 周六/周日：A股无交易，数据标注为上一个交易日
- **技巧文档防过载**：SKILL.md 保持在 300 行以内，cron prompt 必须自包含

## 📄 许可证

[MIT](LICENSE)
