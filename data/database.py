"""
SQLite database module - Lưu trữ lịch sử dữ liệu tài chính và thông báo.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class FinanceDatabase:
    """Quản lý kết nối và các bảng dữ liệu SQLite."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Đảm bảo thư mục chứa database tồn tại
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Khởi tạo cấu trúc các bảng nếu chưa có."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Bảng lịch sử NAV của các quỹ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nav_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fund_code TEXT NOT NULL,
                    nav REAL NOT NULL,
                    nav_date TEXT NOT NULL,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(fund_code, nav_date)
                )
            """)

            # 2. Bảng lịch sử VN-Index và các chỉ số
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_index_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    index_code TEXT NOT NULL,
                    price REAL,
                    change REAL,
                    change_pct REAL,
                    volume REAL,
                    recorded_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Bảng lịch sử giá trị danh mục (Portfolio Snapshot)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_invested REAL NOT NULL,
                    total_current_value REAL NOT NULL,
                    total_pnl REAL NOT NULL,
                    total_pnl_pct REAL NOT NULL,
                    snapshot_date TEXT NOT NULL,
                    details_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Bảng nhật ký thông báo đã gửi qua Telegram
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_type TEXT NOT NULL,
                    content_preview TEXT,
                    status TEXT DEFAULT 'SUCCESS',
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 5. FIX: Bảng lịch sử hội thoại Telegram Bot (thay thế dict trong RAM)
            #    Lưu 20 tin nhắn gần nhất mỗi chat_id, tồn tại sau khi restart.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Index để truy vấn nhanh theo chat_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_history_chat_id
                ON chat_history (chat_id, created_at DESC)
            """)

            conn.commit()

    # ─────────────────────────── NAV ───────────────────────────

    def save_nav(self, fund_code: str, nav: float, nav_date: str, source: str = "auto") -> bool:
        """Lưu hoặc cập nhật giá trị NAV theo ngày."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO nav_history (fund_code, nav, nav_date, source)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(fund_code, nav_date) DO UPDATE SET
                        nav = excluded.nav,
                        source = excluded.source,
                        created_at = CURRENT_TIMESTAMP
                """, (fund_code, nav, nav_date, source))
                conn.commit()
                return True
        except Exception as e:
            logger.error("[DB Error] Lỗi lưu NAV: %s", e)
            return False

    def get_latest_nav(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """Lấy giá trị NAV mới nhất của một quỹ."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fund_code, nav, nav_date, source, created_at
                FROM nav_history
                WHERE fund_code = ?
                ORDER BY nav_date DESC, id DESC
                LIMIT 1
            """, (fund_code,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_nav_history(self, fund_code: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Lấy danh sách NAV lịch sử theo thứ tự tăng dần ngày."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fund_code, nav, nav_date
                FROM (
                    SELECT fund_code, nav, nav_date
                    FROM nav_history
                    WHERE fund_code = ?
                    ORDER BY nav_date DESC
                    LIMIT ?
                )
                ORDER BY nav_date ASC
            """, (fund_code, limit))
            return [dict(row) for row in cursor.fetchall()]

    # ─────────────────────────── Market Index ───────────────────────────

    def save_market_index(self, index_code: str, price: float, change: float,
                          change_pct: float, volume: float, recorded_date: str):
        """Lưu snapshot chỉ số thị trường."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO market_index_history (index_code, price, change, change_pct, volume, recorded_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (index_code, price, change, change_pct, volume, recorded_date))
                conn.commit()
        except Exception as e:
            logger.error("[DB Error] Lỗi lưu chỉ số thị trường: %s", e)

    # ─────────────────────────── Notifications ───────────────────────────

    def save_notification_log(self, report_type: str, content_preview: str, status: str = "SUCCESS"):
        """Ghi nhận lịch sử gửi thông báo."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notification_logs (report_type, content_preview, status)
                    VALUES (?, ?, ?)
                """, (report_type, content_preview[:500], status))
                conn.commit()
        except Exception as e:
            logger.error("[DB Error] Lỗi ghi log thông báo: %s", e)

    # ─────────────────────────── Chat History (FIX) ───────────────────────────

    def get_chat_history(self, chat_id: str, limit: int = 20) -> List[Dict[str, str]]:
        """
        Lấy lịch sử hội thoại của chat_id, sắp xếp theo thời gian cũ → mới.
        Trả về list [{"role": "user"|"model", "text": "..."}, ...]
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT role, text FROM (
                        SELECT role, text, created_at
                        FROM chat_history
                        WHERE chat_id = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    )
                    ORDER BY created_at ASC
                """, (chat_id, limit))
                return [{"role": row["role"], "text": row["text"]} for row in cursor.fetchall()]
        except Exception as e:
            logger.error("[DB Error] Lỗi đọc chat history: %s", e)
            return []

    def append_chat_messages(self, chat_id: str, messages: List[Dict[str, str]], max_history: int = 20):
        """
        Thêm các tin nhắn mới vào chat history và tự động xóa tin cũ vượt quá max_history.
        messages: list [{"role": "user"|"model", "text": "..."}, ...]
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for msg in messages:
                    cursor.execute("""
                        INSERT INTO chat_history (chat_id, role, text)
                        VALUES (?, ?, ?)
                    """, (chat_id, msg["role"], msg["text"]))

                # Giữ tối đa max_history tin nhắn mỗi chat_id (xóa tin cũ nhất)
                cursor.execute("""
                    DELETE FROM chat_history
                    WHERE chat_id = ? AND id NOT IN (
                        SELECT id FROM chat_history
                        WHERE chat_id = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    )
                """, (chat_id, chat_id, max_history))
                conn.commit()
        except Exception as e:
            logger.error("[DB Error] Lỗi lưu chat history: %s", e)

    def clear_chat_history(self, chat_id: str):
        """Xóa toàn bộ lịch sử hội thoại của một chat_id."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chat_history WHERE chat_id = ?", (chat_id,))
                conn.commit()
        except Exception as e:
            logger.error("[DB Error] Lỗi xóa chat history: %s", e)
