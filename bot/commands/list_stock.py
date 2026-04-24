# -*- coding: utf-8 -*-
"""
===================================
自选股列表命令
===================================

查看当前用户的自选股列表。
"""

import logging
from typing import List, Optional

from bot.commands.base import BotCommand
from bot.commands.stock_list_service import get_user_stocks
from bot.models import BotMessage, BotResponse

logger = logging.getLogger(__name__)


class ListStockCommand(BotCommand):
    """查看自选股列表"""

    @property
    def name(self) -> str:
        return "list"

    @property
    def aliases(self) -> List[str]:
        return ["列表", "自选股", "ls"]

    @property
    def description(self) -> str:
        return "查看你的自选股列表"

    @property
    def usage(self) -> str:
        return "/list"

    def validate_args(self, args: List[str]) -> Optional[str]:
        return None

    def execute(self, message: BotMessage, args: List[str]) -> BotResponse:
        logger.info(f"[ListStock] user={message.user_id} listing stocks")

        stocks = get_user_stocks(message.user_id)

        if not stocks:
            lines = [
                "📋 **你的自选列表为空**",
                "",
                "使用 `/add 600519` 添加自选股",
                "例如：`/add 600519` 或 `/add HK00700`",
            ]
        else:
            lines = [f"📋 **你的自选列表**（共 {len(stocks)} 只）", ""]
            for i, code in enumerate(stocks, 1):
                lines.append(f"{i}. `{code}`")
            lines.append("")
            lines.append(f"要删除某只股票：`/remove <代码>`")

        return BotResponse.markdown_response("\n".join(lines))
