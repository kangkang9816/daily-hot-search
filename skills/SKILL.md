---
name: daily-hot-search
description: 每日热搜早报推送 — 通过 Playwright MCP 定时抓取百度热搜、微博热搜、雪球热榜三大平台数据，整理成精美推送消息通过微信发送。
version: 2.1.0
author: Hermes Agent
related_skills: [cronjob, nas-monitor, nas-security-scan]
---

# 每日热搜早报推送

## 概述

每天早上 7:30 自动抓取三大平台（百度、微博、雪球）的热搜数据，汇总后推送至微信。

## 数据来源

### 关键网络环境说明
本任务在 **UGREEN NAS** 上运行，有以下网络限制需要注意：

#### 通用故障应对策略（重要）

当所有 API 都失效时，**使用浏览器直接导航到网页并提取渲染后的文本**是最稳健的兜底方案：

```javascript
// 万能提取法 — 获取页面所有可见文本
browser_console({expression: "document.body.innerText"})

// 或分段获取某区域的文本
browser_console({expression: "document.body.innerText.substring(idx, idx+2000)"})
```

这种方法绕过一切 API 限制、登录墙、CORS 问题。适用于：
- 百度热搜：从页面文本逐段解析（索引 + 热搜指数 + 标题 + 标签）
- 东方财富行情：从页面文本中提取指数数据和两融数据
- 雪球：从弹窗覆盖的页面文本中提取数据

### 1. 百度热搜 Top 10
- URL: `https://top.baidu.com/board?tab=realtime`
- 方式：使用内置浏览器工具（`browser_navigate` + `browser_console`）提取。无需登录。
- **推荐提取策略 — CSS全量解析法**：
  ```javascript
  Array.from(document.querySelectorAll('.category-wrap__ILXoJ, [class*="category-wrap"]')).slice(0,15).map(el => {
    const link = el.querySelector('a[href*="baidu.com/s?wd="]');
    const title = link ? link.textContent.trim() : '';
    const allText = Array.from(el.querySelectorAll('*')).map(e => e.textContent.trim()).filter(Boolean).join(' | ');
    return {title, allText};
  })
  ```
  输出中 `allText` 包含完整的结构文本，可从中提取热搜指数（7位数字+空格+"热搜指数"）和标签（"热"、"沸"、"新"等）。
- **页面结构规律**：条目结构为 `排名号 → 7位数热搜指数 → 热搜指数(文字) → 标题+标签 → 描述文本`
- **备选策略 — 全量文本提取**：使用 `document.body.innerText` 获取全页文本，按换行符分割后逐行解析。

### 2. 微博热搜 Top 10 ✅（推荐方案 — 网页版直接提取）

- URL: `https://weibo.com/newlogin?tabtype=search&gid=&openLoginLayer=0&url=`
- 方式：使用 `browser_navigate` 导航到微博网页版热搜页，**无需登录**即可看到热搜榜单
- 提取方法：页面渲染后直接使用 `browser_snapshot` 查看页面结构，热搜条目以链接形式显示
- **推荐提取 JS**：
  ```javascript
  // 从 weibo.com/newlogin 页面提取热搜 Top 10
  Array.from(document.querySelectorAll('a[href*="//s.weibo.com/weibo"]')).slice(0, 50).map(el => {
    const text = el.textContent.trim();
    const match = text.match(/^(\d+)([\s\S]*?)(\d+)$/);
    if (match) {
      return {
        rank: parseInt(match[1]),
        title: match[2].trim(),
        hot: match[3]
      };
    }
    return null;
  }).filter(Boolean).slice(0, 10)
  ```
- **为什么这个方案可行**：`weibo.com/newlogin?tabtype=search` 是微博的公开热搜页面，不需要登录态
- **已失效的方案**：`m.weibo.cn/api/container/getIndex`（HTTP 432/访客验证）、`weibo.com/ajax/side/hotSearch`（403）、微博账号密码登录（极验行为验证码弹窗，无法自动绕过）

### 3. 雪球数据
#### 3a. 热股榜（无需登录）
- URL: `https://xueqiu.com/hq`
- 方式：内置浏览器 `browser_navigate` 导航到 `/hq` 页面，无需登录即可访问
- 提取方法：使用 `browser_snapshot` 查看页面结构，找到 "热股榜" 区域
- 注意：默认显示"全球"标签，页面还有 "市场一览" 板块显示主要指数行情

