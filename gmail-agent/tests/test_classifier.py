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
    mocker.patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})

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
    mocker.patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})

    email = {**FAKE_EMAIL, "subject": "本週特賣優惠", "body": "點此取消訂閱"}
    result = classify_email(email, model="claude-sonnet-4-6")

    assert result["category"] == "一般"
    assert result["reply_template"] is None

def test_classify_email_with_markdown_wrapper(mocker):
    wrapped_json = '''```json
{
  "category": "待處理",
  "summary": "廠商報價待確認",
  "action": "待閱讀",
  "reply_template": null
}
```'''
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=wrapped_json)]
    )
    mocker.patch('ai_classifier.anthropic.Anthropic', return_value=mock_client)
    mocker.patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})

    email = {**FAKE_EMAIL, "subject": "報價單", "body": "附上報價單請確認"}
    result = classify_email(email, model="claude-sonnet-4-6")

    assert result["category"] == "待處理"
    assert result["reply_template"] is None
