import json
import os
from openai import OpenAI

# 各帳號的重要郵件定義
ACCOUNT_RULES = {
    "admin@lumiora.studio": (
        "【寄件人指定分類，優先於以下其他規則與通用規則】\n"
        "- 重要：Squarespace Ireland Limited 帳單通知（b2ceci@ecimail1.tradevan.com.tw）、"
        "Google Payments（payments-noreply@google.com）\n"
        "- 待處理：PayPal（service@intl.paypal.com）、Squarespace 通知（no-reply@squarespace.com）\n"
        "- 一般：Squarespace 電子報/行銷（noreply@mail.squarespace.com）、"
        "Instagram（no-reply@mail.instagram.com）、ORCID（DoNotReply@verify.orcid.org）\n"
        "【其他規則】\n"
        "Google Workspace 相關通知（日曆邀請、Drive 分享、Google 帳號安全通知、Workspace 管理員通知）"
    ),
    "shuyukan.dk@gmail.com": (
        "【寄件人指定分類，優先於以下其他規則與通用規則】\n"
        "- 重要：AeonProgress LLC 發票通知（invoice+statements+acct_1QSYRA2NCfBsi89q@stripe.com）、"
        "財政部稅務入口網（webmail@etax.nat.gov.tw）、"
        "Anthropic, PBC 發票通知（invoice+statements@mail.anthropic.com）\n"
        "- 待處理：GitHub 通知（notifications@github.com）、OpenAI（noreply@tm.openai.com）\n"
        "- 一般：ReadKidz（help@readkidz.com）、Claude Team（no-reply@email.claude.com）、Notion 訊息通知\n"
        "【其他規則】\n"
        "信用卡或銀行的刷卡通知、帳單、繳費通知；"
        "客戶或工作往來的信件（需要回覆或處理的）；"
        "課程或學習平台通知（Teachable、Notion、線上課程等）"
    ),
    "60722105@gm.chihlee.edu.tw": (
        "【寄件人指定分類，優先於以下其他規則與通用規則】\n"
        "- 待處理：Make（info@make.com）\n"
        "- 一般：Notion Team（notify@updates.notion.so）、Figma（no-reply@email.figma.com）\n"
        "【其他規則】\n"
        "學校重要通知"
    ),
    "shuyu0908178239@gmail.com": (
        "個人重要事務（保險繳費、保單通知、理賠；政府機關；醫療）；"
        "信用卡或銀行的刷卡通知、帳單、繳費通知；"
        "社群訂閱服務通知（Instagram、重要訂閱服務等）"
    ),
    "blighteye.demi@gmail.com": (
        "【寄件人指定分類，優先於以下其他規則與通用規則】\n"
        "- 重要：電子發票通知（einvoice@einvoice.nat.gov.tw）\n"
        "- 待處理：星展銀行 DBS Bank（eservicetw@dbs.com）、"
        "國泰世華銀行（service@pxbillrc01.cathaybk.com.tw）、"
        "龍巖客戶專區（customer@lyls.com.tw）、"
        "凱基銀行（service@kgibank.com）\n"
        "- 一般：星禮程服務系統（service@myotgcard.starbucks.com.tw）、"
        "星禮程（member@e.starbucks.com.tw）、"
        "ShopBack（hello@info.shopback.com.tw）、"
        "樂天國際商業銀行（Service@mhu.rakuten-bank.com.tw）、"
        "凱基銀行（card888@kgibank.com）、"
        "台北富邦銀行（service@bhu.taipeifubon.com.tw）\n"
        "【其他規則】\n"
        "所有信用卡刷卡通知、銀行帳戶通知、帳單、繳費通知（不論寄件人）"
    ),
}

CLASSIFY_PROMPT = """你是一個郵件分類助手。分析以下郵件，回傳 JSON 格式結果。

郵件資訊：
- 帳號：{account}
- 寄件人：{sender}
- 主旨：{subject}
- 內容：{body}
- 日期：{date}

【此帳號的重要郵件定義】
{account_rules}

【通用規則（優先度低於帳號規則）】
- 電子發票、收據、訂閱收據（e-invoice、receipt）只是消費憑證，不需要行動，除非帳號規則特別指定，否則一律歸為「一般」
- 電子報、促銷信、行銷通知 → 一般

請回傳以下格式的 JSON（只回傳純 JSON，不要 markdown 或其他文字）：
{{
  "category": "重要 | 待處理 | 一般",
  "summary": "一句話摘要（15字以內）",
  "action": "需回覆 | 待閱讀 | 可忽略",
  "reply_template": "規則名稱字串（若無適用規則則填 null，JSON null 不是字串）"
}}

分類標準：
- 重要：符合此帳號重要郵件定義的信
- 待處理：需要稍後閱讀，但不緊急
- 一般：電子報、促銷信、行銷通知、電子發票收據等可忽略的信"""


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

    account = email.get("account", "")
    account_rules = ACCOUNT_RULES.get(account, "依一般規則分類")

    prompt = CLASSIFY_PROMPT.format(
        account=account,
        sender=email.get("sender", ""),
        subject=email.get("subject", ""),
        body=email.get("body", "")[:1000],
        date=email.get("date", ""),
        account_rules=account_rules,
    )

    response = client.chat.completions.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    raw = _extract_json(raw)
    return json.loads(raw)
