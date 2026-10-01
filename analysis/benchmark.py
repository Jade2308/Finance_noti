"""
Benchmark Analyzer - So sánh hiệu suất danh mục với 4 kênh đầu tư phổ biến:
1. Lãi suất tiết kiệm ngân hàng (phi rủi ro)
2. VN-Index (thị trường chứng khoán chung)
3. Vàng SJC
4. Giữ tiền mặt (lạm phát CPI)
"""

from typing import Dict, Any, List, Optional
from datetime import date


class BenchmarkAnalyzer:
    """So sánh hiệu suất danh mục quỹ với các kênh đầu tư thay thế."""

    @staticmethod
    def compare_vs_bank(
        invested: float,
        pnl_pct: float,
        bank_rate_12m: float,
        holding_days: int
    ) -> Dict[str, Any]:
        """
        So sánh lợi nhuận thực tế của quỹ với gửi tiết kiệm ngân hàng cùng kỳ.

        Args:
            invested: Số tiền đầu tư ban đầu (VNĐ)
            pnl_pct: % lãi/lỗ thực tế của quỹ
            bank_rate_12m: Lãi suất tiết kiệm 12 tháng (%/năm, ví dụ: 4.6)
            holding_days: Số ngày nắm giữ

        Returns:
            dict với fund_return, bank_return, alpha, verdict
        """
        years = holding_days / 365.25
        # Lãi kép ngân hàng
        bank_return_pct = ((1 + bank_rate_12m / 100) ** years - 1) * 100
        bank_return_vnd = invested * (bank_return_pct / 100)
        fund_return_vnd = invested * (pnl_pct / 100)
        alpha_vnd = fund_return_vnd - bank_return_vnd
        alpha_pct = pnl_pct - bank_return_pct

        if alpha_pct > 2.0:
            verdict = f"✅ Quỹ vượt trội hơn NH {alpha_pct:+.2f}% ({alpha_vnd:+,.0f}đ)"
        elif alpha_pct >= 0:
            verdict = f"😐 Quỹ nhỉnh hơn NH một chút ({alpha_pct:+.2f}%)"
        elif alpha_pct >= -2.0:
            verdict = f"⚠️ Quỹ kém NH một chút ({alpha_pct:+.2f}%). Cân nhắc lại."
        else:
            verdict = f"❌ Quỹ thua NH {alpha_pct:+.2f}% ({alpha_vnd:+,.0f}đ). Gửi NH có lợi hơn!"

        return {
            "fund_return_pct": round(pnl_pct, 2),
            "fund_return_vnd": round(fund_return_vnd, 0),
            "bank_return_pct": round(bank_return_pct, 2),
            "bank_return_vnd": round(bank_return_vnd, 0),
            "alpha_pct": round(alpha_pct, 2),
            "alpha_vnd": round(alpha_vnd, 0),
            "verdict": verdict,
            "bank_rate_used": bank_rate_12m,
            "holding_years": round(years, 2)
        }

    @staticmethod
    def real_return_after_inflation(pnl_pct: float, cpi_annual_pct: float, holding_days: int) -> Dict[str, Any]:
        """
        Tính lợi nhuận thực (real return) sau lạm phát theo Fisher equation.

        Real Return = (1 + nominal) / (1 + inflation) - 1

        Args:
            pnl_pct: % lãi/lỗ danh nghĩa
            cpi_annual_pct: Lạm phát trung bình %/năm (ví dụ: 3.5)
            holding_days: Số ngày nắm giữ

        Returns:
            dict với real_return_pct, inflation_cost_pct, verdict
        """
        years = holding_days / 365.25
        # Lạm phát tích lũy trong kỳ nắm giữ
        cumulative_inflation = ((1 + cpi_annual_pct / 100) ** years - 1) * 100

        # Fisher equation
        nominal = pnl_pct / 100
        inflation = cpi_annual_pct / 100
        # Lạm phát tích lũy theo kỳ
        cumulative_infl_rate = (1 + inflation) ** years - 1
        real_return = ((1 + nominal) / (1 + cumulative_infl_rate) - 1) * 100

        if real_return > 1.0:
            verdict = f"✅ Bảo toàn sức mua + lãi thực {real_return:.2f}%"
        elif real_return >= 0:
            verdict = f"😐 Vừa đủ bảo toàn sức mua (lãi thực {real_return:.2f}%)"
        else:
            verdict = f"❌ Mất sức mua {real_return:.2f}% sau lạm phát!"

        return {
            "nominal_return_pct": round(pnl_pct, 2),
            "cumulative_inflation_pct": round(cumulative_inflation, 2),
            "real_return_pct": round(real_return, 2),
            "verdict": verdict,
            "cpi_used": cpi_annual_pct
        }

    @staticmethod
    def generate_benchmark_summary(
        transactions: List[Dict[str, Any]],
        bank_rate_12m: float,
        cpi_annual_pct: float = 3.5
    ) -> str:
        """
        Tạo đoạn văn bản tóm tắt benchmark cho toàn bộ danh mục.
        Dùng để đưa vào báo cáo Telegram hoặc prompt cho AI.
        """
        lines = ["📊 <b>SO SÁNH VỚI CÁC KÊNH ĐẦU TƯ:</b>"]
        for tx in transactions:
            invested = tx.get("invested", 0)
            pnl_pct = tx.get("pnl_pct", 0)
            buy_date = tx.get("date", "2023-01-01")
            tx_idx = tx.get("tx_index", 1)

            try:
                holding_days = (date.today() - date.fromisoformat(buy_date)).days
            except Exception:
                holding_days = 365

            bank_cmp = BenchmarkAnalyzer.compare_vs_bank(
                invested=invested,
                pnl_pct=pnl_pct,
                bank_rate_12m=bank_rate_12m,
                holding_days=holding_days
            )
            real_ret = BenchmarkAnalyzer.real_return_after_inflation(
                pnl_pct=pnl_pct,
                cpi_annual_pct=cpi_annual_pct,
                holding_days=holding_days
            )

            lines.append(f"\n<i>Lệnh {tx_idx} ({buy_date}, {bank_cmp['holding_years']:.1f} năm):</i>")
            lines.append(f"  • {bank_cmp['verdict']}")
            lines.append(f"  • {real_ret['verdict']}")

        lines.append(f"\n<i>Lãi suất NH tham chiếu: {bank_rate_12m}%/năm | CPI ước tính: {cpi_annual_pct}%/năm</i>")
        return "\n".join(lines)
