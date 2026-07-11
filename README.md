# 🔥 Daily Hot Search — 每日热搜早报

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 自动抓取百度热搜、微博热搜、雪球热榜、A股行情，每天定时推送早报到你的微信/Telegram等平台。

## ✨ 功能

- 📊 **百度热搜** Top 10 — 标题 + 热搜指数
- 🔥 **微博热搜** Top 10 — 标题 + 热度值
- 📈 **雪球热榜** — 热门话题 Top 10 + 热股榜 Top 5
- 💹 **A股行情** — 上证指数 & 深证成指实时数据
- 💰 **融资融券** — 两融余额、净买入等指标
- ⏰ **定时推送** — 通过 Cron 每天自动发送
- 📤 **多平台** — 微信、Telegram、Discord 等

## 🚀 快速开始

### 方式一：Hermes Agent（推荐）

如果你运行的是 Hermes Agent，直接用 cron 技能加载即可：

```bash
cronjob create \
  schedule="30 7 * * *" \
  prompt="抓取热搜并推送" \
  skills="[\"native-mcp\", \"daily-hot-search\"]"
```

详情见 `skills/daily-hot-search/` 目录下的技能配置。

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
│   ├── weibo.py             # 微博热搜爬取
│   ├── xueqiu.py            # 雪球热榜爬取
│   └── stocks.py            # A股行情 & 融资融券
├── reporter.py              # 报告格式化输出
├── docker-compose.yaml      # Docker 部署
├── requirements.txt         # Python 依赖
└── README.md
```

## 🔧 配置

编辑 `config.yaml` 配置你的推送渠道和数据源。

## 📦 模块说明

| 模块 | 方法 | 数据源 |
|------|------|--------|
| **百度热搜** | Playwright 浏览器 + JS 提取 | `top.baidu.com` |
| **微博热搜** | 内部 API 直调 | `m.weibo.cn` |
| **雪球热榜** | Playwright 浏览器 + table 遍历 | `xueqiu.com` |
| **A股行情** | 东方财富 API + 新浪财经 | `push2.eastmoney.com` |
| **融资融券** | Playwright 浏览器表格提取 | `data.eastmoney.com` |

## 🤝 贡献

欢迎通过 Issue 提交需求建议，或通过 Pull Request 贡献代码！

- 新数据源建议（抖音/B站/知乎热搜）
- 新增推送渠道（钉钉/飞书/企业微信）
- 优化提取策略（页面改版适配）

## 📄 License

[MIT](LICENSE)

## ⭐ 支持

如果这个项目对你有帮助，欢迎 Star ⭐ 支持！