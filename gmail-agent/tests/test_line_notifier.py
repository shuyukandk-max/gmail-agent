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
