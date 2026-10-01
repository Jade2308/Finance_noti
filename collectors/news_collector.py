"""
News Collector - Trình thu thập tin tức tài chính thị trường.
Lấy dữ liệu từ đa nguồn RSS uy tín: CafeF, VnEconomy, VNExpress, Tuổi Trẻ, Thanh Niên...
Hỗ trợ cơ chế Fallback parser (ElementTree -> BeautifulSoup), làm sạch HTML entity và Round-Robin chống thiên lệch.
"""

import html
import logging
import re
import warnings
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

# Tắt cảnh báo khi dùng html.parser đọc XML trên BeautifulSoup
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

logger = logging.getLogger(__name__)


class NewsCollector:
    """Thu thập tin tức tài chính - kinh tế nóng hổi từ đa nguồn uy tín nhất Việt Nam."""

    DEFAULT_SOURCES: List[Dict[str, str]] = [
        {
            "name": "CafeF",
            "category": "Chứng khoán",
            "url": "https://cafef.vn/thi-truong-chung-khoan.rss",
        },
        {
            "name": "VnEconomy",
            "category": "Tài chính",
            "url": "https://vneconomy.vn/tai-chinh.rss",
        },
        {
            "name": "VNExpress",
            "category": "Kinh doanh",
            "url": "https://vnexpress.net/rss/kinh-doanh.rss",
        },
        {
            "name": "CafeF",
            "category": "Ngân hàng",
            "url": "https://cafef.vn/tai-chinh-ngan-hang.rss",
        },
        {
            "name": "VnEconomy",
            "category": "Chứng khoán",
            "url": "https://vneconomy.vn/chung-khoan.rss",
        },
        {
            "name": "Tuổi Trẻ",
            "category": "Kinh tế",
            "url": "https://tuoitre.vn/rss/kinh-doanh.rss",
        },
        {
            "name": "Thanh Niên",
            "category": "Kinh tế",
            "url": "https://thanhnien.vn/rss/kinh-te.rss",
        },
    ]

    def __init__(self, sources: Optional[List[Dict[str, str]]] = None):
        self.sources = sources or self.DEFAULT_SOURCES
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Làm sạch định dạng: gỡ CDATA, giải mã HTML entities, bỏ tags HTML thừa."""
        if not text:
            return ""
        # Gỡ CDATA nếu có
        text = re.sub(r"^<!\[CDATA\[(.*)\]\]>$", r"\1", text.strip(), flags=re.DOTALL)
        # Giải mã các ký tự HTML (vd: &quot;, &#039;, &amp;, &aacute;,...)
        text = html.unescape(text)
        # Xóa các thẻ HTML
        text = re.sub(r"<[^>]+>", "", text)
        # Chuẩn hóa khoảng trắng
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _fetch_source_items(
        self, source: Dict[str, str], max_items: int = 5
    ) -> List[Dict[str, str]]:
        """Lấy danh sách tin từ một nguồn RSS, tự động fallback nếu XML không chuẩn."""
        name = source["name"]
        url = source["url"]
        category = source.get("category", "Tài chính")
        items_result: List[Dict[str, str]] = []

        try:
            response = requests.get(url, headers=self.headers, timeout=6)
            if response.status_code != 200:
                logger.warning(
                    "[NewsCollector] Nguồn %s (%s) trả về HTTP %s",
                    name,
                    url,
                    response.status_code,
                )
                return []

            content = response.content

            # Cách 1: Thử dùng ElementTree chuẩn (nhanh và chuẩn XML)
            parsed = False
            try:
                root = ET.fromstring(content)
                for item in root.findall(".//item"):
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    raw_title = (
                        title_elem.text if (title_elem is not None and title_elem.text) else ""
                    )
                    title = self._clean_text(raw_title)
                    link = (
                        link_elem.text.strip()
                        if (link_elem is not None and link_elem.text)
                        else ""
                    )

                    if title and link:
                        items_result.append(
                            {
                                "source": name,
                                "category": category,
                                "title": f"[{name}] {title}",
                                "raw_title": title,
                                "link": link,
                            }
                        )
                    if len(items_result) >= max_items:
                        break
                parsed = True
            except Exception as xml_err:
                logger.debug(
                    "[NewsCollector] ElementTree không phân tích được %s: %s. Chuyển sang BeautifulSoup.",
                    name,
                    xml_err,
                )

            # Cách 2: Fallback sang BeautifulSoup (html.parser) nếu XML chứa ký tự lạ
            if not parsed or not items_result:
                soup = BeautifulSoup(content, "html.parser")
                found_items = soup.find_all("item")
                for item in found_items:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    raw_title = title_elem.get_text(strip=True) if title_elem else ""
                    title = self._clean_text(raw_title)
                    link = link_elem.get_text(strip=True) if link_elem else ""
                    if not link and link_elem and link_elem.get("href"):
                        link = link_elem["href"].strip()

                    if title and link:
                        items_result.append(
                            {
                                "source": name,
                                "category": category,
                                "title": f"[{name}] {title}",
                                "raw_title": title,
                                "link": link,
                            }
                        )
                    if len(items_result) >= max_items:
                        break

        except Exception as e:
            logger.warning(
                "[NewsCollector] Lỗi kết nối tới nguồn %s (%s): %s", name, url, e
            )

        return items_result

    def get_latest_financial_news(self, limit: int = 5) -> List[Dict[str, str]]:
        """
        Lấy các tin tức mới nhất từ đa nguồn RSS uy tín.
        Sử dụng kỹ thuật round-robin (xen kẽ giữa các nguồn) và loại bỏ tin trùng lặp.
        """
        per_source_news: List[List[Dict[str, str]]] = []

        for source in self.sources:
            items = self._fetch_source_items(source, max_items=3)
            if items:
                per_source_news.append(items)

        if not per_source_news:
            return []

        combined_news: List[Dict[str, str]] = []
        seen_titles = set()
        seen_links = set()

        # Round-robin: Lấy tin số 0 của mỗi báo, rồi đến tin số 1, số 2...
        max_depth = max(len(items) for items in per_source_news)
        for depth in range(max_depth):
            for source_list in per_source_news:
                if depth < len(source_list):
                    item = source_list[depth]
                    # Chuẩn hóa để nhận diện tin trùng lặp
                    norm_title = re.sub(r"\W+", "", item["raw_title"].lower())
                    if norm_title in seen_titles or item["link"] in seen_links:
                        continue
                    seen_titles.add(norm_title)
                    seen_links.add(item["link"])
                    combined_news.append(item)
                    if len(combined_news) >= limit:
                        return combined_news

        return combined_news[:limit]
