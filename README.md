# 🔥 Daily Hot Search — 每日热搜早报

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 自动抓取百度热搜、微博热搜、雪球热榜、A股行情，每天定时推送早报到你的微信/Telegram等平台。

## ✨ 功能

- 📊 **百度热搜** Top 10 — 标题 + 热搜指数
- 🔥 **微博热搜** Top 10 ✅ — 标题 + 热度值（网页版公开提取，无需登录）
- 📈 **雪球热榜** — 热股榜 Top 6 + 市场一览
- 💹 **A股行情** — 上证指数 & 深证成指实时数据
- 💰 **融资融券** — 两融余额、净买入等指标
- ⏰ **定时推送** — 通过 Cron 每天 7:30 自动发送
- 📤 **多平台** — 微信、Telegram、Discord 等

## 🚀 快速开始

### 方式一：Hermes Agent（推荐）

如果你运行的是 Hermes Agent，直接用 cron 技能加载即可：

```bash
cronjob create \
  schedule="30 7 * * *" \
  prompt="抓取热搜并推送" \
  skills="[\"daily-hot-search\"]"
```

**注意：skills 只加载 `daily-hot-search` 一个即可**，浏览器工具默认可用，不要同时加载 `native-mcp`。

详情见 `skills/SKILL.md` 目录下的技能配置。

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
│   ├── xueqiu.py            # 雪球热榜爬取
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
| **百度热搜** | Playwright 浏览器 + CSS 提取 | `top.baidu.com` |
| **微博热搜** ✅ | 网页版公开页面提取（无需登录） | `weibo.com/newlogin?tabtype=search` |
| **雪球热榜** | Playwright 浏览器 + snapshot | `xueqiu.com/hq` |
| **A股行情** | 新浪财经 API | `hq.sinajs.cn` |
| **融资融券** | 东方财富数据中心 API | `datacenter-web.eastmoney.com` |

## ⚠️ 重要更新记录

### v2.0.0 (2026-07-12)
- **微博热搜已修复**：微博内部 API（m.weibo.cn）已全面添加访客验证（HTTP 432），`weibo.com/ajax/side/hotSearch` 返回 403，第三方 API 返回 502。
- **新方案**：改用 `weibo.com/newlogin?tabtype=search` 微博网页版公开热搜页面，**无需登录**即可通过浏览器提取热搜数据。
- **Cron 配置陷阱修复**：同时加载 `native-mcp` + `daily-hot-search` 两个技能会导致 cron 只输出技能文档不执行抓取，正确做法是只加载 `daily-hot-search` 一个。

## 🤝 贡献

欢迎通过 Issue 提交需求建议，或通过 Pull Request 贡献代码！

- 新数据源建议（抖音/B站/知乎热搜）
- 新增推送渠道（钉钉/飞书/企业微信）
- 优化提取策略（页面改版适配）

## 📄 License

[MIT](LICENSE)

## ⭐ 支持

如果这个项目对你有帮助，欢迎 Star ⭐ 支持！