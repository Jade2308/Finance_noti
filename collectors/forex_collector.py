"""
Forex Collector - Thu thập tỷ giá ngoại tệ (USD/VND, EUR/VND).
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ForexCollector:
    """Thu thập thông tin tỷ giá ngoại tệ từ Vnstock Retail."""

    def __init__(self):
        pass

    def get_exchange_rates(self) -> Dict[str, Any]:
        """Lấy tỷ giá USD và các ngoại tệ chính so với VND."""
        try:
            from vnstock import Retail
            ret = Retail()
            df = ret.exchange_rate()
            if df is not None and not df.empty:
                result: Dict[str, Any] = {}
                date_val = str(df.iloc[0].get("date", datetime.now().strftime("%Y-%m-%d")))

                # Lấy USD
                usd_df = df[df["currency_code"] == "USD"]
                if not usd_df.empty:
                    usd_row = usd_df.iloc[0]
                    result["USD"] = {
                        "code": "USD",
                        "name": "US Dollar",
                        "buy_cash": str(usd_row.get("buy_cash", "N/A")),
                        "buy_transfer": str(usd_row.get("buy_transfer", "N/A")),
                        "sell": str(usd_row.get("sell", "N/A")),
                    }

                # Lấy EUR
                eur_df = df[df["currency_code"] == "EUR"]
                if not eur_df.empty:
                    eur_row = eur_df.iloc[0]
                    result["EUR"] = {
                        "code": "EUR",
                        "name": "Euro",
                        "buy_transfer": str(eur_row.get("buy_transfer", "N/A")),
                        "sell": str(eur_row.get("sell", "N/A")),
                    }

                result["date"] = date_val
                result["source"] = "vnstock_retail"
                return result
        except Exception as e:
            logger.warning("[ForexCollector] Error: %s", e)

        # Fallback tham khảo
        logger.warning("[ForexCollector] Dùng tỷ giá fallback.")
        return {
            "USD": {
                "code": "USD",
                "name": "US Dollar",
                "buy_cash": "25,750",
                "buy_transfer": "25,780",
                "sell": "26,160",
            },
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "fallback",
        }
