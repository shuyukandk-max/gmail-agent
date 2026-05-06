# Gmail 自動化代理人 — 設計規格

**日期：** 2026-05-04
**狀態：** 待實作

---

## 目標

每天早上 9 點自動讀取 2-3 個 Gmail 帳號的新郵件，透過 Claude AI 分類摘要，對符合規則的郵件自動回覆，並將整理結果以分類摘要的形式推播到 LINE。

---

## 系統架構

```
每天 9:00 AM（cron / Claude Code /schedule）
    ↓
main.py
    ↓
gmail_fetcher.py     ← 讀取所有帳號昨日新郵件
    ↓
ai_classifier.py     ← Claude API 分析每封信
    ↓
    ├→ auto_reply.py  ← 符合 rules.yaml 規則 → 自動回覆
    └→ line_notifier.py ← 推播分類摘要到 LINE
```

---

## 元件說明

### `gmail_fetcher.py`
- 透過 Gmail API（OAuth 2.0）連接多個帳號
- 抓取前一天（昨日 00:00–23:59）收到的郵件
- 回傳結構化清單：`[{account, sender, subject, body, date}]`

### `ai_classifier.py`
- 呼叫 Claude API（claude-sonnet-4-6）
- 每封信輸出 JSON：
  ```json
  {
    "category": "重要 | 待處理 | 一般",
    "summary": "一句話摘要",
    "action": "需回覆 | 待閱讀 | 可忽略",
    "reply_template": "template_name | null"
  }
  ```
- Prompt 包含帳號情境說明，讓分類更準確

### `auto_reply.py`
- 讀取 `rules.yaml`，對照每封信的寄件人、主旨關鍵字
- 符合規則 → 用對應模板產生回覆 → 透過 Gmail API 傳送
- 不符合規則 → 跳過

### `line_notifier.py`
- 使用 LINE Messaging API（Push Message）
- 格式化通知：
  ```
  📬 每日郵件摘要 YYYY-MM-DD

  🔴 重要（N 封）
  ・[帳號] 寄件人：摘要

  🟡 待處理（N 封）
  ・[帳號] 寄件人：摘要

  ⚪ 一般（N 封）
  ・已歸檔/忽略
  ```

---

## 設定檔

### `config.yaml`
```yaml
gmail_accounts:
  - email: account1@gmail.com
    token_file: tokens/token1.json
  - email: account2@gmail.com
    token_file: tokens/token2.json

line:
  channel_access_token: "LINE_BOT_TOKEN"
  user_id: "LINE_USER_ID"

claude:
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY

schedule:
  time: "09:00"
  timezone: "Asia/Taipei"
```

### `rules.yaml`
```yaml
rules:
  - name: 客戶詢問信
    match:
      subject_keywords: ["詢問", "報價", "合作", "諮詢"]
    action: reply
    template: |
      感謝您的來信！
      我們已收到您的詢問，將於 1-2 個工作天內回覆。
      如有急事請直接來電，謝謝。

  - name: 訂單通知
    match:
      from_domain: ["shopee.com", "momo.com", "pchome.com.tw"]
    action: archive

  - name: 電子報
    match:
      subject_keywords: ["unsubscribe", "取消訂閱", "電子報"]
    action: ignore
```

---

## 目錄結構

```
gmail-agent/
├── config.yaml
├── rules.yaml
├── credentials.json       ← Google OAuth（加入 .gitignore）
├── tokens/                ← 各帳號授權 token（加入 .gitignore）
│   ├── token1.json
│   └── token2.json
├── gmail_fetcher.py
├── ai_classifier.py
├── auto_reply.py
├── line_notifier.py
├── main.py
├── requirements.txt
└── .gitignore
```

---

## 前置作業

### Gmail OAuth
1. Google Cloud Console → 建立專案 → 啟用 Gmail API
2. 建立 OAuth 2.0 憑證（桌面應用程式）→ 下載 `credentials.json`
3. 首次執行 `main.py` → 瀏覽器授權各帳號 → 產生 `tokens/tokenN.json`

### LINE Messaging API
1. LINE Developers → 建立 Messaging API Channel
2. 取得 Channel Access Token → 填入 `config.yaml`
3. 加 Bot 好友 → 取得 User ID → 填入 `config.yaml`

### 環境變數
```bash
export ANTHROPIC_API_KEY="your_key"
```

---

## 排程設定

使用 Claude Code `/schedule` 或系統 cron：

```bash
# cron（每天早上 9 點）
0 9 * * * cd /path/to/gmail-agent && python main.py
```

---

## 不在範圍內

- 附件解析
- 多語言回覆模板
- 網頁管理介面
- 郵件行程自動加入 Calendar
