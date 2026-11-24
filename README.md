# Daily Report Bot

每天早上自动发一封「东南亚游戏社媒热点趋势」早报邮件，给射击手游的社媒运营做选题参考。

## 流程

1. 抓取素材：Reddit 相关板块的周热帖、Google News 上的游戏热点，以及 YouTube Shorts 上的玩法、搞笑和剪辑类参考视频。
2. 生成内容：把抓到的情报交给 Gemini，按固定结构写出三条热点趋势拆解、竞品与行业动态和一段爆款脚本建议，并约束它不写体育术语、不输出表格。
3. 发送邮件：把结果转成 HTML，附上参考视频的缩略图墙，通过 SMTP 发给收件人列表。

整个脚本由 GitHub Actions 每天定时运行，北京时间 06:23，也可以在 Actions 页面手动触发。

## 配置

在仓库 Settings → Secrets and variables → Actions 里添加：

| Secret | 用途 |
| --- | --- |
| `GEMINI_API_KEY` | Gemini API 密钥 |
| `MAIL_USER` | 发件邮箱，当前使用 QQ 邮箱 SMTP |
| `MAIL_PASS` | 发件邮箱的 SMTP 授权码 |
| `MAIL_TO` | 收件人，多个用英文逗号分隔 |

配置好后在 Actions 页面启用 `Daily Email Bot` 工作流。

## 本地运行

```bash
pip install requests markdown feedparser beautifulsoup4 lxml youtube-search-python
export GEMINI_API_KEY=... MAIL_USER=... MAIL_PASS=... MAIL_TO=...
python cloud_bot.py
```

## 技术栈

Python、Gemini API、requests、BeautifulSoup、feedparser、GitHub Actions
