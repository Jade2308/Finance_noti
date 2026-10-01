"""
Cấu hình ứng dụng VN Finance Hub.
Nạp biến môi trường từ .env và định nghĩa các hằng số.
"""

import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Tìm và nạp file .env từ thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# ==========================================
# 1. TELEGRAM BOT
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# ==========================================
# 2. GOOGLE GEMINI AI
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()

# ==========================================
# 3. LỊCH BÁO CÁO HÀNG NGÀY
# ==========================================
# Giờ Việt Nam (Asia/Ho_Chi_Minh)
DAILY_REPORT_HOUR = int(os.getenv("DAILY_REPORT_HOUR", "18"))
DAILY_REPORT_MINUTE = int(os.getenv("DAILY_REPORT_MINUTE", "0"))

# ==========================================
# 4. CƠ SỞ DỮ LIỆU
# ==========================================
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "finance_hub.db"))

# ==========================================
# 5. DANH MỤC ĐẦU TƯ QUỸ MỞ (PORTFOLIO)
# ==========================================
# FIX: Đọc từ portfolio.json (gitignored) thay vì hardcode trong settings.py
# Điều này ngăn vô tình commit thông tin giao dịch cá nhân lên Git.
_PORTFOLIO_PATH = Path(os.getenv("PORTFOLIO_PATH", str(BASE_DIR / "portfolio.json")))

def _load_portfolio() -> list:
    """Nạp danh mục từ biến môi trường PORTFOLIO_JSON hoặc file portfolio.json."""
    # 1. Thử biến môi trường (tiện lợi khi deploy Cloud/Render)
    portfolio_env = os.getenv("PORTFOLIO_JSON", "").strip()
    if portfolio_env:
        try:
            data = json.loads(portfolio_env)
            funds = data.get("funds", [])
            if funds:
                logger.info("Đã nạp danh mục thành công từ biến môi trường PORTFOLIO_JSON.")
                return funds
        except Exception as e:
            logger.error("Lỗi đọc biến môi trường PORTFOLIO_JSON: %s", e)

    # 2. Thử file local portfolio.json
    if _PORTFOLIO_PATH.exists():
        try:
            with open(_PORTFOLIO_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("funds", [])
        except Exception as e:
            logger.error("Lỗi đọc portfolio.json: %s", e)
    else:
        logger.warning(
            "Không tìm thấy portfolio.json tại %s. "
            "Hãy tạo file này từ portfolio.json.example hoặc cấu hình biến PORTFOLIO_JSON. Dùng danh mục mẫu.",
            _PORTFOLIO_PATH,
        )
    # Fallback mẫu — chỉ để app không crash khi chưa có file
    return [
        {
            "fund_code": "VEOF",
            "fund_name": "Quỹ Đầu Tư Cổ Phiếu Doanh Nghiệp Hàng Đầu VinaCapital",
            "transactions": [],
            "total_units": 0.0,
            "total_invested": 0.0,
        }
    ]

FUND_PORTFOLIO = _load_portfolio()

# Danh sách mã quỹ/chỉ số theo dõi thêm
WATCHLIST_INDICES = ["VNINDEX", "VN30"]
WATCHLIST_FUNDS = ["VEOF", "VESAF", "VIBF", "VFF"]
