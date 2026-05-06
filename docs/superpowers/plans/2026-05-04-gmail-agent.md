# Gmail 自動化代理人 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 每天早上 9 點自動讀取 2-3 個 Gmail 帳號郵件，AI 分類摘要，自動回覆符合規則的信件，並推播分類摘要到 LINE。

**Architecture:** Python 腳本由 cron 每天 9 點觸發，依序執行：Gmail 讀取 → Claude 分類 → 自動回覆 → LINE 通知。各元件獨立模組，透過 main.py 串接，設定集中在 config.yaml / rules.yaml。

**Tech Stack:** Python 3.11+, google-auth / google-api-python-client, anthropic SDK, requests (LINE API), PyYAML, pytest, pytest-mock

---

## 檔案結構

| 檔案 | 職責 |
|------|------|
| `gmail-agent/main.py` | 主程式，依序呼叫各模組 |
| `gmail-agent/gmail_fetcher.py` | OAuth 連線、讀取多帳號昨日郵件 |
| `gmail-agent/ai_classifier.py` | 呼叫 Claude API，回傳分類 JSON |
| `gmail-agent/auto_reply.py` | 比對 rules.yaml，發送自動回覆 |
| `gmail-agent/line_notifier.py` | 格式化並推播 LINE 訊息 |
| `gmail-agent/config.yaml` | 帳號、token、排程設定（模板） |
| `gmail-agent/rules.yaml` | 自動回覆規則與模板 |
| `gmail-agent/requirements.txt` | Python 相依套件 |
| `gmail-agent/.gitignore` | 排除憑證與 token |
| `gmail-agent/tests/test_classifier.py` | ai_classifier 單元測試 |
| `gmail-agent/tests/test_auto_reply.py` | auto_reply 單元測試 |
| `gmail-agent/tests/test_line_notifier.py` | line_notifier 單元測試 |

---

### Task 1：建立專案結構與設定檔

**Files:**
- Create: `gmail-agent/requirements.txt`
- Create: `gmail-agent/.gitignore`
- Create: `gmail-agent/config.yaml`
- Create: `gmail-agent/rules.yaml`
- Create: `gmail-agent/tokens/.gitkeep`
- Create: `gmail-agent/tests/__init__.py`

- [ ] **Step 1: 建立目錄**

```bash
mkdir -p /Users/demi/Desktop/demi-agent/gmail-agent/tokens
mkdir -p /Users/demi/Desktop/demi-agent/gmail-agent/tests
```

- [ ] **Step 2: 建立 requirements.txt**

```
google-auth==2.29.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.127.0
anthropic==0.28.0
requests==2.31.0
PyYAML==6.0.1
pytest==8.2.0
pytest-mock==3.14.0
```

- [ ] **Step 3: 建立 .gitignore**

```
credentials.json
tokens/
*.json
__pycache__/
.env
```

- [ ] **Step 4: 建立 config.yaml（模板）**

```yaml
gmail_accounts:
  - email: ACCOUNT1@gmail.com
    token_file: tokens/token1.json
  - email: ACCOUNT2@gmail.com
    token_file: tokens/token2.json

line:
  channel_access_token: "YOUR_LINE_CHANNEL_ACCESS_TOKEN"
  user_id: "YOUR_LINE_USER_ID"

claude:
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY

schedule:
  time: "09:00"
  timezone: "Asia/Taipei"
```

- [ ] **Step 5: 建立 rules.yaml**

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

- [ ] **Step 6: 建立 tests/__init__.py**

```python
```

- [ ] **Step 7: 安裝相依套件**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
pip install -r requirements.txt
```

Expected: 所有套件安裝成功，無 error。

- [ ] **Step 8: Commit**

```bash
cd /Users/demi/Desktop/demi-agent
git add gmail-agent/
git commit -m "feat: scaffold gmail-agent project structure"
```

---

### Task 2：實作 ai_classifier.py

**Files:**
- Create: `gmail-agent/ai_classifier.py`
- Create: `gmail-agent/tests/test_classifier.py`

- [ ] **Step 1: 寫失敗測試**

建立 `gmail-agent/tests/test_classifier.py`：

```python
import pytest
from unittest.mock import MagicMock, patch
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ai_classifier import classify_email

