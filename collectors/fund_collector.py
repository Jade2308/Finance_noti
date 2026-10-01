"""
Fund Data Collector - Thu thập giá trị tài sản ròng (NAV) của quỹ mở.
Tích hợp đa tầng: Vnstock API, VinaCapital AJAX Endpoint và cơ chế Fallback an toàn.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests
import json

logger = logging.getLogger(__name__)


class FundDataCollector:
    """Thu thập dữ liệu NAV và danh mục của quỹ mở (mặc định VEOF)."""

    def __init__(self, db_instance=None):
        self.db = db_instance
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/javascript, */*; q=0.01",
        })

    def get_fund_nav(self, fund_code: str = "VEOF") -> Dict[str, Any]:
        """
        Lấy giá NAV mới nhất của quỹ.
        Thử theo thứ tự:
        1. Vnstock Market().fund().nav() (chính thức từ Fmarket, cực kỳ đầy đủ)
        2. VinaCapital AJAX API
        3. Cache từ Database / Mặc định
        """
        fund_code = fund_code.upper()

        # Cách 1: Thử qua Vnstock
        try:
            vnstock_data = self._fetch_vnstock_nav(fund_code)
            if vnstock_data:
                if self.db:
                    self.db.save_nav(
                        fund_code=fund_code,
                        nav=vnstock_data["nav"],
                        nav_date=vnstock_data["date"],
                        source="vnstock"
                    )
                return {
                    "fund_code": fund_code,
                    "nav": vnstock_data["nav"],
                    "date": vnstock_data["date"],
                    "source": "vnstock"
                }
        except Exception as e:
            logger.warning("[FundCollector] Vnstock fund error: %s", e)

        # Cách 2: VinaCapital Endpoint
        try:
            vc_data = self._fetch_vinacapital_nav(fund_code)
            if vc_data:
                if self.db:
                    self.db.save_nav(
                        fund_code=fund_code,
                        nav=vc_data["nav"],
                        nav_date=vc_data["date"],
                        source="vinacapital_api"
                    )
                return {
                    "fund_code": fund_code,
                    "nav": vc_data["nav"],
                    "date": vc_data["date"],
                    "source": "vinacapital_api"
                }
        except Exception as e:
            logger.warning("[FundCollector] VinaCapital API error: %s", e)

        # Cách 3: Fallback qua database cache
        if self.db:
            cached = self.db.get_latest_nav(fund_code)
            if cached:
                return {
                    "fund_code": fund_code,
                    "nav": float(cached["nav"]),
                    "date": cached["nav_date"],
                    "source": "database_cache"
                }

        # Cách 4: Snapshot tham chiếu — chỉ dùng khi tất cả nguồn đều thất bại
        # NAV tham chiếu được cập nhật thủ công định kỳ (Q3/2026)
        FALLBACK_NAV_DEFAULTS = {
            "VEOF": 30745.09,
            "VESAF": 28000.0,   # Ước tính — cần cập nhật thủ công
            "VIBF": 15000.0,    # Ước tính — cần cập nhật thủ công
            "VFF": 12000.0,     # Ước tính — cần cập nhật thủ công
        }
        fallback_nav = FALLBACK_NAV_DEFAULTS.get(fund_code, 20000.0)
        fallback_date = datetime.now().strftime("%Y-%m-%d")
        logger.error("[FundCollector] Tất cả nguồn đều thất bại cho %s. Dùng snapshot NAV=%.2f", fund_code, fallback_nav)
        return {
            "fund_code": fund_code,
            "nav": fallback_nav,
            "date": fallback_date,
            "source": "default_snapshot",
            "warning": f"⚠️ Không lấy được NAV từ bất kỳ nguồn nào. Đang dùng snapshot tham chiếu cũ ({fallback_nav:,.0f}đ). Số liệu lãi/lỗ có thể không chính xác!"
        }

    def _fetch_vnstock_nav(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu qua vnstock."""
        try:
            from vnstock import Market
            m = Market()
            fund_obj = m.fund(fund_code)
            nav_df = fund_obj.nav()
            if nav_df is not None and not nav_df.empty:
                latest = nav_df.iloc[-1]
                nav_col = "nav_per_unit" if "nav_per_unit" in nav_df.columns else ("nav" if "nav" in nav_df.columns else nav_df.columns[-1])
                date_col = "date" if "date" in nav_df.columns else nav_df.columns[0]
                return {
                    "nav": float(latest[nav_col]),
                    "date": str(latest[date_col])
                }
        except Exception as e:
            logger.warning("[FundCollector _fetch_vnstock_nav] %s", e)
        return None

    def _fetch_vinacapital_nav(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """Gửi request tới API AJAX của VinaCapital."""
        url = "https://vinacapital.com/wp-admin/admin-ajax.php"
        data = {
            "action": "getchartfundnav",
            "fundname": fund_code
        }
        resp = self.session.post(url, data=data, timeout=8)
        if resp.status_code == 200:
            result = resp.json()
            if isinstance(result, list) and len(result) > 0:
                for item in reversed(result):
                    nav_val = item.get("nav") or item.get("value")
                    date_val = item.get("date") or item.get("time")
                    if nav_val is not None:
                        return {
                            "nav": float(nav_val),
                            "date": str(date_val)
                        }
        return None

    def get_nav_history(self, fund_code: str = "VEOF", limit: int = 30) -> List[Dict[str, Any]]:
        """Lấy lịch sử NAV để tính xu hướng 7 ngày / 30 ngày."""
        fund_code = fund_code.upper()

        # 1. Thử lấy từ Vnstock trước
        try:
            from vnstock import Market
            m = Market()
            nav_df = m.fund(fund_code).nav()
            if nav_df is not None and not nav_df.empty:
                nav_col = "nav_per_unit" if "nav_per_unit" in nav_df.columns else ("nav" if "nav" in nav_df.columns else nav_df.columns[-1])
                date_col = "date" if "date" in nav_df.columns else nav_df.columns[0]

                recent_df = nav_df.tail(limit)
                history = []
                for _, row in recent_df.iterrows():
                    history.append({
                        "fund_code": fund_code,
                        "nav": float(row[nav_col]),
                        "nav_date": str(row[date_col])
                    })
                return history
        except Exception as e:
            logger.warning("[FundCollector] Lỗi lấy lịch sử NAV từ Vnstock: %s", e)

        # 2. Thử lấy từ DB
        if self.db:
            db_history = self.db.get_nav_history(fund_code, limit=limit)
            if db_history:
                return db_history

        # Fallback danh sách tối thiểu
        cur = self.get_fund_nav(fund_code)
        return [{"fund_code": fund_code, "nav": cur["nav"], "nav_date": cur["date"]}]

    def get_top_holdings(self, fund_code: str = "VEOF") -> List[Dict[str, Any]]:
        """Lấy danh mục top cổ phiếu quỹ đang nắm giữ nhiều nhất."""
        fund_code = fund_code.upper()
        try:
            from vnstock import Market
            m = Market()
            df = m.fund(fund_code).top_holding()
            if df is not None and not df.empty:
                holdings = []
                for _, row in df.head(10).iterrows():
                    holdings.append({
                        "stock_code": str(row.get("stock_code", "")),
                        "industry": str(row.get("industry", "")),
                        "net_asset_percent": float(row.get("net_asset_percent", 0.0)) if "net_asset_percent" in row else None
                    })
                return holdings
        except Exception as e:
            logger.warning("[FundCollector] Lỗi lấy top holdings: %s", e)
        return []
