"""
Investment Comparator - So sánh trực quan giữa các kênh đầu tư tài chính phổ biến:
1. Quỹ mở Cổ phiếu (VinaCapital VEOF / VESAF)
2. Gửi tiết kiệm Ngân hàng (Vietcombank 12M)
3. Vàng miếng SJC
4. Giữ tiền mặt (ảnh hưởng lạm phát CPI)
"""

from typing import Dict, Any, List


class InvestmentComparator:
    """So sánh lợi nhuận và rủi ro giữa các kênh tài sản phổ biến tại Việt Nam."""

    @staticmethod
    def compare_channels(
        initial_capital: float = 1_000_000.0,
        years: int = 3,
        bank_rate_pct: float = 4.6,
        fund_return_pct: float = 12.0,
        gold_return_pct: float = 9.5,
        inflation_pct: float = 3.5,
    ) -> Dict[str, Any]:
        """
        So sánh một khoản tiền đầu tư một lần (Lump-sum) qua 4 kênh trong X năm.
        """
        # 1. Quỹ mở
        fund_fv = initial_capital * ((1.0 + fund_return_pct / 100.0) ** years)
        fund_profit = fund_fv - initial_capital

        # 2. Ngân hàng
        bank_fv = initial_capital * ((1.0 + bank_rate_pct / 100.0) ** years)
        bank_profit = bank_fv - initial_capital

        # 3. Vàng SJC
        gold_fv = initial_capital * ((1.0 + gold_return_pct / 100.0) ** years)
        gold_profit = gold_fv - initial_capital

        # 4. Tiền mặt (Sức mua thực tế bị lạm phát bào mòn)
        cash_real_power = initial_capital / ((1.0 + inflation_pct / 100.0) ** years)
        cash_loss = initial_capital - cash_real_power

        channels = [
            {
                "name": "Quỹ mở Cổ phiếu (VEOF/VESAF)",
                "icon": "🏢",
                "annual_rate": fund_return_pct,
                "fv": round(fund_fv, 0),
                "profit": round(fund_profit, 0),
                "risk": "Trung bình - Cao (Biến động theo chu kỳ)",
                "suitable_for": "Tích sản dài hạn (>2 năm), chịu được rung lắc ngắn hạn",
            },
            {
                "name": "Vàng miếng SJC",
                "icon": "🥇",
                "annual_rate": gold_return_pct,
                "fv": round(gold_fv, 0),
                "profit": round(gold_profit, 0),
                "risk": "Thấp - Trung bình (Chênh lệch mua-bán cao)",
                "suitable_for": "Phòng hộ rủi ro vĩ mô, mất giá tiền tệ",
            },
            {
                "name": "Gửi tiết kiệm Ngân hàng",
                "icon": "🏦",
                "annual_rate": bank_rate_pct,
                "fv": round(bank_fv, 0),
                "profit": round(bank_profit, 0),
                "risk": "Rất thấp (Phi rủi ro danh nghĩa)",
                "suitable_for": "Quỹ khẩn cấp, chi tiêu trong 3-12 tháng tới",
            },
            {
                "name": "Giữ tiền mặt / Tài khoản thanh toán",
                "icon": "📉",
                "annual_rate": -inflation_pct,
                "fv": round(cash_real_power, 0),
                "profit": -round(cash_loss, 0),
                "risk": "Lạm phát âm thầm bào mòn sức mua mỗi năm",
                "suitable_for": "Chi tiêu sinh hoạt hàng ngày",
            },
        ]

        return {
            "initial_capital": initial_capital,
            "years": years,
            "inflation_pct": inflation_pct,
            "channels": channels,
        }

    @staticmethod
    def format_comparison_html(comp_data: Dict[str, Any]) -> str:
        """Định dạng kết quả so sánh thành tin nhắn Telegram HTML."""
        cap = comp_data["initial_capital"]
        years = comp_data["years"]

        lines = [
            "⚖️ <b>SO SÁNH CÁC KÊNH ĐẦU TƯ TẠI VIỆT NAM</b>",
            f"<i>Giả định vốn ban đầu: {cap:,.0f} đ | Thời gian: {years} năm</i>",
            "─────────────────────",
        ]

        for ch in comp_data["channels"]:
            p_sign = "+" if ch["profit"] >= 0 else ""
            lines.append(f"{ch['icon']} <b>{ch['name']}</b>")
            lines.append(f"  • Kỳ vọng: <b>{ch['annual_rate']:+.1f}%/năm</b>")
            lines.append(f"  • Giá trị sau {years} năm: <b>{ch['fv']:,.0f} đ</b> ({p_sign}{ch['profit']:,.0f} đ)")
            lines.append(f"  • Mức độ rủi ro: <i>{ch['risk']}</i>")
            lines.append(f"  • Phù hợp với: {ch['suitable_for']}\n")

        lines.append(
            "> 📌 <b>Chiến lược phân bổ thông minh cho sinh viên:</b>\n"
            "> • <b>70%</b>: Quỹ mở cổ phiếu (tăng trưởng tài sản)\n"
            "> • <b>30%</b>: Tiền gửi ngân hàng (quỹ dự phòng sự cố 3-6 tháng sinh hoạt)\n"
            "> • Không nên giữ tiền mặt nhàn rỗi quá nhiều vì lạm phát ~3.5%/năm!"
        )

        return "\n".join(lines)