FAKE_EMAIL = {
    "account": "work@gmail.com",
    "sender": "client@example.com",
    "subject": "合作詢問",
    "body": "您好，想詢問合作事宜。",
    "date": "2026-05-03"
}

FAKE_RESPONSE_JSON = '''{
  "category": "重要",
  "summary": "客戶詢問合作事宜",
  "action": "需回覆",
  "reply_template": "客戶詢問信"
}'''

def test_classify_email_returns_dict(mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=FAKE_RESPONSE_JSON)]
    )
    mocker.patch('ai_classifier.anthropic.Anthropic', return_value=mock_client)

    result = classify_email(FAKE_EMAIL, model="claude-sonnet-4-6")

    assert result["category"] == "重要"
    assert result["summary"] == "客戶詢問合作事宜"
    assert result["action"] == "需回覆"
    assert result["reply_template"] == "客戶詢問信"

def test_classify_email_general(mocker):
    general_json = '''{
      "category": "一般",
      "summary": "促銷電子報",
      "action": "可忽略",
      "reply_template": null
    }'''
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=general_json)]
    )
    mocker.patch('ai_classifier.anthropic.Anthropic', return_value=mock_client)

    email = {**FAKE_EMAIL, "subject": "本週特賣優惠", "body": "點此取消訂閱"}
    result = classify_email(email, model="claude-sonnet-4-6")

    assert result["category"] == "一般"
    assert result["reply_template"] is None
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
pytest tests/test_classifier.py -v
```

Expected: `ModuleNotFoundError: No module named 'ai_classifier'`

- [ ] **Step 3: 實作 ai_classifier.py**

建立 `gmail-agent/ai_classifier.py`：

```python
import json
import os
import anthropic

CLASSIFY_PROMPT = """你是一個郵件分類助手。分析以下郵件，回傳 JSON 格式結果。

郵件資訊：
- 帳號：{account}
- 寄件人：{sender}
- 主旨：{subject}
- 內容：{body}
- 日期：{date}

請回傳以下格式的 JSON（只回傳 JSON，不要其他文字）：
{{
  "category": "重要 | 待處理 | 一般",
  "summary": "一句話摘要（15字以內）",
  "action": "需回覆 | 待閱讀 | 可忽略",
  "reply_template": "規則名稱字串 或 null"
}}

分類標準：
- 重要：需要你本人處理或回覆的信
- 待處理：需要稍後閱讀，但不緊急
- 一般：電子報、通知信、促銷信等可忽略的信"""


def classify_email(email: dict, model: str = "claude-sonnet-4-6") -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    prompt = CLASSIFY_PROMPT.format(
        account=email.get("account", ""),
        sender=email.get("sender", ""),
        subject=email.get("subject", ""),
        body=email.get("body", "")[:500],
        date=email.get("date", "")
    )

    response = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    return json.loads(raw)
```

- [ ] **Step 4: 跑測試確認通過**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
pytest tests/test_classifier.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
cd /Users/demi/Desktop/demi-agent
git add gmail-agent/ai_classifier.py gmail-agent/tests/test_classifier.py
git commit -m "feat: add ai_classifier with Claude API integration"
```

---

### Task 3：實作 auto_reply.py

**Files:**
- Create: `gmail-agent/auto_reply.py`
- Create: `gmail-agent/tests/test_auto_reply.py`

- [ ] **Step 1: 寫失敗測試**

建立 `gmail-agent/tests/test_auto_reply.py`：

