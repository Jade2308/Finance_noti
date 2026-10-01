"""
Interest Rate Collector - Thu thập lãi suất ngân hàng làm Benchmark.
"""

import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any

logger = logging.getLogger(__name__)


class InterestRateCollector:
    """Lấy dữ liệu lãi suất tiết kiệm ngân hàng (Vietcombank) làm tham chiếu an toàn."""

    def get_vcb_interest_rates(self) -> Dict[str, Any]:
        """
        Lấy lãi suất VNĐ dành cho khách hàng cá nhân.
        Nếu không lấy được từ API, sử dụng dữ liệu mặc định (Fallback).
        """
        url = "https://portal.vietcombank.com.vn/UserControls/TVPortal.TyGia/pXML.aspx?b=ls"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                rates = {}
                for item in root.findall("Rate"):
                    term = item.find("Term").text
                    value = item.find("Value").text
                    rates[term] = value

                # Tìm kỳ hạn 12 tháng làm Benchmark
                benchmark = rates.get("12 Tháng", "4.6")
                return {
                    "source": "Vietcombank",
                    "benchmark_12m": float(benchmark),
                    "details": rates,
                    "error": False,
                }
        except Exception as e:
            logger.warning("[InterestRateCollector] Lỗi lấy lãi suất VCB: %s", e)

        # Fallback rates (Lãi suất tương đối hiện tại năm 2026)
        logger.warning("[InterestRateCollector] Dùng lãi suất fallback 4.6%%/năm.")
        return {
            "source": "Fallback",
            "benchmark_12m": 4.6,
            "details": {
                "1 Tháng": "1.6",
                "3 Tháng": "1.9",
                "6 Tháng": "2.9",
                "12 Tháng": "4.6",
            },
            "error": True,
        }
