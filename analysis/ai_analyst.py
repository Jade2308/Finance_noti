"""
AI Analyst - Chuyên gia phân tích thị trường tài chính, kinh tế vĩ mô và tâm lý dòng tiền.
Tích hợp Google Gemini AI với khung phân tích liên thị trường chuyên sâu.
"""

from typing import Dict, Any, Optional, List
import json


class AIAnalyst:
    """Chuyên gia phân tích kinh tế & tài chính cá nhân sử dụng Google Gemini."""

    def __init__(self, api_key: str, model: str = "gemini-3.8-flash"):
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = model
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[AI Error] Không thể khởi tạo Google GenAI Client: {e}")

    def is_available(self) -> bool:
        """Kiểm tra xem AI đã sẵn sàng hoạt động chưa."""
        return self._client is not None

    def _generate_with_retry(self, prompt: str, max_retries: int = 2) -> str:
        """Gọi Gemini API với model chính và tự động fallback sang các bản Flash tương đương nếu quá tải."""
        import time
        # Thứ tự thử: Model cấu hình -> gemini-3.5-flash -> gemini-flash-latest
        models_to_try = [self.model_name]
        for fallback in ["gemini-3.5-flash", "gemini-flash-latest"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error = None
        for m in models_to_try:
            for attempt in range(1, max_retries + 1):
                try:
                    response = self._client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        time.sleep(1.5)
        return f"⚠️ Lỗi phân tích AI: {last_error}" if last_error else "Không nhận được phản hồi từ AI."

    async def generate_deep_market_intelligence(
        self,
        portfolio_analysis: Dict[str, Any],
        nav_trend: Dict[str, Any],
        market_data: Dict[str, Any],
        gold_data: Optional[Dict[str, Any]] = None,
        forex_data: Optional[Dict[str, Any]] = None,
        macro_data: Optional[Dict[str, Any]] = None,
        fund_holdings: Optional[List[Dict[str, Any]]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Báo cáo phân tích chuyên sâu đa tầng:
        - Tình trạng thị trường hiện tại (Chứng khoán, Vàng, Ngoại tệ)
        - Tâm lý thị trường (Market Sentiment: Sợ hãi hay hưng phấn, phòng thủ hay tấn công)
        - Biến động quỹ mở VEOF và tác động từ nhóm cổ phiếu quỹ nắm giữ (Banks, FPT, HPG...)
        - Căn nguyên vĩ mô (Điều gì dẫn đến những biến động đó: Lãi suất, Tỷ giá, Dòng tiền)
        """
        if not self.is_available():
            return (
                "ℹ️ <i>Chưa kích hoạt AI Gemini (cần điền GEMINI_API_KEY trong file .env). "
                "Sau khi cấu hình, AI sẽ tự động phân tích thị trường, tâm lý dòng tiền và giải thích căn nguyên.</i>"
            )

        from datetime import datetime as _dt, date as _date
        _now = _dt.now()
        _quarter = (_now.month - 1) // 3 + 1
        _period_note = "đầu năm (thường khởi sắc)" if _now.month <= 3 else \
                       "giữa năm (ổn định)" if _now.month <= 6 else \
                       "cuối năm Q3 (mùa KQKD Q2/3, cần chú ý)" if _now.month <= 9 else \
                       "cuối năm Q4 (hiệu ứng window dressing, thường tích cực)"

        _lop1_days = (_date.today() - _date(2023, 2, 9)).days
        _lop1_years = _lop1_days / 365.25
        _lop1_pnl = portfolio_analysis.get('funds', [{}])[0].get('pnl_pct', 0) if portfolio_analysis.get('funds') else 0
        _cagr_approx = ((1 + _lop1_pnl/100) ** (1/_lop1_years) - 1) * 100 if _lop1_years > 0.1 else _lop1_pnl
        _bank_rate = macro_data.get('benchmark_12m', 4.6) if macro_data else 4.6

        prompt = f"""
📅 NGÀY PHÂN TÍCH: {_now.strftime('%d/%m/%Y %H:%M')} | Quý {_quarter}/{_now.year} — {_period_note}

Bạn là một Chuyên gia Kinh tế trưởng và Tư vấn Tài chính cá nhân hàng đầu tại Việt Nam.
Người nghe là một bạn sinh viên ngành Trí tuệ nhân tạo (AI), đang đầu tư quỹ mở cổ phiếu VEOF với số vốn nhỏ (~300K VNĐ), chưa có nền tảng tài chính chuyên sâu.

HÃY PHÂN TÍCH BỘ DỮ LIỆU THỜI GIAN THỰC SAU ĐÂY:

1. THỊ TRƯỜNG CHỨNG KHOÁN (VN-INDEX):
{json.dumps(market_data, ensure_ascii=False, indent=2)}
*(Chú ý các chỉ số RSI và MACD để nhận định quá mua/quá bán và xu hướng động lượng dòng tiền)*
- Chỉ số sợ hãi và tham lam (Fear & Greed Index): {sentiment_data.get('score', 'N/A') if sentiment_data else 'N/A'} - {sentiment_data.get('label', 'N/A') if sentiment_data else 'N/A'}
- Dự báo Machine Learning (LSTM): {json.dumps(forecast_data, ensure_ascii=False) if forecast_data else 'N/A'}

2. GIÁ VÀNG SJC (TÀI SẢN TRÚ ẨN):
{json.dumps(gold_data or {}, ensure_ascii=False, indent=2)}

3. TỶ GIÁ & LÃI SUẤT (VĨ MÔ):
- Tỷ giá ngoại tệ USD/VND: {json.dumps(forex_data or {}, ensure_ascii=False, indent=2)}
- Lãi suất tiết kiệm Benchmark 12 tháng (Vietcombank): {macro_data.get('benchmark_12m', 'N/A') if macro_data else 'N/A'}% / năm.

4. QUỸ MỞ VEOF CỦA NGƯỜI DÙNG:
- NAV mới nhất: {nav_trend.get('latest_nav', 'N/A')} đ
- Biến động 7 phiên gần nhất: {nav_trend.get('change_7d_pct', 0)}%
- Biến động ~30 phiên: {nav_trend.get('change_30d_pct', 0)}%
- Danh mục thực tế của người dùng: Tổng vốn {portfolio_analysis.get('overall_invested', 0):,.0f} đ, Giá trị hiện tại {portfolio_analysis.get('overall_current_value', 0):,.0f} đ, Lãi/lỗ {portfolio_analysis.get('overall_pnl', 0):,.0f} đ ({portfolio_analysis.get('overall_pnl_pct', 0):.2f}%)
- Chi tiết các lệnh mua: Lệnh 2023 và Lệnh 2025: {portfolio_analysis.get('funds', [{}])[0].get('transactions', [])}

5. TIN TỨC TÀI CHÍNH NỔI BẬT:
{json.dumps(news_data or [], ensure_ascii=False, indent=2)}

6. TOP 10 CỔ PHIẾU QUỸ VEOF ĐANG NẮM GIỮ (Theo Fmarket):
{json.dumps(fund_holdings or [], ensure_ascii=False, indent=2)}

7. SO SÁNH HIỆU SUẤT THỰC TẾ (CAGR vs Kênh Thay Thế):
- CAGR ước tính danh mục VEOF (từ lệnh 2023): ~{_cagr_approx:.1f}%/năm
- Lãi suất tiết kiệm NH hiện tại: {_bank_rate}%/năm
- Chênh lệch Alpha: ~{_cagr_approx - _bank_rate:+.1f}%/năm
- Tín hiệu: {'🟢 Quỹ đang vượt trội NH' if _cagr_approx > _bank_rate else '🔴 Quỹ đang kém hiệu quả hơn gửi NH — cần đánh giá lại!'}

----------------------------------------------------------------------
YÊU CẦU CẤU TRÚC PHÂN TÍCH (Trình bày mạch lạc, chặt chẽ, dễ hiểu, dùng bullet points):

1. 🌍 BỨC TRANH LIÊN THỊ TRƯỜNG HIỆN NAY:
   - Đánh giá tổng quan sự phân bổ dòng tiền giữa: Chứng khoán (VN-Index) - Vàng (SJC) - Tỷ giá (USD).
   - Thị trường đang ở xu hướng nào?

2. 🧠 TÂM LÝ THỊ TRƯỜNG (MARKET SENTIMENT):
   - Nhà đầu tư hiện tại đang có tâm lý gì? (Ví dụ: Thận trọng phòng thủ, tích cực gom hàng, hay hoang mang bán tháo? Có đang rút tiền sang kênh vàng hoặc gửi tiết kiệm không?).

3. 🏢 QUỸ ĐẦU TƯ VEOF BIẾN ĐỘNG RA SAO VÀ TẠI SAO:
   - Giải thích mối liên hệ giữa biến động NAV của VEOF với các cổ phiếu cốt lõi mà quỹ đang giữ (đặc biệt là nhóm Ngân hàng như VCB, MBB, CTG, TCB, ACB chiếm tỷ trọng lớn, cùng FPT, HPG, MWG).
   - Tại sao lệnh mua 2023 lại lãi rất đậm (>40%) trong khi lệnh mua gần hơn 2025 lại đang điều chỉnh nhẹ?

4. 🔍 ĐIỀU GÌ DẪN ĐẾN NHỮNG THỨ ĐÓ (CĂN NGUYÊN VĨ MÔ):
   - Phân tích nguyên nhân cốt lõi: Áp lực tỷ giá USD/VND thế nào? Lãi suất điều hành và lãi suất ngân hàng đang hút hay đẩy tiền ra thị trường? Tình hình kinh tế phục hồi hay gặp trở ngại gì?

5. 🎯 ĐÁNH GIÁ RỦI RO VÀ LỜI KHUYÊN KHÁCH QUAN (VỐN ~300K):
   - Dựa trên toàn bộ dữ liệu trên, đánh giá KHÁCH QUAN: Đây có phải thời điểm tốt để tiếp tục DCA không? Nêu CẢ HAI phía — lý do NÊN tiếp tục và lý do CÂN NHẮC dừng/chờ.
   - Mức độ rủi ro hiện tại của danh mục (Thấp / Trung bình / Cao) và tại sao?
   - Nếu có rủi ro đáng kể (thị trường downtrend mạnh, lãi suất NH vượt lợi nhuận quỹ, macro xấu), hãy nói thẳng và đề xuất hành động cụ thể.

QUY TẮC ĐỊNH DẠNG DÀNH CHO GIAO DIỆN TELEGRAM MOBILE (BẮT BUỘC):
- TUYỆT ĐỐI KHÔNG DÙNG BẢNG MARKDOWN (| cột 1 | cột 2 |) vì trên điện thoại sẽ bị vỡ dòng và cực kỳ xấu.
- Hãy trình bày dạng THẺ THÔNG TIN (Cards) với icon sinh động (📈, 🥇, 💵, 🏦, 🏢, 🔹), in đậm tiêu đề và dùng gạch đầu dòng (•).
- Dùng dấu trích dẫn > ở đầu dòng cho Lời khuyên quan trọng nhất để tạo khung Blockquote nổi bật.
"""

        return self._generate_with_retry(prompt)

    async def answer_question(self, question: str, full_context: Optional[Dict[str, Any]] = None, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Trả lời câu hỏi tự do của người dùng trên Telegram.
        Tự động tích hợp đầy đủ dữ liệu vĩ mô, giá vàng, tỷ giá, VN-Index và danh mục.
        """
        if not self.is_available():
            return "⚠️ Chưa cấu hình GEMINI_API_KEY trong file .env."

        context_str = ""
        if full_context:
            context_str = f"""
DỮ LIỆU THỰC TẾ HỆ THỐNG ĐANG THEO DÕI:
- Danh mục người dùng: {json.dumps(full_context.get('portfolio', {}), ensure_ascii=False)}
- Chỉ số VN-Index: {json.dumps(full_context.get('market', {}), ensure_ascii=False)}
- Giá vàng SJC: {json.dumps(full_context.get('gold', {}), ensure_ascii=False)}
- Tỷ giá USD/VND: {json.dumps(full_context.get('forex', {}), ensure_ascii=False)}
- Lãi suất ngân hàng tham chiếu: {json.dumps(full_context.get('macro_data', {}), ensure_ascii=False)}
- Dự báo Machine Learning: {json.dumps(full_context.get('forecast_data', {}), ensure_ascii=False)}
- Tin tức nổi bật: {json.dumps(full_context.get('news_data', []), ensure_ascii=False)}
- Cổ phiếu quỹ VEOF nắm giữ: {json.dumps(full_context.get('fund_holdings', []), ensure_ascii=False)}
"""

        history_str = ""
        if chat_history:
            history_str = "LỊCH SỬ TRÒ CHUYỆN GẦN ĐÂY:\n"
            for msg in chat_history[-5:]: # Chỉ lấy 5 tin nhắn gần nhất
                role = "Người dùng" if msg["role"] == "user" else "Chuyên gia (Bạn)"
                history_str += f"{role}: {msg['text']}\n"
            history_str += "\n"

        prompt = f"""
Bạn là chuyên gia kinh tế và cố vấn tài chính cá nhân dành cho sinh viên Việt Nam.
{context_str}
{history_str}
Câu hỏi hiện tại của người dùng:
"{question}"

YÊU CẦU:
- Tham khảo "LỊCH SỬ TRÒ CHUYỆN GẦN ĐÂY" để hiểu ngữ cảnh (nếu người dùng hỏi tiếp ý trước).
- Nếu câu hỏi liên quan đến:
  + "Thị trường ra sao / tâm lý thế nào": Sử dụng dữ liệu VN-Index, thanh khoản và phân tích tâm lý dòng tiền (risk-on / risk-off).
  + "Giá vàng, tỷ giá, chứng khoán": Sử dụng dữ liệu vàng SJC, tỷ giá USD/VND thực tế được cung cấp ở trên và giải thích sự dịch chuyển của dòng tiền.
  + "Điều gì dẫn đến / Tại sao": Luôn giải thích nguyên nhân gốc rễ (Lãi suất, chính sách tiền tệ, tỷ giá, dòng vốn ngoại, kết quả kinh doanh doanh nghiệp).
  + "Nên mua hay bán / Có nên đầu tư thêm": Phân tích dựa trên số vốn nhỏ của sinh viên, chiến lược DCA dài hạn, nhắc nhở quản trị rủi ro.
- Giải thích đơn giản, trực quan, có ví dụ gần gũi. Tránh thuật ngữ quá trừu tượng mà không cắt nghĩa.

QUY TẮC ĐỊNH DẠNG DÀNH CHO GIAO DIỆN TELEGRAM MOBILE (BẮT BUỘC):
- TUYỆT ĐỐI KHÔNG DÙNG BẢNG MARKDOWN (| cột 1 | cột 2 |) vì trên điện thoại sẽ bị vỡ dòng và cực kỳ xấu.
- Hãy trình bày so sánh hoặc số liệu dạng THẺ THÔNG TIN (Cards) với icon sinh động (📈, 🥇, 💵, 🏦, 🏢, 🔹), in đậm tiêu đề và dùng gạch đầu dòng (•).
  Ví dụ khi so sánh 2 mốc thời gian:
  📈 Tên chỉ số/kênh:
  • 2023: số liệu (chú thích)
  • 2026: số liệu (chú thích)
  ➔ Nhận xét nhanh
- Dùng đường kẻ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ để phân tách các phần nếu câu trả lời dài.
- Dùng dấu trích dẫn > ở đầu dòng cho Lời khuyên quan trọng nhất để tạo khung Blockquote nổi bật trên Telegram.
"""

        return self._generate_with_retry(prompt)
