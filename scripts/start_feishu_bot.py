# -*- coding: utf-8 -*-
"""
飞书机器人启动脚本

运行方式：
    python scripts/start_feishu_bot.py

机器人会通过 WebSocket 长连接接收飞书消息，
无需配置公网 Webhook URL。

按 Ctrl+C 停止。
"""

import sys
import os

# 确保从项目根目录导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from bot.platforms.feishu_stream import start_feishu_stream_background, get_feishu_stream_client
from src.logging_config import setup_logging

setup_logging(log_prefix="feishu_bot", console_level=20)  # INFO

def main():
    print("=" * 50)
    print("飞书股票分析机器人 启动中...")
    print("=" * 50)
    print()

    client = get_feishu_stream_client()
    if client is None:
        print("ERROR: 无法创建飞书机器人客户端")
        print("请确认 .env 文件中已配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        print("并且 FEISHU_STREAM_ENABLED=true")
        sys.exit(1)

    client.start_background()
    print("飞书机器人已启动，等待消息...")
    print("发送 /help 查看可用命令")
    print("按 Ctrl+C 停止")
    print()

    try:
        import time
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n正在停止机器人...")
        client.stop()
        print("已停止")

if __name__ == "__main__":
    main()
