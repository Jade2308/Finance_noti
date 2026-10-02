"""
Message Formatter - Định dạng tin nhắn gửi qua Telegram đẹp mắt bằng HTML.
Bao gồm: Danh mục Quỹ mở, Chỉ số VN-Index, Giá vàng SJC, Tỷ giá USD/VND và Nhận định AI.
Tối ưu hóa hiển thị cho màn hình điện thoại di động (chống tràn dòng, chống lỗi parse HTML).
"""

import html
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from config.settings import get_vietnam_now

DIVIDER = "─────────────────────"


class MessageFormatter:
    """Format các khối dữ liệu tài chính thành định dạng tin nhắn Telegram HTML."""

    @staticmethod
    def beautify_markdown_to_telegram(text: str) -> str:
        """
        Chuyển đổi cú pháp Markdown (bảng, header, bold, rule, quote) sang Telegram HTML thẩm mỹ cao.
        Tự động biến bảng Markdown thô (| col |) thành các Thẻ thông tin (Cards) trực quan cho điện thoại.
        Đảm bảo ký tự đặc biệt (&, <, >) được escape an toàn để không làm hỏng trình phân tích HTML của Telegram.
        """
        if not text:
            return ""

        # 0. Chuẩn hóa xuống dòng
        text = text.replace('\r\n', '\n')

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

                card_lines = [f'{icon} <b>{html.escape(item_raw)}</b>']
                for i in range(1, len(cells)):
                    h_name = headers[i].replace('**', '').replace('*', '').strip()
                    val = cells[i].strip()
                    val_clean = val.replace('**', '').replace('*', '')
                    card_lines.append(f'  • <i>{html.escape(h_name)}:</i> <b>{html.escape(val_clean)}</b>')
                cards.append('\n'.join(card_lines))

            if cards:
                return '\n\n' + '\n\n'.join(cards) + '\n\n'
            return table_raw

        table_pattern = re.compile(r'((?:\|[^\n]+\|\r?\n){2,})', re.MULTILINE)
        text = table_pattern.sub(replace_table, text)

        # 2. Xử lý và bảo vệ blockquotes (> quote)
        quote_blocks: List[str] = []
        def save_quote(match):
            q_lines = [l.strip().lstrip('>').strip() for l in match.group(0).split('\n') if l.strip()]
            idx = len(quote_blocks)
            quote_blocks.append('\n'.join(q_lines))
            return f"\n__BLOCKQUOTE_{idx}__\n"

        text = re.sub(r'((?:^>[^\n]+\r?\n?)+)', save_quote, text, flags=re.MULTILINE)

        # 3. Headers Markdown
        text = re.sub(r'^\s*###\s*(.+)$', r'\n📌 <b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*##\s*(.+)$', r'\n🏛 <b>\1</b>\n', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*#\s*(.+)$', r'\n📋 <b>\1</b>\n', text, flags=re.MULTILINE)

        # 4. Dividers: thay thế tất cả đường kẻ dài bằng DIVIDER (chống rớt dòng mobile)
        text = re.sub(r'^\s*[-*_━]{3,}\s*$', DIVIDER, text, flags=re.MULTILINE)

        # 5. Escape các ký tự & mà chưa phải entity
        text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[a-fA-F0-9]+);)', '&amp;', text)

        # 6. Escape < và > chưa được bảo vệ
        # Match bất kỳ < nào mà không bắt đầu thẻ Telegram hợp lệ
        valid_tag_lookahead = r'(?!(?:/?(?:b|i|u|s|code|pre|blockquote|strong|em|tg-spoiler)|a(?:\s+href=[^>]+)?|/a)>)'
        text = re.sub(r'<' + valid_tag_lookahead, '&lt;', text, flags=re.IGNORECASE)
        # Match bất kỳ > nào không phải đóng thẻ hợp lệ
        text = re.sub(r'(?<![a-zA-Z0-9_"\'-])>', '&gt;', text)

        # 7. In đậm (**text** -> <b>text</b>)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # 8. In nghiêng (*text* hoặc _text_ -> <i>text</i>)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
        text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'<i>\1</i>', text)

        # 9. Inline code (`code` -> <code>code</code>)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

        # 10. Bullets chuẩn hóa (- hoặc * thành •)
        text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)

        # 11. Khôi phục Blockquotes đã lưu
        for idx, q_content in enumerate(quote_blocks):
            q_escaped = html.escape(q_content)
            q_escaped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', q_escaped)
            q_escaped = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', q_escaped)
            text = text.replace(f"__BLOCKQUOTE_{idx}__", f"<blockquote>{q_escaped}</blockquote>")

        # 12. Dọn dẹp dòng trống thừa
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def format_daily_overview(
        portfolio_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        nav_trend: Dict[str, Any],
        gold_data: Optional[Dict[str, Any]] = None,
        forex_data: Optional[Dict[str, Any]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[List[Dict[str, str]]] = None,
        benchmark_summary: Optional[str] = None
    ) -> str:
        """Tạo bản tin tổng quan danh mục & thị trường (Dashboard - Tin nhắn 1)."""
        now_str = get_vietnam_now().strftime("%d/%m/%Y - %H:%M")

        lines = [
            "📋 <b>BÁO CÁO TÀI CHÍNH HÀNG NGÀY</b>",
            f"<i>Cập nhật: {now_str} (Asia/Ho_Chi_Minh)</i>",
            f"{DIVIDER}\n",
        ]

        # 1. Danh mục cá nhân
        invested = portfolio_analysis.get("overall_invested", 0.0)
        current_val = portfolio_analysis.get("overall_current_value", 0.0)
        overall_pnl = portfolio_analysis.get("overall_pnl", 0.0)
        overall_pnl_pct = portfolio_analysis.get("overall_pnl_pct", 0.0)
        status_emoji = "📈" if overall_pnl >= 0 else "📉"
        sign = "+" if overall_pnl >= 0 else ""

        lines.append("💼 <b>DANH MỤC CỦA BẠN:</b>")
        if invested > 0:
            lines.append(f"• Vốn đầu tư: <b>{invested:,.0f} đ</b>")
            lines.append(f"• Giá trị hiện tại: <b>{current_val:,.0f} đ</b>")
            lines.append(f"• Lợi nhuận: {status_emoji} <b>{sign}{overall_pnl:,.0f} đ ({sign}{overall_pnl_pct:.2f}%)</b>\n")
        else:
            lines.append("• Trạng thái: <i>Chưa phát sinh giao dịch (theo dõi NAV tham chiếu)</i>\n")

        # 2. Chi tiết từng quỹ
        for fund in portfolio_analysis.get("funds", []):
            fund_pnl = fund.get("pnl", 0.0)
            fund_pnl_pct = fund.get("pnl_pct", 0.0)
            f_sign = "+" if fund_pnl >= 0 else ""
            f_emoji = "🟢" if fund_pnl >= 0 else "🔴"
            total_units = fund.get("total_units", 0.0)

            lines.append(f"🏢 <b>Quỹ {fund['fund_code']}</b> ({fund.get('fund_name', '')}):")
            lines.append(f"   • NAV mới nhất: <b>{fund.get('current_nav', 0):,.2f} đ</b>")
            if total_units > 0:
                lines.append(f"   • Số lượng sở hữu: <b>{total_units:.2f} CCQ</b>")
                lines.append(f"   • Hiệu suất quỹ: {f_emoji} <b>{f_sign}{fund_pnl:,.0f} đ ({f_sign}{fund_pnl_pct:.2f}%)</b>")

            for tx in fund.get("transactions", []):
                t_pnl = tx.get("pnl", 0.0)
                t_pnl_pct = tx.get("pnl_pct", 0.0)
                t_emoji = "✅" if t_pnl >= 0 else "🔻"
                t_sign = "+" if t_pnl >= 0 else ""
                cagr_str = f" | CAGR: {tx.get('cagr_pct', 0):+.2f}%/năm" if tx.get('holding_years', 0) >= 0.25 else ""
                lines.append(
                    f"      {t_emoji} <i>Lệnh {tx['tx_index']} ({tx['date']})</i>: "
                    f"Mua {tx['buy_price']:,.0f}đ | {t_sign}{t_pnl:,.0f}đ ({t_sign}{t_pnl_pct:.2f}%){cagr_str}"
                )
            lines.append("")

        # 3. Xu hướng NAV
        if nav_trend and nav_trend.get("description"):
            lines.append("📊 <b>BIẾN ĐỘNG NAV:</b>")
            lines.append(f"• {nav_trend['description']}\n")

        if benchmark_summary:
            lines.append(benchmark_summary)
            lines.append("")

        # 4. Toàn cảnh liên thị trường
        lines.append("🌍 <b>TỔNG QUAN LIÊN THỊ TRƯỜNG:</b>")
        if market_data and "error" not in market_data:
            idx_price = market_data.get("price", "N/A")
            idx_change = market_data.get("change", 0.0)
            idx_pct = market_data.get("change_pct", 0.0)
            idx_emoji = "🟢" if str(idx_change).startswith("+") or float(idx_change or 0) >= 0 else "🔴"
            pct_str = f"{idx_pct}" if str(idx_pct).endswith("%") else f"{idx_pct}%"
            lines.append(f"• 📈 <b>VN-Index:</b> <b>{idx_price}</b> ({idx_emoji} {idx_change}, {pct_str})")

            # Chỉ hiển thị chỉ báo TA nếu có số liệu hợp lệ
            rsi = market_data.get("rsi_14")
            macd = market_data.get("macd")
            if rsi not in (None, "None", "N/A", ""):
                lines.append(f"   <i>Chỉ báo TA:</i> RSI: <b>{rsi}</b> | MACD: <b>{macd}</b>")

            if sentiment_data and "score" in sentiment_data:
                lines.append(f"   🧠 <b>Tâm lý thị trường:</b> {sentiment_data['score']}/100 - {sentiment_data['label']}")

            if forecast_data and not forecast_data.get("error"):
                confidence = forecast_data.get("confidence", "N/A")
                confidence_icon = "🟡" if confidence in ("Thấp", "Rất thấp") else "🟢"
                lines.append(
                    f"   🔮 <b>Dự báo LSTM:</b> {forecast_data.get('trend_forecast')} "
                    f"| Mục tiêu: ~{forecast_data.get('predicted_next_day', 0):.0f} ({confidence_icon} {confidence})"
                )

        if gold_data:
            gold_tag = " <i>(Tham khảo)</i>" if gold_data.get("source") == "fallback" else ""
            lines.append(
                f"• 🥇 <b>Vàng SJC{gold_tag}:</b> Mua {gold_data.get('formatted_buy', 'N/A')} | Bán {gold_data.get('formatted_sell', 'N/A')}"
            )

        if forex_data and "USD" in forex_data:
            usd_info = forex_data["USD"]
            lines.append(f"• 💵 <b>Tỷ giá USD/VND:</b> Mua {usd_info.get('buy_transfer', 'N/A')} | Bán {usd_info.get('sell', 'N/A')}")

        lines.append("")

        # 5. Tin tức nổi bật
        if news_data:
            lines.append("📰 <b>TIN TỨC NỔI BẬT:</b>")
            for news in news_data[:3]:
                title = html.escape(news.get("title", "").strip())
                link = html.escape(news.get("link", "#").strip())
                lines.append(f"• <a href='{link}'>{title}</a>")
            lines.append("")

        return "\n".join(lines).strip()

    @staticmethod
    def format_ai_commentary(ai_commentary: str) -> str:
        """Tạo bản tin nhận định chuyên sâu từ AI Gemini (Tin nhắn 2)."""
        beautified_ai = MessageFormatter.beautify_markdown_to_telegram(ai_commentary.strip())
        lines = [
            "🤖 <b>ĐÁNH GIÁ THỊ TRƯỜNG & TÂM LÝ DÒNG TIỀN</b>",
            "<i>Chuyên gia AI Gemini</i>",
            f"{DIVIDER}\n",
            beautified_ai,
            f"\n{DIVIDER}",
            "⚠️ <i>Lưu ý: Báo cáo tổng hợp tự động nhằm mục đích tham khảo, không phải khuyến nghị đầu tư.</i>"
        ]
        return "\n".join(lines).strip()

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
        """Tạo bản tin tổng hợp hàng ngày gộp cả 2 phần (Tương thích ngược)."""
        overview = MessageFormatter.format_daily_overview(
            portfolio_analysis=portfolio_analysis,
            market_data=market_data,
            nav_trend=nav_trend,
            gold_data=gold_data,
            forex_data=forex_data,
            sentiment_data=sentiment_data,
            forecast_data=forecast_data,
            news_data=news_data,
            benchmark_summary=benchmark_summary,
        )
        ai_part = MessageFormatter.format_ai_commentary(ai_commentary)
        return f"{overview}\n\n{ai_part}"

    @staticmethod
    def format_quick_portfolio(portfolio_analysis: Dict[str, Any]) -> str:
        """Format nhanh danh mục cho lệnh /report."""
        overall_pnl = portfolio_analysis.get("overall_pnl", 0.0)
        overall_pnl_pct = portfolio_analysis.get("overall_pnl_pct", 0.0)
        overall_status_emoji = "📈" if overall_pnl >= 0 else "📉"
        pnl_color_sign = "+" if overall_pnl >= 0 else ""
        invested = portfolio_analysis.get("overall_invested", 0.0)
        current_val = portfolio_analysis.get("overall_current_value", 0.0)

        lines = [
            "💼 <b>THÔNG TIN DANH MỤC NHANH:</b>",
            f"{DIVIDER}",
        ]

        if invested > 0:
            lines.append(f"• Vốn đầu tư: <b>{invested:,.0f} đ</b>")
            lines.append(f"• Giá trị hiện tại: <b>{current_val:,.0f} đ</b>")
            lines.append(f"• Tổng lãi/lỗ: {overall_status_emoji} <b>{pnl_color_sign}{overall_pnl:,.0f} đ ({pnl_color_sign}{overall_pnl_pct:.2f}%)</b>\n")
        else:
            lines.append("• Trạng thái: <i>Chưa phát sinh giao dịch (theo dõi NAV tham chiếu)</i>\n")

        for fund in portfolio_analysis.get("funds", []):
            lines.append(f"🏢 <b>{fund['fund_code']}</b> | NAV: <b>{fund.get('current_nav', 0):,.2f} đ</b>")
            total_units = fund.get("total_units", 0.0)
            if total_units > 0:
                lines.append(f"   • Nắm giữ: <b>{total_units:.2f} CCQ</b> = <b>{fund.get('current_value', 0):,.0f} đ</b>")
            for tx in fund.get("transactions", []):
                t_sign = "+" if tx.get("pnl", 0) >= 0 else ""
                t_emoji = "✅" if tx.get("pnl", 0) >= 0 else "🔻"
                lines.append(f"   {t_emoji} {tx['date']}: {t_sign}{tx.get('pnl', 0):,.0f}đ ({t_sign}{tx.get('pnl_pct', 0):.2f}%)")
            lines.append("")

        return "\n".join(lines).strip()

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
        lines = [
            "🌍 <b>TỔNG QUAN LIÊN THỊ TRƯỜNG HÔM NAY:</b>",
            f"{DIVIDER}\n",
        ]
        if market_data and "error" not in market_data:
            idx_price = market_data.get("price", "N/A")
            idx_change = market_data.get("change", 0.0)
            idx_pct = market_data.get("change_pct", 0.0)
            idx_emoji = "🟢" if str(idx_change).startswith("+") or float(idx_change or 0) >= 0 else "🔴"
            pct_str = f"{idx_pct}" if str(idx_pct).endswith("%") else f"{idx_pct}%"
            lines.append(f"• 📈 <b>VN-Index:</b> <b>{idx_price}</b> ({idx_emoji} {idx_change}, {pct_str})")

            rsi = market_data.get("rsi_14")
            macd = market_data.get("macd")
            if rsi not in (None, "None", "N/A", ""):
                lines.append(f"   <i>Chỉ báo TA:</i> RSI: <b>{rsi}</b> | MACD: <b>{macd}</b>")

            if sentiment_data and "score" in sentiment_data:
                lines.append(f"   🧠 <b>Tâm lý thị trường:</b> {sentiment_data['score']}/100 - {sentiment_data['label']}")
            if "volume" in market_data and market_data["volume"]:
                lines.append(f"   Khối lượng GD: {market_data['volume']}")

        if gold_data:
            gold_tag = " <i>(Tham khảo)</i>" if gold_data.get("source") == "fallback" else ""
            lines.append(f"\n• 🥇 <b>Giá vàng SJC{gold_tag}:</b>")
            lines.append(f"   Mua vào: <b>{gold_data.get('formatted_buy', 'N/A')}</b>")
            lines.append(f"   Bán ra: <b>{gold_data.get('formatted_sell', 'N/A')}</b>")
            lines.append(f"   Chênh lệch: {gold_data.get('formatted_spread', 'N/A')}")

        if forex_data and "USD" in forex_data:
            usd = forex_data["USD"]
            lines.append(f"\n• 💵 <b>Tỷ giá USD/VND:</b>")
            lines.append(f"   Mua CK: <b>{usd.get('buy_transfer', 'N/A')}</b> | Bán: <b>{usd.get('sell', 'N/A')}</b>")

        if news_data:
            lines.append(f"\n📰 <b>TIN TỨC TÀI CHÍNH NỔI BẬT:</b>")
            for news in news_data[:3]:
                title = html.escape(news.get("title", "").strip())
                link = html.escape(news.get("link", "#").strip())
                lines.append(f"   • <a href='{link}'>{title}</a>")

        return "\n".join(lines).strip()

    @staticmethod
    def format_gold_detail(gold_data: Dict[str, Any]) -> str:
        """Định dạng chi tiết giá vàng SJC cho lệnh /gold."""
        if not gold_data:
            return "⚠️ Chưa có dữ liệu giá vàng."
        gold_tag = " <i>(Dữ liệu tham khảo)</i>" if gold_data.get("source") == "fallback" else ""
        return (
            f"🥇 <b>CHI TIẾT GIÁ VÀNG SJC HÔM NAY</b>{gold_tag}\n"
            f"<i>Cập nhật: {gold_data.get('date', get_vietnam_now().strftime('%Y-%m-%d'))}</i>\n"
            f"{DIVIDER}\n"
            f"• Tên sản phẩm: <b>{gold_data.get('name', 'Vàng miếng SJC')}</b>\n"
            f"• Giá mua vào: <b>{gold_data.get('formatted_buy', 'N/A')}</b>\n"
            f"• Giá bán ra: <b>{gold_data.get('formatted_sell', 'N/A')}</b>\n"
            f"• Chênh lệch Mua - Bán: <b>{gold_data.get('formatted_spread', 'N/A')}</b>\n\n"
            "> 💡 <b>Kinh nghiệm đầu tư:</b> Chênh lệch mua - bán càng rộng thì rủi ro lướt sóng "
            "ngắn hạn càng cao. Vàng miếng phù hợp làm tài sản trú ẩn dài hạn (>1-3 năm)."
        )

    @staticmethod
    def format_forex_detail(forex_data: Dict[str, Any]) -> str:
        """Định dạng chi tiết tỷ giá ngoại tệ cho lệnh /forex."""
        if not forex_data:
            return "⚠️ Chưa có dữ liệu tỷ giá."
        lines = [
            "💵 <b>BẢNG TỶ GIÁ NGOẠI TỆ (VIETCOMBANK)</b>",
            f"<i>Cập nhật: {forex_data.get('date', get_vietnam_now().strftime('%Y-%m-%d'))}</i>",
            f"{DIVIDER}",
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
            "> 📌 <b>Tác động vĩ mô:</b> Tỷ giá USD/VND tăng cao thường tạo áp lực rút vốn của khối ngoại, "
            "đồng thời khiến Ngân hàng Nhà nước phải thận trọng hơn trong việc nới lỏng chính sách tiền tệ."
        )
        return "\n".join(lines).strip()

    @staticmethod
    def format_news_detail(news_data: List[Dict[str, str]]) -> str:
        """Định dạng danh sách tin tức tài chính cho lệnh /news."""
        if not news_data:
            return "⚠️ Không có tin tức tài chính mới."

        sources: List[str] = []
        for item in news_data:
            src = item.get("source")
            if src and src not in sources:
                sources.append(src)
        sources_str = ", ".join(sources) if sources else "Đa nguồn tài chính uy tín"

        lines = [
            "📰 <b>TIN TỨC TÀI CHÍNH NỔI BẬT NHẤT</b>",
            f"<i>Tổng hợp đa nguồn: {sources_str}</i>",
            f"{DIVIDER}\n",
        ]
        for idx, item in enumerate(news_data, 1):
            title = html.escape(item.get("title", "").strip())
            link = html.escape(item.get("link", "#").strip())
            lines.append(f"{idx}. <a href='{link}'><b>{title}</b></a>\n")
        return "\n".join(lines).strip()
