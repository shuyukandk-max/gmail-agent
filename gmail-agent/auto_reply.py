import base64
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
