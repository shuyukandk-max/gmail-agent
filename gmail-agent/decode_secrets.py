import base64
import os

files = {
    "credentials.json": os.environ["GOOGLE_CREDENTIALS"],
    "tokens/token1.json": os.environ["GMAIL_TOKEN_1"],
    "tokens/token2.json": os.environ["GMAIL_TOKEN_2"],
    "tokens/token3.json": os.environ["GMAIL_TOKEN_3"],
    "tokens/token4.json": os.environ["GMAIL_TOKEN_4"],
    "tokens/token5.json": os.environ["GMAIL_TOKEN_5"],
}
for path, data in files.items():
    with open(path, "wb") as f:
        f.write(base64.b64decode(data))
