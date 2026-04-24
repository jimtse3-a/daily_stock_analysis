# -*- coding: utf-8 -*-
"""
===================================
用户自选股存储服务
===================================

为每个用户维护独立的自选股列表，存储在 SQLite 数据库中。
"""

import logging
import sqlite3
import threading
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Stock code validation regex
_A_STOCK_RE = r'^\d{6}$'
_HK_STOCK_RE = r'^HK\d{5}$'
_US_STOCK_RE = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'

# Database path — stored next to the existing stock_analysis.db
_DB_PATH: Optional[Path] = None
_db_lock = threading.Lock()


def _get_db_path() -> Path:
    global _DB_PATH
    if _DB_PATH is None:
        from src.config import get_config
        data_dir = getattr(get_config(), 'data_dir', Path('data'))
        _DB_PATH = data_dir / 'stock_list.db'
    return _DB_PATH


def _get_connection() -> sqlite3.Connection:
    db_path = _get_db_path()
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    """Ensure the user_stock_list table exists."""
    with _db_lock:
        conn = _get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_stock_list (
                    user_id TEXT NOT NULL,
                    stock_code TEXT NOT NULL,
                    added_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                    PRIMARY KEY (user_id, stock_code)
                )
            """)
            conn.commit()
        finally:
            conn.close()


def _validate_code(code: str) -> Optional[str]:
    """Normalize and validate a stock code. Returns canonical form or None."""
    import re
    code = code.strip().upper()
    if re.match(_A_STOCK_RE, code):
        return code
    if re.match(_HK_STOCK_RE, code):
        return code
    if re.match(_US_STOCK_RE, code):
        return code
    return None


def get_user_stocks(user_id: str) -> List[str]:
    """Get the stock list for a user, ordered by add time."""
    _init_db()
    with _db_lock:
        conn = _get_connection()
        try:
            rows = conn.execute(
                "SELECT stock_code FROM user_stock_list WHERE user_id = ? ORDER BY added_at ASC",
                (user_id,),
            ).fetchall()
            return [r['stock_code'] for r in rows]
        finally:
            conn.close()


def add_stock(user_id: str, stock_code: str) -> tuple[bool, str]:
    """
    Add a stock to a user's watchlist.

    Returns (success, message).
    """
    _init_db()
    canonical = _validate_code(stock_code)
    if canonical is None:
        return False, f"无效的股票代码: {stock_code}，支持格式: A股(600519) / 港股(HK00700) / 美股(AAPL)"

    with _db_lock:
        conn = _get_connection()
        try:
            existing = conn.execute(
                "SELECT 1 FROM user_stock_list WHERE user_id = ? AND stock_code = ?",
                (user_id, canonical),
            ).fetchone()
            if existing:
                return True, f"**{canonical}** 已在自选列表中，无需重复添加"
            conn.execute(
                "INSERT INTO user_stock_list (user_id, stock_code) VALUES (?, ?)",
                (user_id, canonical),
            )
            conn.commit()

            count = conn.execute(
                "SELECT COUNT(*) FROM user_stock_list WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]
            return True, f"✅ 已添加 **[{canonical}]** 到你的自选列表（共 {count} 只）"
        finally:
            conn.close()


def remove_stock(user_id: str, stock_code: str) -> tuple[bool, str]:
    """
    Remove a stock from a user's watchlist.

    Returns (success, message).
    """
    _init_db()
    canonical = _validate_code(stock_code)
    if canonical is None:
        return False, f"无效的股票代码: {stock_code}"

    with _db_lock:
        conn = _get_connection()
        try:
            existing = conn.execute(
                "SELECT 1 FROM user_stock_list WHERE user_id = ? AND stock_code = ?",
                (user_id, canonical),
            ).fetchone()
            if not existing:
                return False, f"**{stock_code}** 不在你的自选列表中，删除失败"
            conn.execute(
                "DELETE FROM user_stock_list WHERE user_id = ? AND stock_code = ?",
                (user_id, canonical),
            )
            conn.commit()

            count = conn.execute(
                "SELECT COUNT(*) FROM user_stock_list WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]
            return True, f"✅ 已从自选列表移除 **[{canonical}]**（剩余 {count} 只）"
        finally:
            conn.close()