```python
import pytest
from unittest.mock import MagicMock, patch, call
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from auto_reply import should_reply, send_reply, load_rules

RULES = [
    {
        "name": "客戶詢問信",
        "match": {"subject_keywords": ["詢問", "報價"]},
        "action": "reply",
        "template": "感謝您的來信，我們將盡快回覆。"
    },
    {
        "name": "訂單通知",
        "match": {"from_domain": ["shopee.com"]},
        "action": "archive"
    }
]

def test_should_reply_matches_subject_keyword():
    email = {"subject": "合作報價詢問", "sender": "client@example.com"}
    rule = should_reply(email, RULES)
    assert rule is not None
    assert rule["name"] == "客戶詢問信"

def test_should_reply_matches_from_domain():
    email = {"subject": "您的訂單已出貨", "sender": "noreply@shopee.com"}
    rule = should_reply(email, RULES)
    assert rule is not None
    assert rule["name"] == "訂單通知"

def test_should_reply_no_match():
    email = {"subject": "Hello", "sender": "friend@gmail.com"}
    rule = should_reply(email, RULES)
    assert rule is None

def test_send_reply_calls_gmail_api(mocker):
    mock_service = MagicMock()
    mock_service.users().messages().send().execute.return_value = {"id": "msg123"}

    email = {
        "account": "work@gmail.com",
        "sender": "client@example.com",
        "subject": "報價詢問",
        "message_id": "abc123"
    }
    template = "感謝您的來信，我們將盡快回覆。"

    result = send_reply(mock_service, email, template)
    assert result is True
    mock_service.users().messages().send.assert_called()
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
pytest tests/test_auto_reply.py -v
```

Expected: `ModuleNotFoundError: No module named 'auto_reply'`

- [ ] **Step 3: 實作 auto_reply.py**

建立 `gmail-agent/auto_reply.py`：

```python
import base64
import email as email_lib
from email.mime.text import MIMEText
from typing import Optional


def load_rules(rules_path: str = "rules.yaml") -> list:
    import yaml
    with open(rules_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])


def should_reply(email: dict, rules: list) -> Optional[dict]:
    subject = email.get("subject", "").lower()
    sender = email.get("sender", "").lower()

    for rule in rules:
        match = rule.get("match", {})

        keywords = match.get("subject_keywords", [])
        if any(kw.lower() in subject for kw in keywords):
            return rule

        domains = match.get("from_domain", [])
        if any(domain.lower() in sender for domain in domains):
            return rule

    return None


def send_reply(service, email: dict, template: str) -> bool:
    account = email.get("account", "me")
    to = email.get("sender", "")
    subject = "Re: " + email.get("subject", "")

    msg = MIMEText(template, "plain", "utf-8")
    msg["To"] = to
    msg["Subject"] = subject
    msg["In-Reply-To"] = email.get("message_id", "")
    msg["References"] = email.get("message_id", "")

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {"raw": raw, "threadId": email.get("thread_id", "")}

    service.users().messages().send(userId="me", body=body).execute()
    return True
```

- [ ] **Step 4: 跑測試確認通過**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
pytest tests/test_auto_reply.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
cd /Users/demi/Desktop/demi-agent
git add gmail-agent/auto_reply.py gmail-agent/tests/test_auto_reply.py
git commit -m "feat: add auto_reply engine with rules.yaml matching"
```

---

### Task 4：實作 line_notifier.py

**Files:**
- Create: `gmail-agent/line_notifier.py`
- Create: `gmail-agent/tests/test_line_notifier.py`

- [ ] **Step 1: 寫失敗測試**

建立 `gmail-agent/tests/test_line_notifier.py`：

```python
import pytest
from unittest.mock import MagicMock, patch
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from line_notifier import format_summary, send_line_message

CLASSIFIED_EMAILS = [
    {
        "account": "work@gmail.com",
        "sender": "王小明 <client@example.com>",
        "subject": "合作詢問",
        "category": "重要",
        "summary": "客戶詢問合作事宜",
        "action": "需回覆"
    },
    {
        "account": "personal@gmail.com",
        "sender": "noreply@shopee.com",
        "subject": "訂單已出貨",
        "category": "一般",
        "summary": "訂單出貨通知",
        "action": "可忽略"
    },
    {
        "account": "work@gmail.com",
        "sender": "vendor@company.com",
        "subject": "報價單",
        "category": "待處理",
        "summary": "廠商報價單待確認",
        "action": "待閱讀"
    }
]

def test_format_summary_contains_sections():
    msg = format_summary(CLASSIFIED_EMAILS, date="2026-05-04")
    assert "📬 每日郵件摘要 2026-05-04" in msg
    assert "🔴 重要" in msg
    assert "🟡 待處理" in msg
    assert "⚪ 一般" in msg

