# -*- coding: utf-8 -*-
"""
===================================
添加自选股命令
===================================

将股票代码添加到当前用户的自选列表。
"""

import logging
from typing import List, Optional

from bot.commands.base import BotCommand
from bot.commands.stock_list_service import add_stock
from bot.models import BotMessage, BotResponse

logger = logging.getLogger(__name__)


class AddStockCommand(BotCommand):
    """添加自选股"""

    @property
    def name(self) -> str:
        return "add"

    @property
    def aliases(self) -> List[str]:
        return ["添加", "加", "自选"]

    @property
    def description(self) -> str:
        return "将股票加入自选列表"

    @property
    def usage(self) -> str:
        return "/add <股票代码>"

    def validate_args(self, args: List[str]) -> Optional[str]:
        if not args:
            return "请输入要添加的股票代码\n用法: `/add 600519`"
        return None

    def execute(self, message: BotMessage, args: List[str]) -> BotResponse:
        code = args[0].strip()
        logger.info(f"[AddStock] user={message.user_id} add={code}")

        success, reply = add_stock(message.user_id, code)
        return BotResponse.text_response(reply)
