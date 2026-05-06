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
