"""
News Collector - Trình thu thập tin tức tài chính thị trường.
Lấy dữ liệu từ RSS Feeds (CafeF / VNExpress).
"""

import logging
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class NewsCollector:
    """Thu thập tin tức tài chính - kinh tế nóng hổi nhất."""

    def get_latest_financial_news(self, limit: int = 5) -> List[Dict[str, str]]:
        """
        Lấy các tin tức mới nhất từ đa nguồn RSS (CafeF, VNExpress) để tránh thiên lệch.
        """
        rss_sources = [
            {"name": "CafeF", "url": "https://cafef.vn/trang-chu.rss"},
            {"name": "VNExpress", "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
        ]

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

        all_news: List[Dict[str, str]] = []

        for source in rss_sources:
            try:
                response = requests.get(source["url"], headers=headers, timeout=5)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    # Lấy 3 tin đầu mỗi báo để mix
                    for item in root.findall(".//item")[:3]:
                        title_elem = item.find("title")
                        link_elem = item.find("link")

                        if title_elem is not None and link_elem is not None:
                            title = title_elem.text.strip() if title_elem.text else ""
                            link = link_elem.text.strip() if link_elem.text else ""
                            all_news.append({
                                "source": source["name"],
                                "title": f"[{source['name']}] {title}",
                                "link": link,
                            })
            except Exception as e:
                logger.warning("[NewsCollector] Lỗi khi lấy tin tức từ %s: %s", source["name"], e)

        # Trả về giới hạn số lượng tin tổng cộng
        return all_news[:limit]
