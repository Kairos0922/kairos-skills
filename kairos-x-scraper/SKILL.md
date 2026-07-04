---
name: kairos-x-scraper
description: |
  抓取 X.com（Twitter）任意公开账号的推文。触发词："抓取推文"、"抓X"、"爬twitter"、"fetch tweets"、"抓他的推文"、"抓一下XXX的X"、提到 X/Twitter 账号想抓取其内容。当用户想获取某个账号的推文数据用于分析时加载。仅为一次性抓取任务设计，不适用于持续监控或定时抓取。
metadata:
  version: "1.0.0"
---

# kairos-x-scraper

抓取 X.com（Twitter）公开账号的推文，保存为结构化 JSONL 文件。

## 密钥配置

此 skill 需要 X.com 的认证信息。首次使用或密钥过期时，引导用户提供。配置保存在 `~/.kairos/kairos-x-scraper-config.json`。

### 引导用户获取 auth_token 和 ct0

1. 打开 https://x.com 并登录
2. 按 `F12` 打开开发者工具
3. 进入 **Application**（应用程序）标签
4. 左侧 **Cookies** → 点击 `https://x.com`
5. 在 Cookie 列表中找到 `auth_token` 和 `ct0`，分别复制其 **Value**
6. 粘贴给我

> 如需使 token 失效，去 X 设置中登出再重新登录即可。

---

## 流程

### Step 1：确认抓取信息

向用户确认以下三项，**缺一不可**：

| 信息 | 说明 | 默认值 |
|------|------|--------|
| **目标账号** | X 的 @handle（不用加 @） | 无，必须提供 |
| **时间范围** | 往前翻多久 | 1 个月 |
| **输出目录** | JSONL 文件保存位置 | 当前工作目录 |

必须展示确认摘要，等用户说"确认"或"开始"。

### Step 2：检查密钥

读取 `~/.kairos/kairos-x-scraper-config.json`：

- **存在** → 进入 Step 3
- **不存在** → 输出上面的获取教程，用户提供后写入配置文件，进入 Step 3

配置文件格式：
```json
{
  "auth_token": "用户提供的值",
  "ct0": "用户提供的值"
}
```

### Step 3：执行抓取

运行脚本，三个参数：

```bash
python3 scripts/fetch_tweets.py <handle> <月数> <输出目录>
```

示例：
```bash
python3 /path/to/kairos-x-scraper/scripts/fetch_tweets.py aleabitoreddit 1 /Users/xxx/Documents
```

### Step 4：处理结果

- **成功** → 告知用户：推文数、日期范围、文件路径、TOP 20 股票代码提及
- **401** → "auth_token 已过期"，回到获取教程，更新配置文件后重试
- **429** → 脚本会自动等待 60 秒后重试，告知用户耐心等候
- **404 / query not found** → GraphQL ID 过期（X 每几周换一次），告诉用户："X 的内部 API 已更新，需要手动获取新的 query ID。打开 X → F12 → Network → 搜索 UserByScreenName → 复制 /graphql/ 后面的 ID 告诉我。" 拿到后传给脚本 `--user-query-id` 和 `--tweets-query-id` 参数
- **其他错误** → 告知用户错误信息，不要猜测

### Step 5：安全提醒

抓取完成后提醒用户：

> 可以去 X 设置中退出登录再重新登录，使 auth_token 失效。

---

## 注意事项

- 此 skill 仅用于公开推文的获取，遵守 X 的服务条款
- 不要频繁抓取同一账号，避免触发风控
- 一般账号每月 ~200-500 条推文，约需 1-3 分钟
