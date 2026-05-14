import json
import os
from openai import OpenAI

CLASSIFY_PROMPT = """你是一個郵件分類助手。分析以下郵件，回傳 JSON 格式結果。

郵件資訊：
- 帳號：{account}
- 寄件人：{sender}
- 主旨：{subject}
- 內容：{body}
- 日期：{date}

請回傳以下格式的 JSON（只回傳純 JSON，不要 markdown 或其他文字）：
{{
  "category": "重要 | 待處理 | 一般",
  "summary": "一句話摘要（15字以內）",
  "action": "需回覆 | 待閱讀 | 可忽略",
  "reply_template": "規則名稱字串（若無適用規則則填 null，JSON null 不是字串）"
}}

分類標準：
- 重要：需要你本人處理或回覆的信；銀行或信用卡的刷卡通知、帳單、繳費通知；保險公司的保單通知、繳費提醒、理賠相關通知
- 待處理：需要稍後閱讀，但不緊急
- 一般：電子報、促銷信、一般行銷通知等可忽略的信"""


def _extract_json(raw: str) -> str:
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    return raw


def classify_email(email: dict, model: str = "gpt-4o-mini") -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("環境變數 OPENAI_API_KEY 未設置")

    client = OpenAI(api_key=api_key)

    prompt = CLASSIFY_PROMPT.format(
        account=email.get("account", ""),
        sender=email.get("sender", ""),
        subject=email.get("subject", ""),
        body=email.get("body", "")[:1000],
        date=email.get("date", "")
    )

    response = client.chat.completions.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    raw = _extract_json(raw)
    return json.loads(raw)
