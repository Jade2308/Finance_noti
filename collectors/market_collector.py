"""
Market Data Collector - Thu thập dữ liệu chỉ số thị trường chứng khoán (VN-Index, VN30).
Tích hợp trực tiếp từ Vnstock Index OHLCV và Database Cache.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketDataCollector:
    """Thu thập thông tin chỉ số VN-Index và độ rộng thị trường."""

    def __init__(self, db_instance=None):
        self.db = db_instance

    def get_vnindex(self) -> Dict[str, Any]:
        """
        Lấy dữ liệu chỉ số VN-Index mới nhất.
        Sử dụng Vnstock Index OHLCV để lấy giá đóng cửa và tính % thay đổi so với phiên trước.

        Lưu ý về kiểu dữ liệu:
            - rsi_14, macd, macd_signal: float | None (không phải string)
              SentimentAnalyzer sử dụng float() trực tiếp nên giữ nguyên kiểu float.
              Giá trị None khi không đủ dữ liệu để tính TA.
        """
        # Cách 1: Thử qua Vnstock Index OHLCV
        try:
            from vnstock import Market
            m = Market()
            df = m.index("VNINDEX").ohlcv()
            if df is not None and not df.empty and len(df) >= 2:
                # Tính toán phân tích kỹ thuật (Technical Analysis)
                # FIX: lưu dạng float | None, không format thành string
                rsi_val: Optional[float] = None
                macd_val: Optional[float] = None
                macd_signal_val: Optional[float] = None

                if len(df) >= 30:
                    try:
                        import ta
                        rsi_series = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
                        macd_obj = ta.trend.MACD(df["close"])
                        rsi_val = round(float(rsi_series.iloc[-1]), 2)
                        macd_val = round(float(macd_obj.macd().iloc[-1]), 2)
                        macd_signal_val = round(float(macd_obj.macd_signal().iloc[-1]), 2)
                    except Exception as ta_err:
                        logger.warning("[MarketCollector] Lỗi tính TA indicators: %s", ta_err)

                latest = df.iloc[-1]
                prev = df.iloc[-2]

                latest_close = float(latest["close"])
                prev_close = float(prev["close"])
                change = latest_close - prev_close
                change_pct = (change / prev_close) * 100
                volume = float(latest.get("volume", 0))
                time_val = str(latest.get("time", datetime.now().strftime("%Y-%m-%d")))

                result: Dict[str, Any] = {
                    "index_code": "VNINDEX",
                    "price": f"{latest_close:,.2f}",
                    "price_raw": latest_close,
                    "change": f"{change:+,.2f}",
                    "change_pct": f"{change_pct:+.2f}%",
                    "volume": f"{volume:,.0f}" if volume > 0 else "N/A",
                    # float | None — SentimentAnalyzer đọc trực tiếp
                    "rsi_14": rsi_val,
                    "macd": macd_val,
                    "macd_signal": macd_signal_val,
                    "date": time_val,
                    "source": "vnstock_index",
                }

                if self.db:
                    self.db.save_market_index(
                        index_code="VNINDEX",
                        price=latest_close,
                        change=change,
                        change_pct=change_pct,
                        volume=volume,
                        recorded_date=time_val,
                    )
                return result
        except Exception as e:
            logger.warning("[MarketCollector] Vnstock index error: %s", e)

        # Cách 2: Fallback snapshot gần nhất (không có TA)
        logger.warning("[MarketCollector] Dùng snapshot fallback cho VN-Index.")
        return {
            "index_code": "VNINDEX",
            "price": "1,280.50",
            "price_raw": 1280.50,
            "change": "+5.20",
            "change_pct": "+0.41%",
            "volume": "650,000,000",
            "rsi_14": None,
            "macd": None,
            "macd_signal": None,
            "source": "snapshot_fallback",
        }

    def get_historical_vnindex(self) -> Optional[Any]:
        """Lấy dữ liệu lịch sử VNINDEX dưới dạng DataFrame để LSTM sử dụng."""
        try:
            from vnstock import Market
            m = Market()
            df = m.index("VNINDEX").ohlcv()
            return df
        except Exception as e:
            logger.error("[MarketCollector] Lỗi lấy lịch sử VNINDEX: %s", e)
            return None
