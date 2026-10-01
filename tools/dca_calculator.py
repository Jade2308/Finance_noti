"""
DCA Calculator - Công cụ tính toán kế hoạch tích lũy trung bình giá (Dollar-Cost Averaging).
Hỗ trợ tính toán lãi kép, so sánh với gửi ngân hàng, khấu trừ lạm phát và lập kế hoạch mục tiêu.
"""

from typing import Dict, Any


class DCACalculator:
    """Tính toán hiệu quả chiến lược tích lũy định kỳ (DCA)."""

    @staticmethod
    def calculate_dca_plan(
        monthly_amount: float,
        years: int = 3,
        annual_return_pct: float = 12.0,
        bank_rate_pct: float = 4.6,
        inflation_pct: float = 3.5,
    ) -> Dict[str, Any]:
        """
        Tính toán kết quả chiến lược DCA hàng tháng.

        Args:
            monthly_amount: Số tiền đầu tư đều đặn mỗi tháng (VNĐ)
            years: Số năm đầu tư (mặc định 3 năm)
            annual_return_pct: Tỷ suất sinh lời kỳ vọng hàng năm (%/năm, ví dụ quỹ cổ phiếu ~12%)
            bank_rate_pct: Lãi suất tiết kiệm ngân hàng tham chiếu (%/năm, ví dụ ~4.6%)
            inflation_pct: Lạm phát dự kiến (%/năm, ví dụ ~3.5%)

        Returns:
            Dict chứa tổng tiền vốn, giá trị tương lai quỹ, gửi ngân hàng, lãi và giá trị thực sau lạm phát.
        """
        total_months = max(1, int(years * 12))
        total_invested = monthly_amount * total_months

        # 1. Tính giá trị tương lai đầu tư quỹ (Lãi kép gộp theo tháng - Annuity Due)
        r_fund_month = (annual_return_pct / 100.0) / 12.0
        if r_fund_month > 0:
            fv_fund = monthly_amount * (((1 + r_fund_month) ** total_months - 1) / r_fund_month) * (1 + r_fund_month)
        else:
            fv_fund = total_invested

        fund_profit = fv_fund - total_invested
        fund_roi_pct = (fund_profit / total_invested * 100.0) if total_invested > 0 else 0.0

        # 2. Tính giá trị nếu gửi tiết kiệm ngân hàng
        r_bank_month = (bank_rate_pct / 100.0) / 12.0
        if r_bank_month > 0:
            fv_bank = monthly_amount * (((1 + r_bank_month) ** total_months - 1) / r_bank_month) * (1 + r_bank_month)
        else:
            fv_bank = total_invested

        bank_profit = fv_bank - total_invested
        alpha_vs_bank = fv_fund - fv_bank

        # 3. Giá trị thực sau lạm phát (Real Purchasing Power)
        cum_inflation = (1 + inflation_pct / 100.0) ** years
        real_purchasing_power = fv_fund / cum_inflation if cum_inflation > 0 else fv_fund

        return {
            "monthly_amount": monthly_amount,
            "years": years,
            "total_months": total_months,
            "total_invested": round(total_invested, 0),
            "annual_return_pct": annual_return_pct,
            "fv_fund": round(fv_fund, 0),
            "fund_profit": round(fund_profit, 0),
            "fund_roi_pct": round(fund_roi_pct, 2),
            "bank_rate_pct": bank_rate_pct,
            "fv_bank": round(fv_bank, 0),
            "bank_profit": round(bank_profit, 0),
            "alpha_vs_bank": round(alpha_vs_bank, 0),
            "inflation_pct": inflation_pct,
            "real_purchasing_power": round(real_purchasing_power, 0),
        }

    @staticmethod
    def calculate_target_goal(
        target_amount: float,
        years: int = 3,
        annual_return_pct: float = 12.0,
    ) -> Dict[str, Any]:
        """
        Tính số tiền cần trích mỗi tháng để đạt được số tiền mục tiêu trong X năm.
        """
        total_months = max(1, int(years * 12))
        r_month = (annual_return_pct / 100.0) / 12.0

        if r_month > 0:
            # FV = PMT * [((1+r)^n - 1)/r] * (1+r)
            # PMT = FV / ([((1+r)^n - 1)/r] * (1+r))
            factor = (((1 + r_month) ** total_months - 1) / r_month) * (1 + r_month)
            required_monthly = target_amount / factor
        else:
            required_monthly = target_amount / total_months

        total_invested = required_monthly * total_months
        total_interest = target_amount - total_invested

        return {
            "target_amount": target_amount,
            "years": years,
            "total_months": total_months,
            "required_monthly": round(required_monthly, 0),
            "total_invested": round(total_invested, 0),
            "total_interest": round(total_interest, 0),
            "interest_pct": round((total_interest / target_amount * 100.0) if target_amount > 0 else 0, 1),
        }

    @staticmethod
    def format_dca_html(plan: Dict[str, Any]) -> str:
        """Định dạng kết quả tính toán DCA thành tin nhắn HTML đẹp cho Telegram."""
        return (
            "🧮 <b>BẢNG TÍNH KẾ HOẠCH TÍCH LŨY DCA</b>\n"
            "─────────────────────\n"
            f"• Số tiền tích lũy: <b>{plan['monthly_amount']:,.0f} đ/tháng</b>\n"
            f"• Thời gian đầu tư: <b>{plan['years']} năm ({plan['total_months']} tháng)</b>\n"
            f"• Tổng vốn bạn bỏ ra: <b>{plan['total_invested']:,.0f} đ</b>\n\n"
            f"📈 <b>1. Kênh Quỹ mở cổ phiếu (Kỳ vọng {plan['annual_return_pct']}%/năm):</b>\n"
            f"  • Tổng tài sản nhận về: <b>{plan['fv_fund']:,.0f} đ</b>\n"
            f"  • Tiền lời từ lãi kép: <b>+{plan['fund_profit']:,.0f} đ (+{plan['fund_roi_pct']}%)</b>\n"
            f"  • Sức mua thực (trừ lạm phát {plan['inflation_pct']}%): <b>~{plan['real_purchasing_power']:,.0f} đ</b>\n\n"
            f"🏦 <b>2. Nếu chỉ gửi tiết kiệm ngân hàng ({plan['bank_rate_pct']}%/năm):</b>\n"
            f"  • Tổng tài sản nhận về: <b>{plan['fv_bank']:,.0f} đ</b>\n"
            f"  • Tiền lãi: <b>+{plan['bank_profit']:,.0f} đ</b>\n"
            f"  • Chênh lệch so với Quỹ: <b>{'+' if plan['alpha_vs_bank'] >= 0 else ''}{plan['alpha_vs_bank']:,.0f} đ</b>\n\n"
            "> 💡 <b>Lời khuyên:</b> Với số vốn nhỏ, DCA đều đặn là vũ khí mạnh nhất của sinh viên. "
            "Lãi kép cần thời gian để phát huy sức mạnh vượt trội so với giữ tiền mặt."
        )