def test_format_summary_counts_correct():
    msg = format_summary(CLASSIFIED_EMAILS, date="2026-05-04")
    assert "重要（1 封）" in msg
    assert "待處理（1 封）" in msg
    assert "一般（1 封）" in msg

def test_send_line_message_calls_api(mocker):
    mock_post = mocker.patch('line_notifier.requests.post')
    mock_post.return_value = MagicMock(status_code=200)

    result = send_line_message(
        token="fake_token",
        user_id="fake_user",
        message="Test message"
    )

    assert result is True
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "fake_token" in str(call_kwargs)
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
pytest tests/test_line_notifier.py -v
```

Expected: `ModuleNotFoundError: No module named 'line_notifier'`

- [ ] **Step 3: 實作 line_notifier.py**

建立 `gmail-agent/line_notifier.py`：

```python
import requests
from datetime import date as date_type


def format_summary(emails: list, date: str = None) -> str:
    if date is None:
        date = str(date_type.today())

    important = [e for e in emails if e.get("category") == "重要"]
    pending = [e for e in emails if e.get("category") == "待處理"]
    general = [e for e in emails if e.get("category") == "一般"]

    lines = [f"📬 每日郵件摘要 {date}", ""]

    lines.append(f"🔴 重要（{len(important)} 封）")
    if important:
        for e in important:
            account = e.get("account", "")
            sender = e.get("sender", "").split("<")[0].strip()
            summary = e.get("summary", "")
            lines.append(f"・[{account}] {sender}：{summary}")
    else:
        lines.append("・無")

    lines.append("")
    lines.append(f"🟡 待處理（{len(pending)} 封）")
    if pending:
        for e in pending:
            account = e.get("account", "")
            sender = e.get("sender", "").split("<")[0].strip()
            summary = e.get("summary", "")
            lines.append(f"・[{account}] {sender}：{summary}")
    else:
        lines.append("・無")

    lines.append("")
    lines.append(f"⚪ 一般（{len(general)} 封）")
    if general:
        for e in general:
            summary = e.get("summary", "")
            lines.append(f"・{summary}")
    else:
        lines.append("・無")

    return "\n".join(lines)


def send_line_message(token: str, user_id: str, message: str) -> bool:
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.status_code == 200
```

- [ ] **Step 4: 跑測試確認通過**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
pytest tests/test_line_notifier.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
cd /Users/demi/Desktop/demi-agent
git add gmail-agent/line_notifier.py gmail-agent/tests/test_line_notifier.py
git commit -m "feat: add line_notifier with categorized summary format"
```

---

### Task 5：實作 gmail_fetcher.py

**Files:**
- Create: `gmail-agent/gmail_fetcher.py`

> 注意：gmail_fetcher 依賴 Google OAuth，測試需要 mock，功能驗證在 Task 6 整合測試時進行。

- [ ] **Step 1: 實作 gmail_fetcher.py**

建立 `gmail-agent/gmail_fetcher.py`：

```python
import os
import base64
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]


def get_gmail_service(token_file: str, credentials_file: str = "credentials.json"):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_yesterday_emails(service, account_email: str) -> list:
    yesterday = datetime.now() - timedelta(days=1)
    after = yesterday.strftime("%Y/%m/%d")
    today = datetime.now().strftime("%Y/%m/%d")
    query = f"after:{after} before:{today}"

    result = service.users().messages().list(userId="me", q=query).execute()
    messages = result.get("messages", [])

    emails = []
    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        subject = headers.get("Subject", "(無主旨)")
        sender = headers.get("From", "")
        date_str = headers.get("Date", "")
        message_id = headers.get("Message-ID", "")
        thread_id = msg.get("threadId", "")

        body = ""
        payload = msg.get("payload", {})
        if payload.get("body", {}).get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        elif payload.get("parts"):
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                    break

        emails.append({
            "account": account_email,
            "sender": sender,
            "subject": subject,
            "body": body[:1000],
            "date": date_str,
            "message_id": message_id,
            "thread_id": thread_id,
            "gmail_service": service
        })

    return emails


def fetch_all_accounts(accounts: list, credentials_file: str = "credentials.json") -> list:
    all_emails = []
    for account in accounts:
        service = get_gmail_service(account["token_file"], credentials_file)
        emails = fetch_yesterday_emails(service, account["email"])
        all_emails.extend(emails)
    return all_emails
```

