@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
echo ======================================
echo  飞书股票分析机器人
echo ======================================
echo.
echo 启动中...
python scripts/start_feishu_bot.py
pause