#### 3b. 热门话题（需要登录，但有绕过方法）
- 雪球主页 `https://xueqiu.com/` 有登录弹窗覆盖整个页面
- **绕过方法**：使用 `browser_console` 执行 JS 隐藏登录弹窗
- 或者直接使用 `browser_console({expression: "document.body.innerText"})` 提取全页文本

### 4. A股成交量和融资融券数据
#### 4a. 指数行情数据（推荐方案 — 新浪财经 API）
- URL: `https://hq.sinajs.cn/list=sh000001,sz399001`
- 方式：`curl` 或 `mcp_fetch_fetch_txt` 获取，需要设置 `Referer: https://finance.sina.com.cn/`
- 返回格式：`var hq_str_sh000001="上证指数,开盘价,昨收价,当前价,最高价,最低价,0,0,成交量(手),成交额(元),..."`
- 两市合计成交额 = 上证成交额 + 深证成交额，需要将元转换为亿（除以 10^8）
- 注意：返回数据编码为 GBK，需用 `iconv -f gbk -t utf-8` 转换

#### 4b. 融资融券数据
- **推荐方案 — 东方财富数据中心 API**
- API URL: `https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_RZRQ_LSHJ&columns=ALL&pageNumber=1&pageSize=3&sortTypes=-1&sortColumns=DIM_DATE&source=WEB`
- 方式：`curl` 获取（设置 `Referer: https://data.eastmoney.com/rzrq/total.html`）
- 返回字段：`DIM_DATE`(交易日)、`RZYE`(融资余额/元)、`RQYE`(融券余额/元)、`RZRQYE`(两融合计)、`RZMRE`(融资买入额)、`RZCHE`(融资偿还额)、`RZJME`(融资净买入)、`RZYEZB`(余额占比)
- 单位转换：元 → 亿（除以 100,000,000）
- 注意：融资融券数据 T+1 公布

## Cron 任务设置

使用 `cronjob` 工具的 `create` 动作，设置：
- `schedule`: `"30 7 * * *"`（每天早上 7:30）
- `deliver`: 自动发送到当前聊天（微信）
- `skills`: `["daily-hot-search"]`（**只加载本技能即可**，不要同时加载 native-mcp）
- `prompt`: 包含完整任务说明的 prompt

**重要：SKILLS 只加载 daily-hot-search 一个技能！** 之前曾同时加载 `native-mcp` 和 `daily-hot-search` 两个技能，导致 cron 执行时只输出了 native-mcp 的技能文档就结束会话，完全没有执行热搜抓取流程。浏览器工具（`browser_navigate`, `browser_console` 等）和 mcp_fetch 工具在 cron 会话中默认可用，不需要额外加载 native-mcp。

**重要：cron 任务运行在无用户交互的环境中。** 最终输出会由系统自动投递。不要使用 `send_message`，只需在返回文本中包含报告内容即可。

**重要：GitHub 仓库多文件同步** — 本技能对应的 GitHub 仓库 `kangkang9816/daily-hot-search` 包含 `main.py`、`config.yaml`、`README.md` 等多个文件。更新技能文档后，需要同步更新仓库中对应的文件（README 的模块说明、config.yaml 的数据源URL等），不能只推送 skills/SKILL.md。

## 注意事项

- 如果某个平台抓取失败，标注 "获取失败" 并继续其他平台
- 日期使用系统当前时间获取
- cron 任务中 **不要使用 `send_message`** — 系统自动投递最终回复
- 雪球页面有登录弹窗，但 snapshot 可穿透获取底层数据
- **微博热搜已修复** — 改用 `weibo.com/newlogin?tabtype=search` 网页版公开页面提取，无需登录、无需 Cookie
- **Cron 任务技能配置陷阱** — 只加载 `daily-hot-search` 一个技能即可
- **NAS 容器网络限制**：curl 和 MCP fetch 可能无法访问部分外部 API，但 Playwright 浏览器可以正常访问
- **周末交易日处理**：周六/周日A股无交易，需要在报告中明确标注数据日期