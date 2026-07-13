---
name: daily-hot-search
description: 每日热搜早报推送 — 通过浏览器抓取百度/微博/雪球热搜+A股数据，整理推送至微信
version: 3.0.0
author: Hermes Agent
---

# 每日热搜早报推送

每天早上 7:30 自动抓取并推送。

## 已验证可用的完整数据链路

### 1. 百度热搜 Top 10
```
browser_navigate("https://top.baidu.com/board?tab=realtime")
browser_console({expression: "document.body.innerText.substring(document.body.innerText.indexOf('热搜榜'), document.body.innerText.indexOf('热搜榜')+3000)"})
```
页面结构规律：`热搜榜` → 置顶(无排名号) → 7位数热搜指数 → 标题 → 排名1 → 7位数指数 → 标题+标签(热/沸/新双空格分隔) → (循环)
标签在数字后的同一行用双空格隔开，如`"沈阳将在全市实行紧急避险措施  新"`

### 2. 微博热搜 Top 10
```
browser_navigate("https://weibo.com/newlogin?tabtype=search&gid=&openLoginLayer=0&url=")
browser_snapshot()
```
页面结构：热搜链接 `a[href*="//s.weibo.com/weibo"]`，紧跟text含标签+排名+热度值
格式：`link "标题"` + `text "热 939146 2"`（标签+空格+热度+空格+排名）

### 3. 雪球热股榜 Top 6
```
browser_navigate("https://xueqiu.com/hq")
browser_snapshot()
```
在"热股榜"区域找listitem，格式 `"1. 赛力斯 +1.58%"`
市场一览也在同一页面：上证/深证/创业板/科创50

### 4. A股行情数据
```
curl -s -H "Referer: https://finance.sina.com.cn/" "https://hq.sinajs.cn/list=sh000001,sz399001" | iconv -f gbk -t utf-8
```
返回：`var hq_str_sh000001="上证指数,开盘,昨收,当前,最高,最低,0,0,成交量(手),成交额(元),...日期,时间"`
字段索引：[0名称, 1开盘, 2昨收, 3当前价, 4最高, 5最低, 8成交量, 9成交额]
两市成交额=(上证成交额+深证成交额)/1e8亿

### 5. 融资融券数据
```
curl -s --max-time 10 -H "Referer: https://data.eastmoney.com/rzrq/total.html" "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_RZRQ_LSHJ&columns=ALL&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=DIM_DATE&source=WEB"
```
返回JSON字段：DIM_DATE(日期), RZYE(融资余额), RQYE(融券余额), RZRQYE(两融合计), RZMRE(融资买入额), RZJME(融资净买入), RZYEZB(占比%)
单位转换：元→亿/1e8

## Cron 任务设置

**关键原则：prompt 必须自包含，不要依赖AI阅读长skill文档再执行。** prompt直接给完整操作步骤。

```javascript
// cronjob 参数：
{
  schedule: "30 7 * * *",
  skills: ["daily-hot-search"],  // 只加载这一个技能
  prompt: "精简的完整操作指令（含URL和提取方法）",
  deliver: "origin"  // 自动推送到当前对话
}
```

## 推送消息模板

```
🔥 每日热搜早报 · YYYY年M月D日（周X）

━━━━━━━━━━━━━━━━━━━
📊 百度热搜 Top 10
━━━━━━━━━━━━━━━━━━━
| # | 热搜词 | 指数 | 标签 |
|:--:|------|------:|:----:|
| 🔴 | 置顶标题 | 7,xxx,xxx | |
| 1 | 标题 | 7,xxx,xxx | 热 |

━━━━━━━━━━━━━━━━━━━
📊 微博热搜 Top 10
━━━━━━━━━━━━━━━━━━━
| # | 热搜词 | 热度 | 标签 |
|:--:|------|:----:|:----:|

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

## 注意事项

- **skill文档过长导致静默失败**：SKILL.md超过300行时，cron中AI加载文档后上下文不足。cron的prompt必须自包含，直接写操作步骤和URL
- 每个平台失败则标注"获取失败"，不影响其他平台
- 周六/周日A股数据为上一个交易日，需标注
- 融资融券T+1公布，最新数据为前一个交易日
- 不要使用 `send_message`，系统自动投递最终回复
- 2026年7月验证：百度热搜用innerText提取最稳定（CSS类名会变），微博用`weibo.com/newlogin?tabtype=search`直接提取不用加url参数

## 小说下载记录
- 《边军：从领取罪女开始，一统天下》by 一宁会发光ogsun
- 下载源：思兔阅读 https://www.sto66.com/book/2amNRVOv9vCqWGHqOpCBut.html
- 共338章连载中，NAS路径：/volume1/Hermes/data/Hermes下载专用/电子书下载/边军：从领取罪女开始，一统天下.txt
- 已补缺第80章