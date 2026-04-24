# -*- coding: utf-8 -*-
"""
===================================
删除自选股命令
===================================

将股票代码从当前用户的自选列表中移除。
"""

import logging
from typing import List, Optional

from bot.commands.base import BotCommand
from bot.commands.stock_list_service import remove_stock
from bot.models import BotMessage, BotResponse

logger = logging.getLogger(__name__)


class RemoveStockCommand(BotCommand):
    """删除自选股"""

    @property
    def name(self) -> str:
        return "remove"

    @property
    def aliases(self) -> List[str]:
        return ["删除", "删", "自选删除", "del"]

    @property
    def description(self) -> str:
        return "将股票从自选列表移除"

    @property
    def usage(self) -> str:
        return "/remove <股票代码>"

    def validate_args(self, args: List[str]) -> Optional[str]:
        if not args:
            return "请输入要删除的股票代码\n用法: `/remove 600519`"
        return None

    def execute(self, message: BotMessage, args: List[str]) -> BotResponse:
        code = args[0].strip()
        logger.info(f"[RemoveStock] user={message.user_id} remove={code}")

        success, reply = remove_stock(message.user_id, code)
        return BotResponse.text_response(reply)
