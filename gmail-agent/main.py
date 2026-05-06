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
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", line_cfg["channel_access_token"])
    line_user_id = os.environ.get("LINE_USER_ID", line_cfg["user_id"])
    success = send_line_message(
        token=line_token,
        user_id=line_user_id,
        message=message
    )

    if success:
        print("✅ LINE 通知發送成功")
    else:
        print("❌ LINE 通知發送失敗，請確認 token 和 user_id")


if __name__ == "__main__":
    main()
