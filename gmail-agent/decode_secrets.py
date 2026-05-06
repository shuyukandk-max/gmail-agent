import os
import json

files = {
    "credentials.json": os.environ["GOOGLE_CREDENTIALS"],
    "tokens/token1.json": os.environ["GMAIL_TOKEN_1"],
    "tokens/token2.json": os.environ["GMAIL_TOKEN_2"],
    "tokens/token3.json": os.environ["GMAIL_TOKEN_3"],
    "tokens/token4.json": os.environ["GMAIL_TOKEN_4"],
    "tokens/token5.json": os.environ["GMAIL_TOKEN_5"],
}
for path, data in files.items():
    if not data.strip():
        raise ValueError(f"Secret for {path} is empty!")
    try:
        json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for {path}: {e}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    print(f"OK: {path} ({len(data)} chars)")
