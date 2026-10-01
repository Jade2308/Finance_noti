"""
Sentiment Analyzer - Đánh giá tâm lý thị trường (Fear & Greed).
"""

from typing import Dict, Any

class SentimentAnalyzer:
    """Đo lường tâm lý thị trường dựa trên các dữ liệu định lượng."""

    @staticmethod
    def calculate_fear_and_greed(market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tính toán chỉ số Fear & Greed cơ bản cho VN-Index.

        Phương pháp: Normalize từng thành phần về [0, 1] rồi tổng hợp có trọng số.
        - RSI Component (trọng số 60%):
            RSI < 30 → gần 0 (Fear), RSI > 70 → gần 1 (Greed)
            Vùng trung lập [30, 70] → linear map về [0.0, 1.0]
        - MACD Momentum Component (trọng số 40%):
            MACD > Signal → Bullish = 1.0
            MACD < Signal → Bearish = 0.0
            Mức độ chênh lệch điều chỉnh tinh tế trong [0.2, 0.8]

        Output: score (0–100), label, components
        """
        # FIX: rsi_14/macd/macd_signal hiện là float | None (không còn là string "N/A")
        rsi_raw = market_data.get("rsi_14")
        macd_raw = market_data.get("macd")
        if "error" in market_data or rsi_raw is None:
            return {
                "score": 50,
                "label": "Neutral (Trung lập)",
                "description": "Không đủ dữ liệu TA để tính toán.",
                "components": {}
            }

        try:
            rsi = float(rsi_raw)
            macd = float(macd_raw) if macd_raw is not None else 0.0
            macd_signal = float(market_data.get("macd_signal") or 0.0)

            # --- Component 1: RSI (60%) ---
            # Map RSI [30, 70] → [0.0, 1.0]
            # Ngoài biên: RSI < 30 → 0.0 (Extreme Fear), RSI > 70 → 1.0 (Extreme Greed)
            rsi_normalized = (rsi - 30) / 40.0
            rsi_normalized = max(0.0, min(1.0, rsi_normalized))

            # --- Component 2: MACD Momentum (40%) ---
            # MACD > Signal → bullish momentum → gần 1.0
            # MACD < Signal → bearish momentum → gần 0.0
            # Dùng sigmoid-like để làm mượt, tránh nhảy bậc thang
            macd_diff = macd - macd_signal
            # Normalize: diff dương → >0.5, diff âm → <0.5
            # Scale factor 0.1 tùy chỉnh theo độ lớn MACD của VNINDEX (~1200 điểm)
            macd_normalized = 1.0 / (1.0 + pow(2.718, -macd_diff * 0.1))
            # Đảm bảo trong [0.0, 1.0]
            macd_normalized = max(0.0, min(1.0, macd_normalized))

            # --- Tổng hợp có trọng số ---
            WEIGHT_RSI = 0.60
            WEIGHT_MACD = 0.40
            composite = (rsi_normalized * WEIGHT_RSI) + (macd_normalized * WEIGHT_MACD)

            # Scale về [0, 100]
            final_score = round(composite * 100)
            final_score = max(0, min(100, final_score))

            # --- Phân loại nhãn ---
            if final_score <= 20:
                label = "Extreme Fear (Sợ hãi tột độ)"
            elif final_score <= 40:
                label = "Fear (Sợ hãi)"
            elif final_score <= 60:
                label = "Neutral (Trung lập)"
            elif final_score <= 80:
                label = "Greed (Tham lam)"
            else:
                label = "Extreme Greed (Tham lam tột độ)"

            return {
                "score": final_score,
                "label": label,
                "components": {
                    "rsi_raw": rsi,
                    "rsi_normalized": round(rsi_normalized, 3),
                    "macd_diff": round(macd_diff, 4),
                    "macd_normalized": round(macd_normalized, 3),
                    "weights": {"rsi": WEIGHT_RSI, "macd": WEIGHT_MACD}
                }
            }
        except Exception as e:
            return {
                "score": 50,
                "label": "Neutral (Trung lập)",
                "description": f"Lỗi tính toán: {e}",
                "components": {}
            }
