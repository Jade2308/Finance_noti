"""
Message Formatter - Định dạng tin nhắn gửi qua Telegram đẹp mắt bằng HTML.
Bao gồm: Danh mục Quỹ mở, Chỉ số VN-Index, Giá vàng SJC, Tỷ giá USD/VND và Nhận định AI.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class MessageFormatter:
    """Format các khối dữ liệu tài chính thành định dạng tin nhắn Telegram HTML."""

    @staticmethod
    def beautify_markdown_to_telegram(text: str) -> str:
        """
        Chuyển đổi cú pháp Markdown (bảng, header, bold, rule, quote) sang Telegram HTML thẩm mỹ cao.
        Tự động biến bảng Markdown thô (| col |) thành các Thẻ thông tin (Cards) trực quan cho điện thoại.
        """
        if not text:
            return text

        # 1. Chuyển đổi bảng Markdown (| col1 | col2 |) thành Thẻ thông tin (Cards)
        def replace_table(match):
            table_raw = match.group(0).strip()
            lines = [l.strip() for l in table_raw.split('\n') if l.strip()]
            if len(lines) < 2:
                return table_raw

            headers = [c.strip() for c in lines[0].split('|')[1:-1]]
            if not headers:
                return table_raw

            cards = []
            for line in lines[2:]:
                if '|' not in line:
                    continue
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) < len(headers):
                    continue

                item_raw = cells[0].replace('**', '').replace('*', '').strip()
                icon = '🔹'
                lower_item = item_raw.lower()
                if any(k in lower_item for k in ['vn-index', 'chỉ số', 'chứng khoán']):
                    icon = '📈'
                elif any(k in lower_item for k in ['vàng', 'sjc']):
                    icon = '🥇'
                elif any(k in lower_item for k in ['tỷ giá', 'usd', 'ngoại tệ']):
                    icon = '💵'
                elif any(k in lower_item for k in ['lãi suất', 'tiết kiệm', 'ngân hàng']):
                    icon = '🏦'
                elif any(k in lower_item for k in ['quỹ', 'veof', 'ccq']):
                    icon = '🏢'
                elif any(k in lower_item for k in ['lạm phát', 'cpi']):
                    icon = '📉'

                card_lines = [f'{icon} <b>{item_raw}</b>']
                for i in range(1, len(cells)):
                    h_name = headers[i].replace('**', '').replace('*', '').strip()
                    val = cells[i].strip()
                    val = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', val)
                    val = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', val)
                    card_lines.append(f'  • <i>{h_name}:</i> {val}')
                cards.append('\n'.join(card_lines))

            if cards:
                return '\n\n' + '\n\n'.join(cards) + '\n\n'
            return table_raw

        table_pattern = re.compile(r'((?:\|[^\n]+\|\r?\n){2,})', re.MULTILINE)
        text = table_pattern.sub(replace_table, text)

        # 2. Chuyển đổi Markdown Headers
        text = re.sub(r'^\s*###\s*(.+)$', r'\n📌 <b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*##\s*(.+)$', r'\n🏛 <b>\1</b>\n', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*#\s*(.+)$', r'\n📋 <b>\1</b>\n', text, flags=re.MULTILINE)

        # 3. Chuyển đổi đường kẻ ngang (---, ***, ___) thành thanh phân cách đẹp
        text = re.sub(r'^\s*[-*_]{3,}\s*$', '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', text, flags=re.MULTILINE)

        # 4. Chuyển đổi in đậm (**text** -> <b>text</b>)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # 5. Chuyển đổi in nghiêng (*text* hoặc _text_ -> <i>text</i>)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
        text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'<i>\1</i>', text)

        # 6. Chuyển đổi Blockquotes (> quote) thành <blockquote> của Telegram
        def replace_blockquotes(match):
            lines = [l.strip().lstrip('>').strip() for l in match.group(0).split('\n') if l.strip()]
            return '<blockquote>' + '\n'.join(lines) + '</blockquote>'
        text = re.sub(r'((?:^>[^\n]+\r?\n?)+)', replace_blockquotes, text, flags=re.MULTILINE)

        # 7. Chuẩn hóa bullet lists (- hoặc * thành •)
        text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)

        # 8. Dọn dẹp dòng trống thừa
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def format_daily_report(
        portfolio_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        nav_trend: Dict[str, Any],
        ai_commentary: str,
        gold_data: Optional[Dict[str, Any]] = None,
        forex_data: Optional[Dict[str, Any]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[List[Dict[str, str]]] = None,
        benchmark_summary: Optional[str] = None
    ) -> str:
        """Tạo bản tin tổng hợp hàng ngày hoàn chỉnh."""
        now_str = datetime.now().strftime("%d/%m/%Y - %H:%M")

        overall_pnl = portfolio_analysis.get("overall_pnl", 0.0)
        overall_pnl_pct = portfolio_analysis.get("overall_pnl_pct", 0.0)
        overall_status_emoji = "📈" if overall_pnl >= 0 else "📉"
        pnl_color_sign = "+" if overall_pnl >= 0 else ""

        # Header
        lines = [
            f"📋 <b>BÁO CÁO TÀI CHÍNH HÀNG NGÀY</b>",
            f"<i>Cập nhật: {now_str} (Asia/Ho_Chi_Minh)</i>",
            f"{'━' * 32}\n"
        ]

        # 1. Khối tổng quan danh mục
        lines.append("💼 <b>TỔNG QUAN DANH MỤC CỦA BẠN:</b>")
        lines.append(f"• Vốn ban đầu: <b>{portfolio_analysis.get('overall_invested', 0):,.0f} đ</b>")
        lines.append(f"• Giá trị hiện tại: <b>{portfolio_analysis.get('overall_current_value', 0):,.0f} đ</b>")
        lines.append(
            f"• Lợi nhuận: {overall_status_emoji} <b>{pnl_color_sign}{overall_pnl:,.0f} đ "
            f"({pnl_color_sign}{overall_pnl_pct:.2f}%)</b>\n"
        )

        # 2. Khối chi tiết từng quỹ & từng lệnh
        for fund in portfolio_analysis.get("funds", []):
            fund_pnl = fund.get("pnl", 0.0)
            fund_pnl_pct = fund.get("pnl_pct", 0.0)
            f_sign = "+" if fund_pnl >= 0 else ""
            f_emoji = "🟢" if fund_pnl >= 0 else "🔴"

            lines.append(f"🏢 <b>Quỹ {fund['fund_code']}</b> ({fund.get('fund_name', '')}):")
            lines.append(f"   • NAV mới nhất: <b>{fund.get('current_nav', 0):,.2f} đ</b>")
            lines.append(f"   • Số lượng sở hữu: <b>{fund.get('total_units', 0):.2f} CCQ</b>")
            lines.append(f"   • Hiệu suất quỹ: {f_emoji} <b>{f_sign}{fund_pnl:,.0f} đ ({f_sign}{fund_pnl_pct:.2f}%)</b>")

            # Liệt kê các lệnh mua
            for tx in fund.get("transactions", []):
                t_pnl = tx.get("pnl", 0.0)
                t_pnl_pct = tx.get("pnl_pct", 0.0)
                t_emoji = "✅" if t_pnl >= 0 else "🔻"
                t_sign = "+" if t_pnl >= 0 else ""
                cagr_str = f" | CAGR: {tx.get('cagr_pct', 0):+.2f}%/năm" if tx.get('holding_years', 0) >= 0.25 else ""
                holding_str = f" ({tx.get('holding_years', 0):.1f} năm)" if tx.get('holding_years', 0) >= 0.08 else ""
                lines.append(
                    f"      {t_emoji} <i>Lệnh {tx['tx_index']} ({tx['date']}){holding_str}</i>: "
                    f"Giá mua {tx['buy_price']:,.0f}đ | {t_sign}{t_pnl:,.0f}đ ({t_sign}{t_pnl_pct:.2f}%){cagr_str}"
                )
            lines.append("")

        # 3. Khối xu hướng NAV
        if nav_trend and nav_trend.get("description"):
            lines.append("📊 <b>BIẾN ĐỘNG NAV:</b>")
            lines.append(f"• {nav_trend['description']}\n")

        if benchmark_summary:
            lines.append(benchmark_summary)
            lines.append("")

        # 4. Khối liên thị trường (Chứng khoán, Vàng, Ngoại tệ)
        lines.append("🌍 <b>TỔNG QUAN LIÊN THỊ TRƯỜNG:</b>")
        if market_data and "error" not in market_data:
            idx_price = market_data.get("price", "N/A")
            idx_change = market_data.get("change", 0.0)
            idx_pct = market_data.get("change_pct", 0.0)
            idx_emoji = "🟢" if str(idx_change).startswith("+") or float(idx_change or 0) >= 0 else "🔴"
            pct_str = f"{idx_pct}" if str(idx_pct).endswith("%") else f"{idx_pct}%"
            lines.append(f"• 📈 <b>VN-Index:</b> <b>{idx_price}</b> ({idx_emoji} {idx_change}, {pct_str})")
            if "rsi_14" in market_data and market_data["rsi_14"] != "N/A":
                lines.append(f"   <i>Chỉ báo TA:</i> RSI: {market_data.get('rsi_14')} | MACD: {market_data.get('macd')} (Signal: {market_data.get('macd_signal')})")
            if sentiment_data and "score" in sentiment_data:
                lines.append(f"   🧠 <b>Tâm lý thị trường:</b> {sentiment_data['score']}/100 - {sentiment_data['label']}")
            if forecast_data and not forecast_data.get("error"):
                confidence = forecast_data.get("confidence", "N/A")
                confidence_icon = "🟡" if confidence in ("Thấp", "Rất thấp") else "🟢"
                lines.append(
                    f"   🔮 <b>Dự báo LSTM (Tham khảo):</b> Xu hướng <b>{forecast_data.get('trend_forecast')}</b> "
                    f"| VN-Index ~ {forecast_data.get('predicted_next_day', 0):.0f} "
                    f"| {confidence_icon} Tin cậy: {confidence}"
                )
                lines.append(f"   <i>⚠️ Dự báo thống kê 1 phiên, không phải khuyến nghị đầu tư.</i>")

        if gold_data:
            gold_warning = " ⚠️" if gold_data.get("source") == "fallback" else ""
            lines.append(
                f"• 🥇 <b>Vàng SJC{gold_warning}:</b> Mua {gold_data.get('formatted_buy', 'N/A')} | Bán {gold_data.get('formatted_sell', 'N/A')}"
            )
            if gold_data.get("warning"):
                lines.append(f"   <i>{gold_data['warning']}</i>")

        if forex_data and "USD" in forex_data:
            usd_info = forex_data["USD"]
            lines.append(f"• 💵 <b>Tỷ giá USD/VND:</b> Mua {usd_info.get('buy_transfer', 'N/A')} | Bán {usd_info.get('sell', 'N/A')}")

        lines.append("")

        if news_data:
            lines.append("📰 <b>TIN TỨC NỔI BẬT:</b>")
            for i, news in enumerate(news_data[:3]):
                lines.append(f"• <a href='{news.get('link', '#')}'>{news.get('title', '')}</a>")
            lines.append("")

        # 5. Khối phân tích chuyên sâu từ AI Gemini
        lines.append(f"{'━' * 32}")
        lines.append("🤖 <b>ĐÁNH GIÁ THỊ TRƯỜNG & TÂM LÝ DÒNG TIỀN (AI GEMINI):</b>\n")
        beautified_ai = MessageFormatter.beautify_markdown_to_telegram(ai_commentary.strip())
        lines.append(beautified_ai)
        lines.append(f"\n{'━' * 32}")
        lines.append(
            "⚠️ <i>Lưu ý: Báo cáo do hệ thống tự động tổng hợp nhằm mục đích tham khảo, "
            "không phải lời khuyên tài chính cá nhân.</i>"
        )

        return "\n".join(lines)

    @staticmethod
    def format_quick_portfolio(portfolio_analysis: Dict[str, Any]) -> str:
        """Format nhanh danh mục cho lệnh /report."""
        overall_pnl = portfolio_analysis.get("overall_pnl", 0.0)
        overall_pnl_pct = portfolio_analysis.get("overall_pnl_pct", 0.0)
        overall_status_emoji = "📈" if overall_pnl >= 0 else "📉"
        pnl_color_sign = "+" if overall_pnl >= 0 else ""

        lines = [
            "💼 <b>THÔNG TIN DANH MỤC NHANH:</b>",
            f"• Vốn đầu tư: <b>{portfolio_analysis.get('overall_invested', 0):,.0f} đ</b>",
            f"• Giá trị hiện tại: <b>{portfolio_analysis.get('overall_current_value', 0):,.0f} đ</b>",
            f"• Tổng lãi/lỗ: {overall_status_emoji} <b>{pnl_color_sign}{overall_pnl:,.0f} đ ({pnl_color_sign}{overall_pnl_pct:.2f}%)</b>\n"
        ]

        for fund in portfolio_analysis.get("funds", []):
            lines.append(f"🏢 <b>{fund['fund_code']}</b> | NAV: <b>{fund.get('current_nav', 0):,.2f} đ</b>")
            lines.append(f"   • Nắm giữ: {fund.get('total_units', 0):.2f} CCQ = {fund.get('current_value', 0):,.0f} đ")
            for tx in fund.get("transactions", []):
                t_sign = "+" if tx.get("pnl", 0) >= 0 else ""
                t_emoji = "✅" if tx.get("pnl", 0) >= 0 else "🔻"
                lines.append(f"   {t_emoji} {tx['date']}: {t_sign}{tx.get('pnl', 0):,.0f}đ ({t_sign}{tx.get('pnl_pct', 0):.2f}%)")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_quick_market(
        market_data: Dict[str, Any],
        gold_data: Optional[Dict[str, Any]] = None,
        forex_data: Optional[Dict[str, Any]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Format nhanh thị trường cho lệnh /market."""
        lines = ["🌍 <b>TỔNG QUAN LIÊN THỊ TRƯỜNG HÔM NAY:</b>\n"]
        if market_data and "error" not in market_data:
            idx_price = market_data.get("price", "N/A")
            idx_change = market_data.get("change", 0.0)
            idx_pct = market_data.get("change_pct", 0.0)
            idx_emoji = "🟢" if str(idx_change).startswith("+") or float(idx_change or 0) >= 0 else "🔴"
            pct_str = f"{idx_pct}" if str(idx_pct).endswith("%") else f"{idx_pct}%"
            lines.append(f"• 📈 <b>VN-Index:</b> <b>{idx_price}</b> ({idx_emoji} {idx_change}, {pct_str})")
            if "rsi_14" in market_data and market_data["rsi_14"] != "N/A":
                lines.append(f"   <i>Chỉ báo TA:</i> RSI: {market_data.get('rsi_14')} | MACD: {market_data.get('macd')} (Signal: {market_data.get('macd_signal')})")
            if sentiment_data and "score" in sentiment_data:
                lines.append(f"   🧠 <b>Tâm lý thị trường:</b> {sentiment_data['score']}/100 - {sentiment_data['label']}")
            if "volume" in market_data and market_data["volume"]:
                lines.append(f"   Khối lượng GD: {market_data['volume']}")

        if gold_data:
            lines.append(f"\n• 🥇 <b>Giá vàng SJC:</b>")
            lines.append(f"   Giá mua: <b>{gold_data.get('formatted_buy', 'N/A')}</b>")
            lines.append(f"   Giá bán: <b>{gold_data.get('formatted_sell', 'N/A')}</b>")
            lines.append(f"   Chênh lệch mua/bán: {gold_data.get('formatted_spread', 'N/A')}")

        if forex_data and "USD" in forex_data:
            usd = forex_data["USD"]
            lines.append(f"\n• 💵 <b>Tỷ giá USD/VND:</b>")
            lines.append(f"   Mua chuyển khoản: <b>{usd.get('buy_transfer', 'N/A')}</b> | Bán: <b>{usd.get('sell', 'N/A')}</b>")

        if news_data:
            lines.append(f"\n📰 <b>TIN TỨC TÀI CHÍNH NỔI BẬT:</b>")
            for news in news_data[:3]:
                lines.append(f"   • <a href='{news.get('link', '#')}'>{news.get('title', '')}</a>")

        return "\n".join(lines)

    @staticmethod
    def format_gold_detail(gold_data: Dict[str, Any]) -> str:
        """Định dạng chi tiết giá vàng SJC cho lệnh /gold."""
        if not gold_data:
            return "⚠️ Chưa có dữ liệu giá vàng."
        warning_str = f"\n<i>{gold_data['warning']}</i>\n" if gold_data.get("warning") else ""
        return (
            "🥇 <b>CHI TIẾT GIÁ VÀNG SJC HÔM NAY</b>\n"
            f"<i>Cập nhật: {gold_data.get('date', datetime.now().strftime('%Y-%m-%d'))}</i>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• Tên sản phẩm: <b>{gold_data.get('name', 'Vàng miếng SJC')}</b>\n"
            f"• Giá mua vào: <b>{gold_data.get('formatted_buy', 'N/A')}</b>\n"
            f"• Giá bán ra: <b>{gold_data.get('formatted_sell', 'N/A')}</b>\n"
            f"• Chênh lệch Mua - Bán: <b>{gold_data.get('formatted_spread', 'N/A')}</b>\n"
            f"{warning_str}\n"
            "> 💡 <b>Kinh nghiệm đầu tư vàng:</b> Chênh lệch mua - bán càng rộng thì rủi ro lướt sóng "
            "ngắn hạn càng cao. Vàng miếng phù hợp làm tài sản trú ẩn dài hạn (>1-3 năm)."
        )

    @staticmethod
    def format_forex_detail(forex_data: Dict[str, Any]) -> str:
        """Định dạng chi tiết tỷ giá ngoại tệ cho lệnh /forex."""
        if not forex_data:
            return "⚠️ Chưa có dữ liệu tỷ giá."
        lines = [
            "💵 <b>BẢNG TỶ GIÁ NGOẠI TỆ (VIETCOMBANK)</b>",
            f"<i>Cập nhật: {forex_data.get('date', datetime.now().strftime('%Y-%m-%d'))}</i>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        if "USD" in forex_data:
            u = forex_data["USD"]
            lines.append("🇺🇸 <b>Đô la Mỹ (USD):</b>")
            lines.append(f"  • Mua tiền mặt: <b>{u.get('buy_cash', 'N/A')} đ</b>")
            lines.append(f"  • Mua chuyển khoản: <b>{u.get('buy_transfer', 'N/A')} đ</b>")
            lines.append(f"  • Bán ra: <b>{u.get('sell', 'N/A')} đ</b>\n")
        if "EUR" in forex_data:
            e = forex_data["EUR"]
            lines.append("🇪🇺 <b>Đồng Euro (EUR):</b>")
            lines.append(f"  • Mua chuyển khoản: <b>{e.get('buy_transfer', 'N/A')} đ</b>")
            lines.append(f"  • Bán ra: <b>{e.get('sell', 'N/A')} đ</b>\n")

        lines.append(
            "> 📌 <b>Tác động thị trường:</b> Tỷ giá USD/VND tăng cao thường tạo áp lực rút vốn của khối ngoại, "
            "đồng thời khiến Ngân hàng Nhà nước phải thận trọng hơn trong việc nới lỏng chính sách tiền tệ."
        )
        return "\n".join(lines)

    @staticmethod
    def format_news_detail(news_data: List[Dict[str, str]]) -> str:
        """Định dạng danh sách tin tức tài chính cho lệnh /news."""
        if not news_data:
            return "⚠️ Không có tin tức tài chính mới."
        lines = [
            "📰 <b>TIN TỨC TÀI CHÍNH NỔI BẬT NHẤT</b>",
            "<i>Tổng hợp từ CafeF và VNExpress Kinh Doanh</i>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        ]
        for idx, item in enumerate(news_data, 1):
            title = item.get("title", "")
            link = item.get("link", "#")
            lines.append(f"{idx}. <a href='{link}'><b>{title}</b></a>\n")
        return "\n".join(lines)

