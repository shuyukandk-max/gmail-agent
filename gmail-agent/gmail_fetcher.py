import os
import base64
import socket
from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google_auth_httplib2
import httplib2

# httplib2 預設用 IPv4，但此網路環境 IPv6 才通，強制優先 IPv6
_orig_getaddrinfo = socket.getaddrinfo
def _prefer_ipv6(host, port, family=0, *args, **kwargs):
    results = _orig_getaddrinfo(host, port, family, *args, **kwargs)
    return sorted(results, key=lambda x: 0 if x[0] == socket.AF_INET6 else 1)
socket.getaddrinfo = _prefer_ipv6

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

    http = httplib2.Http(timeout=30)
    authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)
    return build("gmail", "v1", http=authorized_http, cache_discovery=False)


def fetch_yesterday_emails(service, account_email: str) -> list:
    taiwan = timezone(timedelta(hours=8))
    now_tw = datetime.now(taiwan)
    today_str = now_tw.strftime("%Y/%m/%d")
    two_days_ago_str = (now_tw - timedelta(days=2)).strftime("%Y/%m/%d")
    query = f"after:{two_days_ago_str} before:{today_str}"

    print(f"   [{account_email}] 查詢：{query}")
    result = service.users().messages().list(userId="me", q=query).execute()
    messages = result.get("messages", [])
    print(f"   [{account_email}] 找到 {len(messages)} 封")

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
        try:
            service = get_gmail_service(account["token_file"], credentials_file)
            emails = fetch_yesterday_emails(service, account["email"])
            all_emails.extend(emails)
        except Exception as e:
            print(f"   ⚠️  [{account['email']}] 讀取失敗：{e}")
    return all_emails
