#!/bin/bash
# Gmail 代理人啟動腳本（給 cron 使用）
cd /Users/demi/Desktop/demi-agent/gmail-agent

# 載入環境變數
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

/usr/bin/python3 main.py
