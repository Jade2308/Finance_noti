"""
Gold Collector - Thu thập giá vàng SJC và biến động giá vàng trong nước.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GoldCollector:
    """Thu thập thông tin giá vàng SJC từ Vnstock Retail."""

    def __init__(self):
        pass

    def get_gold_prices(self) -> Dict[str, Any]:
        """Lấy giá vàng SJC mới nhất."""
        try:
            from vnstock import Retail
            ret = Retail()
            df = ret.gold()
            if df is not None and not df.empty:
                # Lọc dòng SJC HCM hoặc dòng đầu tiên
                sjc_rows = df[df["name"].str.contains("SJC", case=False, na=False)]
                target = sjc_rows.iloc[0] if not sjc_rows.empty else df.iloc[0]

                buy = float(target["buy_price"])
                sell = float(target["sell_price"])
                spread = sell - buy
                date_val = str(target.get("date", datetime.now().strftime("%Y-%m-%d")))

                return {
                    "name": str(target["name"]),
                    "buy_price": buy,
                    "sell_price": sell,
                    "spread": spread,
                    "date": date_val,
                    "formatted_buy": f"{buy:,.0f} đ",
                    "formatted_sell": f"{sell:,.0f} đ",
                    "formatted_spread": f"{spread:,.0f} đ",
                    "source": "vnstock_retail",
                }
        except Exception as e:
            logger.warning("[GoldCollector] Error: %s", e)

        # Fallback — chỉ dùng khi API hoàn toàn không lấy được
        # Cập nhật giá tham chiếu định kỳ: Q3/2026 ~135-145 triệu/lượng SJC
        FALLBACK_BUY = 139_500_000.0
        FALLBACK_SELL = 142_500_000.0
        logger.warning("[GoldCollector] Không lấy được giá vàng từ API. Dùng snapshot tham chiếu cũ!")
        return {
            "name": "Vàng SJC (⚠️ Snapshot tham chiếu - có thể không chính xác)",
            "buy_price": FALLBACK_BUY,
            "sell_price": FALLBACK_SELL,
            "spread": FALLBACK_SELL - FALLBACK_BUY,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "formatted_buy": f"{FALLBACK_BUY:,.0f} đ",
            "formatted_sell": f"{FALLBACK_SELL:,.0f} đ",
            "formatted_spread": f"{FALLBACK_SELL - FALLBACK_BUY:,.0f} đ",
            "source": "fallback",
            "warning": "⚠️ Không lấy được giá thực từ API. Dữ liệu có thể lỗi thời. Kiểm tra lại kết nối mạng.",
        }
