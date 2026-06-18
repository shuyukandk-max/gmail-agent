import requests
from datetime import date as date_type


def format_summary(emails: list, date: str = None, fetched: int = None) -> str:
    if date is None:
        date = str(date_type.today())

    important = [e for e in emails if e.get("category") == "重要"]
    pending = [e for e in emails if e.get("category") == "待處理"]
    general = [e for e in emails if e.get("category") == "一般"]

    fetch_info = f"（共讀取 {fetched} 封）" if fetched is not None else ""
    lines = [f"📬 {date} 郵件摘要 {fetch_info}", ""]

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
