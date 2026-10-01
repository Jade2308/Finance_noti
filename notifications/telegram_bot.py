"""
Telegram Bot - Xử lý thông báo tự động và tương tác 2 chiều với người dùng.
Hỗ trợ đầy đủ các lệnh: /start, /report, /market, /gold, /forex, /news, /compare, /dca, /alerts, /tip, /learn, /ask, /clear.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, MenuButtonCommands
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import html
import re
from education.glossary import get_term_explanation, list_all_terms
from notifications.message_formatter import MessageFormatter

logger = logging.getLogger(__name__)


class FinanceTelegramBot:
    """Telegram Bot thông minh quản lý danh mục tài chính và liên thị trường."""

    def __init__(self, token: str, chat_id: str, app_controller=None):
        self.token = token.strip()
        self.default_chat_id = chat_id.strip()
        self.controller = app_controller
        self.app: Optional[Application] = None
        self._ram_history: Dict[str, List[Dict[str, str]]] = {}

    def is_configured(self) -> bool:
        """Kiểm tra token bot đã được điền chưa."""
        return bool(self.token and self.token != "your_telegram_bot_token_here")

    # ─────────────────── Chat History helpers ───────────────────

    def _get_history(self, chat_id: str) -> List[Dict[str, str]]:
        """Lấy lịch sử hội thoại từ DB (nếu có) hoặc RAM."""
        db = getattr(self.controller, "db", None) if self.controller else None
        if db:
            return db.get_chat_history(chat_id, limit=20)
        return self._ram_history.get(chat_id, [])

    def _append_history(self, chat_id: str, user_text: str, model_text: str):
        """Lưu cặp tin nhắn user+model vào DB hoặc RAM."""
        messages = [
            {"role": "user", "text": user_text},
            {"role": "model", "text": model_text},
        ]
        db = getattr(self.controller, "db", None) if self.controller else None
        if db:
            db.append_chat_messages(chat_id, messages, max_history=20)
        else:
            history = self._ram_history.setdefault(chat_id, [])
            history.extend(messages)
            if len(history) > 20:
                self._ram_history[chat_id] = history[-20:]

    def _clear_history(self, chat_id: str):
        """Xóa lịch sử hội thoại trong DB hoặc RAM."""
        db = getattr(self.controller, "db", None) if self.controller else None
        if db:
            db.clear_chat_history(chat_id)
        self._ram_history.pop(chat_id, None)

    # ─────────────────── Application setup ───────────────────

    def build_application(self) -> Application:
        """Khởi tạo application và đăng ký tất cả các command handlers."""
        app = Application.builder().token(self.token).build()

        # Đăng ký các lệnh
        app.add_handler(CommandHandler("start", self._cmd_start))
        app.add_handler(CommandHandler("help", self._cmd_help))
        app.add_handler(CommandHandler("report", self._cmd_report))
        app.add_handler(CommandHandler("market", self._cmd_market))
        app.add_handler(CommandHandler("gold", self._cmd_gold))
        app.add_handler(CommandHandler("forex", self._cmd_forex))
        app.add_handler(CommandHandler("news", self._cmd_news))
        app.add_handler(CommandHandler("compare", self._cmd_compare))
        app.add_handler(CommandHandler("dca", self._cmd_dca))
        app.add_handler(CommandHandler("alerts", self._cmd_alerts))
        app.add_handler(CommandHandler("tip", self._cmd_tip))
        app.add_handler(CommandHandler("learn", self._cmd_learn))
        app.add_handler(CommandHandler("ask", self._cmd_ask))
        app.add_handler(CommandHandler("clear", self._cmd_clear))

        # Đăng ký xử lý nút bấm Menu
        app.add_handler(CallbackQueryHandler(self._handle_callback))

        # Đăng ký nhận tin nhắn văn bản tự do (Hỏi AI)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message))

        self.app = app
        return app

    async def register_menu_button(self, bot=None):
        """Kích hoạt nút [Menu] màu xanh ở góc trái thanh gõ tin nhắn của Telegram."""
        target_bot = bot or (self.app.bot if self.app else None)
        if not target_bot:
            return
        commands = [
            BotCommand("report", "📊 Báo cáo danh mục & lãi/lỗ VEOF"),
            BotCommand("market", "🌍 Toàn cảnh thị trường & VN-Index"),
            BotCommand("gold", "🥇 Giá vàng SJC hôm nay"),
            BotCommand("forex", "💵 Tỷ giá USD & ngoại tệ"),
            BotCommand("news", "📰 Tin tức tài chính nóng hổi"),
            BotCommand("compare", "⚖️ So sánh Quỹ vs NH vs Vàng"),
            BotCommand("dca", "🧮 Kế hoạch tích lũy DCA"),
            BotCommand("alerts", "🚨 Cảnh báo biến động thị trường"),
            BotCommand("tip", "💡 Mẹo tài chính thông minh"),
            BotCommand("learn", "📚 Tra cứu thuật ngữ tài chính"),
            BotCommand("ask", "🤖 Hỏi đáp chuyên gia AI Gemini"),
            BotCommand("clear", "🧹 Xóa lịch sử trò chuyện AI"),
            BotCommand("help", "ℹ️ Hướng dẫn sử dụng & danh sách lệnh"),
            BotCommand("start", "🏠 Menu phím tắt chính"),
        ]
        try:
            await target_bot.set_my_commands(commands)
            await target_bot.set_chat_menu_button(menu_button=MenuButtonCommands())
            logger.info("[Telegram] Đã kích hoạt nút [Menu] góc trái thành công!")
        except Exception as e:
            logger.warning("[Telegram] Lỗi đăng ký menu button: %s", e)

    # ─────────────────── Command handlers ───────────────────

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /start - Chào mừng và hiển thị menu nút bấm đầy đủ."""
        keyboard = [
            [
                InlineKeyboardButton("📊 Danh mục VEOF", callback_data="btn_report"),
                InlineKeyboardButton("🌍 Thị trường hôm nay", callback_data="btn_market"),
            ],
            [
                InlineKeyboardButton("🥇 Giá vàng SJC", callback_data="btn_gold"),
                InlineKeyboardButton("💵 Tỷ giá ngoại tệ", callback_data="btn_forex"),
            ],
            [
                InlineKeyboardButton("📰 Tin tức nổi bật", callback_data="btn_news"),
                InlineKeyboardButton("⚖️ So sánh kênh ĐT", callback_data="btn_compare"),
            ],
            [
                InlineKeyboardButton("🧮 Kế hoạch DCA", callback_data="btn_dca"),
                InlineKeyboardButton("💡 Mẹo tài chính", callback_data="btn_tip"),
            ],
            [
                InlineKeyboardButton("🚨 Cảnh báo thị trường", callback_data="btn_alerts"),
                InlineKeyboardButton("📚 Tra cứu thuật ngữ", callback_data="btn_learn"),
            ],
            [
                InlineKeyboardButton("🤖 Hỏi chuyên gia AI Gemini", callback_data="btn_ask_help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = (
            "👋 <b>Xin chào bạn!</b>\n\n"
            "Tôi là <b>VN Finance Hub Bot</b> — trợ lý theo dõi danh mục đầu tư quỹ mở "
            "và toàn cảnh thị trường tài chính Việt Nam dành riêng cho bạn.\n\n"
            "✨ <b>Các công cụ nổi bật:</b>\n"
            "• Tự động gửi báo cáo danh mục & thị trường lúc 18:00 (T2-T6).\n"
            "• Gửi mẹo tài chính thông minh mỗi sáng lúc 08:00.\n"
            "• Tra cứu giá vàng SJC, tỷ giá USD/VND, lãi suất ngân hàng.\n"
            "• Công cụ tính toán kế hoạch DCA & so sánh các kênh tài sản.\n"
            "• Hỏi đáp kiến thức kinh tế với AI Gemini 3.8 Flash.\n\n"
            "<i>Hãy bấm nút bên dưới hoặc gõ tin nhắn để bắt đầu:</i>"
        )
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /help - Hướng dẫn sử dụng."""
        help_text = (
            "📖 <b>HƯỚNG DẪN CÁC LỆNH BOT:</b>\n\n"
            "• <code>/report</code>: Xem tình trạng lời/lỗ danh mục ngay lập tức.\n"
            "• <code>/market</code>: Xem chỉ số VN-Index, chỉ báo TA, tâm lý dòng tiền.\n"
            "• <code>/gold</code>: Xem giá mua/bán vàng miếng SJC mới nhất.\n"
            "• <code>/forex</code>: Xem tỷ giá USD/VND và ngoại tệ Vietcombank.\n"
            "• <code>/news</code>: Xem tin tức tài chính kinh tế đa nguồn (CafeF, VnEconomy, VNExpress,...).\n"
            "• <code>/compare</code>: So sánh hiệu quả Quỹ mở vs Gửi NH vs Vàng SJC.\n"
            "• <code>/dca [số_tiền] [năm]</code>: Tính kế hoạch tích lũy (VD: <code>/dca 500000 3</code>).\n"
            "• <code>/alerts</code>: Xem các cảnh báo rủi ro biến động thị trường.\n"
            "• <code>/tip</code>: Nhận 1 mẹo tài chính cá nhân thông minh.\n"
            "• <code>/learn &lt;từ_khóa&gt;</code>: Tra cứu thuật ngữ tài chính (VD: <code>/learn nav</code>).\n"
            "• <code>/ask &lt;câu hỏi&gt;</code>: Đặt câu hỏi kinh tế, đầu tư cho AI.\n"
            "• <code>/clear</code>: Xóa lịch sử trò chuyện để bắt đầu chủ đề mới với AI.\n"
            "• <i>Nhắn tin tự do</i>: Nhắn bất kỳ câu hỏi nào, AI sẽ phân tích và trả lời ngay!"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    async def _cmd_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /report - Gửi báo cáo danh mục nhanh."""
        await update.message.reply_text("🔄 <i>Đang kiểm tra NAV và tính toán danh mục...</i>", parse_mode=ParseMode.HTML)
        if self.controller:
            msg = await self.controller.get_quick_report_text()
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /market - Xem nhanh thị trường."""
        if self.controller:
            msg = await self.controller.get_quick_market_text()
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_gold(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /gold - Giá vàng SJC."""
        if self.controller:
            msg = await self.controller.get_gold_text()
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_forex(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /forex - Tỷ giá ngoại tệ."""
        if self.controller:
            msg = await self.controller.get_forex_text()
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /news - Top tin tức tài chính."""
        if self.controller:
            msg = await self.controller.get_news_text()
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_compare(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /compare - So sánh các kênh đầu tư."""
        if self.controller:
            msg = await self.controller.get_comparison_text(capital=1_000_000, years=3)
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_dca(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /dca [số_tiền] [năm] - Tính toán tích lũy."""
        monthly_amount = 300_000.0
        years = 3

        if context.args:
            try:
                monthly_amount = float(context.args[0].replace(",", "").replace(".", ""))
                if len(context.args) >= 2:
                    years = max(1, int(context.args[1]))
            except Exception:
                pass

        if self.controller:
            msg = await self.controller.get_dca_text(monthly_amount=monthly_amount, years=years)
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /alerts - Kiểm tra cảnh báo thị trường tức thời."""
        if self.controller:
            msg = await self.controller.get_alerts_text()
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_tip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /tip - Nhận một mẹo tài chính ngẫu nhiên."""
        if self.controller:
            msg = self.controller.get_daily_tip_text()
            await self._send_safe_html(update.effective_chat.id, msg)
        else:
            await update.message.reply_text("Chưa kết nối bộ điều khiển dữ liệu.")

    async def _cmd_learn(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /learn - Tra cứu thuật ngữ tài chính."""
        args = context.args
        if not args:
            await update.message.reply_text(list_all_terms(), parse_mode=ParseMode.HTML)
        else:
            keyword = " ".join(args)
            explanation = get_term_explanation(keyword)
            await update.message.reply_text(explanation, parse_mode=ParseMode.HTML)

    async def _cmd_ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /ask - Hỏi AI chuyên gia."""
        args = context.args
        if not args:
            await update.message.reply_text(
                "❓ Bạn vui lòng nhập câu hỏi sau lệnh /ask.\n<i>Ví dụ: <code>/ask Tôi có 200K một tháng thì nên đầu tư thế nào?</code></i>",
                parse_mode=ParseMode.HTML,
            )
            return

        question = " ".join(args)
        await self._process_ai_question(update, question)

    async def _cmd_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /clear - Xóa lịch sử trò chuyện AI."""
        chat_id = str(update.effective_chat.id)
        self._clear_history(chat_id)
        await update.message.reply_text(
            "🧹 <i>Đã xóa lịch sử trò chuyện với AI. Bạn có thể bắt đầu chủ đề mới!</i>",
            parse_mode=ParseMode.HTML,
        )

    # ─────────────────── Callback handler ───────────────────

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý sự kiện khi người dùng click vào nút inline keyboard."""
        query = update.callback_query
        await query.answer()

        data = query.data
        chat_id = query.message.chat_id

        if not self.controller:
            await self._send_safe_html(chat_id, "Chưa kết nối bộ điều khiển dữ liệu.")
            return

        if data == "btn_report":
            msg = await self.controller.get_quick_report_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_market":
            msg = await self.controller.get_quick_market_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_gold":
            msg = await self.controller.get_gold_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_forex":
            msg = await self.controller.get_forex_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_news":
            msg = await self.controller.get_news_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_compare":
            msg = await self.controller.get_comparison_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_dca":
            msg = await self.controller.get_dca_text(monthly_amount=300_000, years=3)
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_tip":
            msg = self.controller.get_daily_tip_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_alerts":
            msg = await self.controller.get_alerts_text()
            await self._send_safe_html(chat_id, msg)
        elif data == "btn_learn":
            await self._send_safe_html(chat_id, list_all_terms())
        elif data == "btn_ask_help":
            prompt_hint = (
                "🤖 <b>HỎI ĐÁP VỚI CHUYÊN GIA AI:</b>\n\n"
                "Bạn chỉ cần gõ tin nhắn trực tiếp vào khung chat này (VD: <i>'Lãi suất ngân hàng giảm thì quỹ VEOF có tăng không?'</i>).\n"
                "Tôi sẽ nhờ chuyên gia AI Gemini phân tích và giải thích cho bạn ngay!"
            )
            await self._send_safe_html(chat_id, prompt_hint)

    # ─────────────────── Text message handler ───────────────────

    async def _handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý tin nhắn văn bản tự do của người dùng."""
        text = update.message.text.strip()
        if text.startswith("/"):
            return
        await self._process_ai_question(update, text)

    async def _process_ai_question(self, update: Update, question: str):
        """Gửi câu hỏi tới AI Gemini và trả kết quả, có lưu lịch sử."""
        chat_id = str(update.effective_chat.id)

        thinking_msg = await update.message.reply_text(
            "🤔 <i>Chuyên gia AI đang phân tích câu hỏi của bạn...</i>", parse_mode=ParseMode.HTML
        )

        reply = "Chưa kết nối AI Analyst."
        if self.controller and self.controller.ai_analyst:
            portfolio_ctx = await self.controller.get_portfolio_context_for_ai()
            history = self._get_history(chat_id)
            reply = await self.controller.ai_analyst.answer_question(
                question,
                portfolio_ctx,
                chat_history=history,
            )

        # Lưu lịch sử
        self._append_history(chat_id, question, reply)

        # Xóa tin nhắn chờ
        try:
            await thinking_msg.delete()
        except Exception:
            pass

        clean_reply = MessageFormatter.beautify_markdown_to_telegram(reply)
        await self._send_safe_html(chat_id, f"🤖 <b>Trả lời từ AI Gemini:</b>\n\n{clean_reply}")

    # ─────────────────── Broadcast & Helpers ───────────────────

    @staticmethod
    def strip_html(text: str) -> str:
        """Loại bỏ thẻ HTML và unescape entities khi cần fallback gửi văn bản thuần (plain text)."""
        if not text:
            return ""
        clean = re.sub(r'</?(?:b|strong)>', '', text)
        clean = re.sub(r'</?(?:i|em)>', '', clean)
        clean = re.sub(r'</?blockquote>', '\n> ', clean)
        clean = re.sub(r'<a\s+href=[\'"]([^\'"]+)[\'"]>([^<]+)</a>', r'\2 (\1)', clean)
        clean = re.sub(r'<[^>]+>', '', clean)
        return html.unescape(clean).strip()

    @staticmethod
    def split_telegram_html(text: str, max_chars: int = 3800) -> List[str]:
        """
        Chia nhỏ văn bản HTML dài thành các đoạn an toàn <= max_chars cho Telegram.
        Tự động cân bằng và đóng thẻ ở cuối đoạn, mở lại ở đầu đoạn kế tiếp để chống lỗi 400 Bad Request.
        """
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]

        tag_re = re.compile(r'<(/?)([a-zA-Z0-9_-]+)(?:\s+[^>]*?)?>')
        valid_tags = {'b', 'i', 'u', 's', 'code', 'pre', 'blockquote', 'a', 'strong', 'em', 'tg-spoiler'}

        def get_open_tags(html_str: str):
            stack = []
            for match in tag_re.finditer(html_str):
                is_closing = match.group(1) == '/'
                tag_name = match.group(2).lower()
                if tag_name in valid_tags:
                    if not is_closing:
                        stack.append((tag_name, match.group(0)))
                    else:
                        for i in range(len(stack) - 1, -1, -1):
                            if stack[i][0] == tag_name:
                                stack.pop(i)
                                break
            return stack

        paragraphs = text.split('\n\n')
        chunks: List[str] = []
        current_chunk = ''

        for p in paragraphs:
            cand = (current_chunk + '\n\n' + p).strip() if current_chunk else p
            if len(cand) <= max_chars:
                current_chunk = cand
            else:
                if current_chunk:
                    open_tags = get_open_tags(current_chunk)
                    closing = ''.join(f'</{t[0]}>' for t in reversed(open_tags))
                    chunks.append(current_chunk + closing)
                    reopen = ''.join(t[1] for t in open_tags)
                    current_chunk = reopen

                cand_p = (current_chunk + '\n\n' + p).strip() if current_chunk else p
                if len(cand_p) <= max_chars:
                    current_chunk = cand_p
                else:
                    lines = p.split('\n')
                    for line in lines:
                        cand_l = (current_chunk + '\n' + line).strip() if current_chunk else line
                        if len(cand_l) <= max_chars:
                            current_chunk = cand_l
                        else:
                            if current_chunk:
                                open_tags = get_open_tags(current_chunk)
                                closing = ''.join(f'</{t[0]}>' for t in reversed(open_tags))
                                chunks.append(current_chunk + closing)
                                reopen = ''.join(t[1] for t in open_tags)
                                current_chunk = reopen

                            cand_l2 = (current_chunk + '\n' + line).strip() if current_chunk else line
                            if len(cand_l2) <= max_chars:
                                current_chunk = cand_l2
                            else:
                                words = line.split(' ')
                                for w in words:
                                    cand_w = (current_chunk + ' ' + w).strip() if current_chunk else w
                                    if len(cand_w) <= max_chars:
                                        current_chunk = cand_w
                                    else:
                                        if current_chunk:
                                            open_tags = get_open_tags(current_chunk)
                                            closing = ''.join(f'</{t[0]}>' for t in reversed(open_tags))
                                            chunks.append(current_chunk + closing)
                                            reopen = ''.join(t[1] for t in open_tags)
                                            current_chunk = (reopen + ' ' + w).strip()
                                        else:
                                            chunks.append(w[:max_chars])
                                            current_chunk = w[max_chars:]

        if current_chunk.strip():
            open_tags = get_open_tags(current_chunk)
            closing = ''.join(f'</{t[0]}>' for t in reversed(open_tags))
            chunks.append(current_chunk + closing)

        return chunks

    async def send_broadcast_message(self, text: str, chat_id: Optional[str] = None):
        """Gửi tin nhắn chủ động (báo cáo hàng ngày hoặc cảnh báo khẩn) an toàn."""
        target_chat = chat_id or self.default_chat_id
        if not target_chat:
            logger.warning("[Telegram] Không có CHAT_ID để gửi broadcast.")
            return
        await self._send_safe_html(target_chat, text)

    async def _send_safe_html(self, chat_id, text: str):
        """Gửi tin nhắn với phân đoạn HTML thông minh, chống đứt gãy thẻ và fallback văn bản sạch."""
        chunks = self.split_telegram_html(text, max_chars=3800)

        # Lấy bot instance
        bot_instance = self.app.bot if self.app else None
        if not bot_instance:
            from telegram import Bot
            bot_instance = Bot(token=self.token)

        for chunk in chunks:
            try:
                await bot_instance.send_message(chat_id=chat_id, text=chunk, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.warning("[Telegram HTML parse error]: %s. Chuyển sang fallback plain text sạch.", e)
                try:
                    # Tuyệt đối không gửi raw HTML thô — loại bỏ thẻ HTML trước khi gửi fallback!
                    clean_text = self.strip_html(chunk)
                    await bot_instance.send_message(chat_id=chat_id, text=clean_text)
                except Exception as e2:
                    logger.error("[Telegram] Lỗi nghiêm trọng khi gửi fallback: %s", e2)
            await asyncio.sleep(0.35)

