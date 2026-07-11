# Daily Hot Search — Hermes Agent Skill

本目录包含 Hermes Agent 的 skill 定义，可直接在 Hermes Agent 中加载使用。

## 使用方式

### 方式一：通过 cronjob 加载

在 Hermes Agent 中执行：

```
cronjob create \
  schedule="30 7 * * *" \
  prompt="完整的每日热搜早报抓取和推送任务" \
  skills="[\"native-mcp\", \"daily-hot-search\"]"
```

### 方式二：直接复制 skill 到你的 Hermes Agent

将 `skills/daily-hot-search/` 目录复制到你的 Hermes Agent 的 `skills/` 目录下。

## skill 内容说明

该 skill 包含了：
- 百度热搜 Playwright JS 提取策略
- 微博热搜内部 API 提取策略
- 雪球热榜 table 遍历策略
- A股行情和融资融券数据提取策略
- 报告格式化模板