- [ ] **Step 2: Commit**

```bash
cd /Users/demi/Desktop/demi-agent
git add gmail-agent/gmail_fetcher.py
git commit -m "feat: add gmail_fetcher with OAuth multi-account support"
```

---

### Task 6：實作 main.py

**Files:**
- Create: `gmail-agent/main.py`

- [ ] **Step 1: 實作 main.py**

建立 `gmail-agent/main.py`：

```python
import yaml
import os
from datetime import date
from gmail_fetcher import fetch_all_accounts
from ai_classifier import classify_email
from auto_reply import load_rules, should_reply, send_reply
from line_notifier import format_summary, send_line_message


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    rules = load_rules("rules.yaml")

    print("📥 正在讀取郵件...")
    all_emails = fetch_all_accounts(
        config["gmail_accounts"],
        credentials_file="credentials.json"
    )
    print(f"   共讀取 {len(all_emails)} 封郵件")

    model = config["claude"]["model"]
    classified = []

    print("🤖 正在分析郵件...")
    for email in all_emails:
        result = classify_email(email, model=model)
        enriched = {**email, **result}
        classified.append(enriched)

        rule = should_reply(email, rules)
        if rule and rule.get("action") == "reply":
            service = email.get("gmail_service")
            if service:
                send_reply(service, email, rule["template"])
                print(f"   ✉️  已自動回覆：{email['subject']}")

    print("📲 正在發送 LINE 通知...")
    today = str(date.today())
    message = format_summary(classified, date=today)

    line_cfg = config["line"]
    success = send_line_message(
        token=line_cfg["channel_access_token"],
        user_id=line_cfg["user_id"],
        message=message
    )

    if success:
        print("✅ LINE 通知發送成功")
    else:
        print("❌ LINE 通知發送失敗，請確認 token 和 user_id")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
cd /Users/demi/Desktop/demi-agent
git add gmail-agent/main.py
git commit -m "feat: add main.py orchestrator"
```

---

### Task 7：設定 cron 排程

**Files:**
- Modify: 系統 crontab

- [ ] **Step 1: 確認 Python 路徑**

```bash
which python3
```

記下輸出路徑，例如 `/usr/bin/python3` 或 `/opt/homebrew/bin/python3`。

- [ ] **Step 2: 新增 cron job**

```bash
crontab -e
```

在編輯器中加入這行（將 `PYTHON_PATH` 替換為上一步的路徑）：

```
0 9 * * * cd /Users/demi/Desktop/demi-agent/gmail-agent && ANTHROPIC_API_KEY=你的金鑰 PYTHON_PATH main.py >> /tmp/gmail-agent.log 2>&1
```

例如：

```
0 9 * * * cd /Users/demi/Desktop/demi-agent/gmail-agent && ANTHROPIC_API_KEY=sk-ant-xxx /opt/homebrew/bin/python3 main.py >> /tmp/gmail-agent.log 2>&1
```

- [ ] **Step 3: 確認 cron 已設定**

```bash
crontab -l
```

Expected: 看到剛才新增的那行。

- [ ] **Step 4: 手動測試執行（填好 config.yaml 後）**

```bash
cd /Users/demi/Desktop/demi-agent/gmail-agent
python3 main.py
```

Expected:
```
📥 正在讀取郵件...
   共讀取 N 封郵件
🤖 正在分析郵件...
📲 正在發送 LINE 通知...
✅ LINE 通知發送成功
```

---

## 完成後的驗收清單

- [ ] `pytest tests/` 全部通過
- [ ] `config.yaml` 填入真實帳號、LINE token、user_id
- [ ] `credentials.json` 已放入目錄
- [ ] 首次執行時完成各帳號的瀏覽器授權
- [ ] 手動執行 `python3 main.py` 成功收到 LINE 通知
- [ ] crontab 已設定，明早 9 點自動執行
