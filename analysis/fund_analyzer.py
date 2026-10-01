"""
Fund Analyzer - Tính toán lợi nhuận, hiệu suất danh mục và xu hướng NAV quỹ mở.
"""

from typing import List, Dict, Any, Optional
import pandas as pd


class FundAnalyzer:
    """Phân tích danh mục quỹ mở và đánh giá xu hướng biến động."""

    @staticmethod
    def calculate_cagr(pnl_pct: float, buy_date_str: str) -> dict:
        """
        Tính CAGR (Compound Annual Growth Rate) — Lợi nhuận tăng trưởng kép hàng năm.
        
        Công thức: CAGR = (1 + total_return) ^ (1 / years) - 1
        
        Args:
            pnl_pct: % lãi/lỗ tổng (ví dụ: 40.0 cho 40%)
            buy_date_str: Ngày mua dạng "YYYY-MM-DD"
        
        Returns:
            dict với cagr_pct (float) và holding_days (int)
        """
        from datetime import date
        try:
            buy_date = date.fromisoformat(buy_date_str)
            today = date.today()
            holding_days = (today - buy_date).days
            
            if holding_days < 30:
                # Quá ngắn để có ý nghĩa — trả về tổng return
                return {
                    "cagr_pct": pnl_pct,
                    "holding_days": holding_days,
                    "holding_years": round(holding_days / 365.25, 2),
                    "note": "Nắm giữ < 30 ngày, CAGR chưa có ý nghĩa"
                }
            
            years = holding_days / 365.25
            total_return = pnl_pct / 100.0
            cagr = ((1 + total_return) ** (1.0 / years) - 1) * 100
            
            return {
                "cagr_pct": round(cagr, 2),
                "holding_days": holding_days,
                "holding_years": round(years, 2),
                "note": f"Nắm giữ {holding_days} ngày ({years:.1f} năm)"
            }
        except Exception as e:
            return {
                "cagr_pct": pnl_pct,
                "holding_days": 0,
                "holding_years": 0,
                "note": f"Lỗi tính CAGR: {e}"
            }

    @staticmethod
    def analyze_portfolio(portfolio_config: List[Dict[str, Any]], current_navs: Dict[str, float]) -> Dict[str, Any]:
        """
        Tính toán hiệu suất danh mục dựa trên NAV mới nhất.

        Args:
            portfolio_config: Cấu hình danh mục từ settings.py
            current_navs: Dict mã quỹ -> NAV hiện tại, ví dụ: {"VEOF": 32191.35}

        Returns:
            Dict chứa phân tích chi tiết từng quỹ, từng lệnh mua và tổng thể danh mục.
        """
        funds_analysis = []
        overall_invested = 0.0
        overall_current_value = 0.0

        for fund in portfolio_config:
            fund_code = fund["fund_code"]
            fund_name = fund.get("fund_name", fund_code)
            current_nav = current_navs.get(fund_code, 0.0)

            total_units = fund.get("total_units", 0.0)
            fund_invested = fund.get("total_invested", 0.0)
            fund_current_val = round(total_units * current_nav, 2)
            fund_pnl = round(fund_current_val - fund_invested, 2)
            fund_pnl_pct = round((fund_pnl / fund_invested * 100) if fund_invested > 0 else 0.0, 2)

            # Phân tích từng lệnh mua riêng lẻ
            tx_details = []
            for idx, tx in enumerate(fund.get("transactions", []), start=1):
                units = tx["units"]
                buy_price = tx["buy_price"]
                invested = tx["invested"]
                cur_val = round(units * current_nav, 2)
                pnl = round(cur_val - invested, 2)
                pnl_pct = round((pnl / invested * 100) if invested > 0 else 0.0, 2)
                cagr_info = FundAnalyzer.calculate_cagr(pnl_pct, tx["date"])

                tx_details.append({
                    "tx_index": idx,
                    "date": tx["date"],
                    "units": units,
                    "buy_price": buy_price,
                    "invested": invested,
                    "current_value": cur_val,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "cagr_pct": cagr_info["cagr_pct"],
                    "holding_days": cagr_info["holding_days"],
                    "holding_years": cagr_info["holding_years"],
                })

            funds_analysis.append({
                "fund_code": fund_code,
                "fund_name": fund_name,
                "current_nav": current_nav,
                "total_units": total_units,
                "total_invested": fund_invested,
                "current_value": fund_current_val,
                "pnl": fund_pnl,
                "pnl_pct": fund_pnl_pct,
                "transactions": tx_details
            })

            overall_invested += fund_invested
            overall_current_value += fund_current_val

        overall_pnl = round(overall_current_value - overall_invested, 2)
        overall_pnl_pct = round((overall_pnl / overall_invested * 100) if overall_invested > 0 else 0.0, 2)

        return {
            "funds": funds_analysis,
            "overall_invested": overall_invested,
            "overall_current_value": overall_current_value,
            "overall_pnl": overall_pnl,
            "overall_pnl_pct": overall_pnl_pct
        }

    @staticmethod
    def analyze_nav_trend(nav_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phân tích xu hướng NAV từ lịch sử giá.
        
        Args:
            nav_history: Danh sách dict [{'nav_date': ..., 'nav': ...}, ...] tăng dần theo ngày.
        """
        if not nav_history or len(nav_history) < 2:
            latest_nav = nav_history[-1]["nav"] if nav_history else 0.0
            return {
                "latest_nav": latest_nav,
                "change_7d_pct": 0.0,
                "change_30d_pct": 0.0,
                "description": "Chưa đủ dữ liệu lịch sử để đánh giá xu hướng dài hạn."
            }

        nav_values = [item["nav"] for item in nav_history]
        latest = nav_values[-1]

        # Tính % thay đổi 7 phiên gần nhất
        change_7d = 0.0
        if len(nav_values) >= 7:
            ref_7d = nav_values[-7]
            if ref_7d > 0:
                change_7d = round(((latest - ref_7d) / ref_7d) * 100, 2)

        # Tính % thay đổi 30 phiên gần nhất
        change_30d = 0.0
        if len(nav_values) >= 30:
            ref_30d = nav_values[-30]
            if ref_30d > 0:
                change_30d = round(((latest - ref_30d) / ref_30d) * 100, 2)
        elif len(nav_values) > 1:
            ref_first = nav_values[0]
            if ref_first > 0:
                change_30d = round(((latest - ref_first) / ref_first) * 100, 2)

        # Mô tả xu hướng bằng văn bản thân thiện
        if change_7d > 2.0:
            short_term = "tăng tích cực"
        elif change_7d > 0:
            short_term = "tăng nhẹ"
        elif change_7d > -2.0:
            short_term = "giảm nhẹ"
        else:
            short_term = "điều chỉnh giảm"

        description = (
            f"Trong 7 phiên gần đây, NAV {short_term} ({change_7d:+.2f}%). "
            f"Tính theo chu kỳ dài hơn (~30 phiên), hiệu suất đạt {change_30d:+.2f}%."
        )

        return {
            "latest_nav": latest,
            "change_7d_pct": change_7d,
            "change_30d_pct": change_30d,
            "description": description
        }
