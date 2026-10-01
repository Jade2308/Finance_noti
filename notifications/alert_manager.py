"""
Alert Manager - Quản lý và kích hoạt các cảnh báo biến động thị trường thông minh.
Giám sát ngưỡng biến động của: VN-Index, NAV quỹ mở, Giá vàng SJC và Tỷ giá ngoại tệ.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AlertManager:
    """Kiểm tra điều kiện biến động và tạo danh sách thông báo cảnh báo thông minh."""

    def __init__(self):
        # Các ngưỡng kích hoạt cảnh báo
        self.VNINDEX_CRASH_THRESHOLD = -2.0     # VN-Index giảm >= 2.0% trong ngày
        self.VNINDEX_SURGE_THRESHOLD = 2.0      # VN-Index tăng >= 2.0% trong ngày
        self.NAV_DROP_7D_THRESHOLD = -4.0       # NAV quỹ giảm >= 4.0% trong 7 ngày
        self.NAV_SURGE_30D_THRESHOLD = 8.0      # NAV quỹ tăng >= 8.0% trong 30 ngày
        self.USD_HIGH_PRESSURE = 26_000.0       # Tỷ giá bán USD vượt 26,000 đ

    def evaluate_market_alerts(
        self,
        market_data: Optional[Dict[str, Any]] = None,
        nav_trend: Optional[Dict[str, Any]] = None,
        gold_data: Optional[Dict[str, Any]] = None,
        forex_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Đánh giá toàn diện các tín hiệu thị trường và sinh danh sách cảnh báo.

        Returns:
            Danh sách cảnh báo: [{"level": "HIGH"|"MEDIUM"|"INFO", "title": str, "message": str, "action": str}, ...]
        """
        alerts: List[Dict[str, Any]] = []

        # 1. Cảnh báo VN-Index
        if market_data and "error" not in market_data:
            change_pct_raw = market_data.get("change_pct", "0%")
            try:
                # Loại bỏ dấu % và chuyển sang float
                pct_val = float(str(change_pct_raw).replace("%", "").replace("+", "").strip())
                if pct_val <= self.VNINDEX_CRASH_THRESHOLD:
                    alerts.append({
                        "level": "HIGH",
                        "code": "vnindex_crash",
                        "title": f"🔴 THỊ TRƯỜNG GIẢM MẠNH: VN-Index {pct_val:+.2f}%",
                        "message": (
                            f"VN-Index hôm nay giảm mạnh {pct_val:+.2f}% về mốc {market_data.get('price', 'N/A')}. "
                            "Áp lực bán tháo lan rộng có thể tác động trực tiếp làm sụt giảm NAV của quỹ cổ phiếu VEOF."
                        ),
                        "action": "Không nên hoảng loạn bán tháo. Với chiến lược DCA dài hạn, các phiên giảm sâu thường là cơ hội mua tích lũy giá tốt."
                    })
                elif pct_val >= self.VNINDEX_SURGE_THRESHOLD:
                    alerts.append({
                        "level": "INFO",
                        "code": "vnindex_surge",
                        "title": f"🟢 THỊ TRƯỜNG BÙNG NỔ: VN-Index {pct_val:+.2f}%",
                        "message": (
                            f"VN-Index tăng ấn tượng {pct_val:+.2f}% lên {market_data.get('price', 'N/A')}. "
                            "Dòng tiền nhập cuộc tích cực giúp danh mục đầu tư của bạn tăng trưởng mạnh."
                        ),
                        "action": "Tiếp tục duy trì kỷ luật tích lũy, không nên FOMO mua đuổi ở vùng giá cao."
                    })
            except Exception as e:
                logger.warning("[AlertManager] Lỗi phân tích % VN-Index: %s", e)

        # 2. Cảnh báo NAV quỹ 7 ngày & 30 ngày
        if nav_trend:
            chg_7d = nav_trend.get("change_7d_pct", 0.0)
            chg_30d = nav_trend.get("change_30d_pct", 0.0)

            if chg_7d <= self.NAV_DROP_7D_THRESHOLD:
                alerts.append({
                    "level": "HIGH",
                    "code": "nav_drop_7d",
                    "title": f"⚠️ NAV QUỸ ĐIỀU CHỈNH: Giảm {chg_7d:+.2f}% trong 7 phiên",
                    "message": f"Giá trị CCQ đã sụt giảm {chg_7d:+.2f}% trong tuần qua do diễn biến ngắn hạn của thị trường.",
                    "action": "Đánh giá lại tỷ trọng cổ phiếu trụ của quỹ (FPT, Ngân hàng). Không cần cắt lỗ nếu tầm nhìn đầu tư trên 2 năm."
                })
            elif chg_30d >= self.NAV_SURGE_30D_THRESHOLD:
                alerts.append({
                    "level": "MEDIUM",
                    "code": "nav_surge_30d",
                    "title": f"🎯 HIỆU SUẤT TĂNG TỐC: Tăng {chg_30d:+.2f}% trong 30 ngày",
                    "message": f"Quỹ đạt mức tăng trưởng nóng {chg_30d:+.2f}% trong vòng 1 tháng qua.",
                    "action": "Nếu có mục tiêu chi tiêu ngắn hạn, bạn có thể cân nhắc hiện thực hóa một phần lợi nhuận hoặc tiếp tục nắm giữ."
                })

        # 3. Cảnh báo Tỷ giá USD
        if forex_data and "USD" in forex_data:
            usd_sell_str = forex_data["USD"].get("sell", "0")
            try:
                usd_sell = float(str(usd_sell_str).replace(",", "").replace(".", "").strip())
                # Xử lý trường hợp chuỗi có thể là 26.160 hoặc 26160
                if usd_sell < 1000:
                    usd_sell *= 1000
                if usd_sell >= self.USD_HIGH_PRESSURE:
                    alerts.append({
                        "level": "MEDIUM",
                        "code": "usd_pressure",
                        "title": f"💵 CẢNH BÁO TỶ GIÁ: USD/VND vượt {usd_sell:,.0f} đ",
                        "message": "Tỷ giá USD/VND ở mức cao làm gia tăng áp lực rút vốn của khối ngoại trên thị trường chứng khoán.",
                        "action": "Theo dõi động thái điều hành hút tiền qua tín phiếu của Ngân hàng Nhà nước (SBV)."
                    })
            except Exception as e:
                logger.warning("[AlertManager] Lỗi phân tích tỷ giá USD: %s", e)

        return alerts

    @staticmethod
    def format_alerts_html(alerts: List[Dict[str, Any]]) -> str:
        """Định dạng danh sách cảnh báo thành văn bản HTML gửi qua Telegram."""
        if not alerts:
            return "✅ <b>Không có cảnh báo rủi ro đột biến. Thị trường đang trong tầm kiểm soát ổn định.</b>"

        lines = ["🚨 <b>CẢNH BÁO BIẾN ĐỘNG THỊ TRƯỜNG:</b>\n"]
        for alert in alerts:
            lines.append(f"<b>{alert['title']}</b>")
            lines.append(f"• <i>Chi tiết:</i> {alert['message']}")
            lines.append(f"• 💡 <i>Hành động đề xuất:</i> {alert['action']}\n")

        return "\n".join(lines).strip()
