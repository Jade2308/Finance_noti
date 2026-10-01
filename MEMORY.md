# 🧠 VN Finance Hub - Project Memory & Log

> **Mục tiêu:** Hệ thống theo dõi tài chính cá nhân, danh mục quỹ mở VEOF, phân tích liên thị trường (Chứng khoán, Vàng, Ngoại tệ, Lãi suất, Tin tức), tích hợp Telegram Bot tương tác 2 chiều và AI Quant Analyst (Google Gemini + PyTorch LSTM + RAG).
> **Khởi tạo:** 30/09/2026
> **Trạng thái hiện tại:** ✅ **Hoàn thành Giai đoạn 1 + Giai đoạn 2 + Kiểm toán & Chuẩn hóa + 🔧 Bugfix & Refactor (30/09/2026)**

### 🔧 Bugfix & Refactor — 30/09/2026
- **[CRITICAL FIX]** `telegram_bot.py`: Thêm `import asyncio` (NameError crash khi gửi broadcast không có polling).
- **[CRITICAL FIX]** `forecaster.py`: LSTM training chuyển sang `async_predict_trend_lstm()` chạy trong `ThreadPoolExecutor` — không còn block asyncio event loop.
- **[CRITICAL FIX]** `main.py`: Implement data cache TTL 10 phút (`_DATA_CACHE_TTL=600s`) — tránh gọi API + train LSTM 3 lần mỗi lần user gõ lệnh Telegram.
- **[TYPE FIX]** `market_collector.py`: RSI/MACD lưu dạng `float | None` thay vì string "N/A" — tránh `ValueError` trong `SentimentAnalyzer`.
- **[TYPE FIX]** `sentiment_analyzer.py`: Xử lý `None` thay vì so sánh chuỗi "N/A".
- **[SECURITY FIX]** `settings.py` + `portfolio.json`: Tách danh mục đầu tư cá nhân ra `portfolio.json` (gitignored) — tránh vô tình commit thông tin giao dịch.
- **[PERSISTENCE FIX]** `database.py` + `telegram_bot.py`: Chat history lưu vào SQLite (bảng `chat_history`) thay vì RAM dict — tồn tại sau khi restart bot/VPS.
- **[DATA FIX]** `main.py`: CPI lấy từ `macro_data["cpi_annual_pct"]` thực tế thay vì hardcode 3.5%.
- **[LOGIC FIX]** `main.py`: Benchmark loop toàn bộ quỹ (không hardcode `funds[0]`).
### 🚀 Tính năng & Công cụ Mới Triển Khai — 30/09/2026
- **[TOOL]** `tools/dca_calculator.py`: Tính toán kế hoạch tích lũy định kỳ (DCA), giá trị tương lai với lãi kép theo tháng, so sánh với gửi ngân hàng và khấu trừ lạm phát sức mua thực tế.
- **[TOOL]** `tools/investment_comparator.py`: So sánh đa chiều 4 kênh đầu tư (Quỹ mở VEOF vs Gửi tiết kiệm Ngân hàng vs Vàng miếng SJC vs Giữ tiền mặt lạm phát) kèm lời khuyên tỷ lệ phân bổ tài sản.
- **[ALERT ENGINE]** `notifications/alert_manager.py`: Bộ máy giám sát ngưỡng biến động thị trường (VN-Index crash/surge >= 2%, NAV drop >= 4% / 7d, tỷ giá USD áp lực cao).
- **[EDUCATION]** `education/daily_tips.py`: Kho bài học & mẹo tài chính thông minh cho sinh viên (Quy tắc 50/30/20, Quỹ khẩn cấp, Bẫy FOMO/FUD, Asset vs Liability) tự động gửi 08:00 sáng mỗi ngày.
- **[TELEGRAM BOT]** Nâng cấp trọn bộ lệnh và giao diện Menu phím bấm trực quan:
  - `/gold`: Tra cứu giá vàng miếng SJC mua/bán chi tiết.
  - `/forex`: Tra cứu bảng tỷ giá ngoại tệ Vietcombank (USD, EUR).
  - `/news`: Tra cứu top 5 tin tức tài chính nóng hổi từ CafeF & VNExpress.
  - `/compare`: So sánh trực quan 4 kênh đầu tư tại Việt Nam.
  - `/dca [số_tiền] [năm]`: Công cụ tính toán kế hoạch tích lũy cá nhân hóa.
  - `/alerts`: Quét và hiển thị cảnh báo rủi ro thị trường tức thời.
  - `/tip`: Nhận 1 mẹo tài chính ngẫu nhiên.
  - Menu inline buttons 5 hàng đầy đủ mọi phím tắt chức năng.

---

## 1. Môi trường Miniconda độc lập
- **Tên môi trường:** `vnfinance`
- **Đường dẫn Python:** `D:\miniconda3\envs\vnfinance\python.exe`
- **Phiên bản Python:** `Python 3.11.16`
- **Lệnh kích hoạt:**
  ```powershell
  conda activate vnfinance
  ```
- **Các thư viện chính đã cài đặt:**
  - `vnstock` (4.0.9) & `vnai` (2.6.2): Thu thập dữ liệu chứng khoán, chỉ số thị trường, NAV quỹ mở từ Fmarket, Giá vàng SJC, Tỷ giá ngoại tệ.
  - `ta` (0.11.0): Thư viện Phân tích Kỹ thuật (Technical Analysis), tự động tính toán RSI (14) và đường MACD / Signal.
  - `torch` (2.14.0+cpu) & `scikit-learn` (1.9.1): Xây dựng và huấn luyện mô hình Học sâu chuỗi thời gian LSTM (PyTorch) siêu tốc trên CPU.
  - `python-telegram-bot` (22.8): Tương tác Bot 2 chiều, xử lý CommandHandler, CallbackQueryHandler, MessageHandler.
  - `google-genai` (2.25.0): Gọi Google Gemini AI (mặc định cấu hình `gemini-3.8-flash`).
  - `apscheduler` (3.11.3): Lập lịch tự động gửi báo cáo mỗi ngày lúc 18:00 (T2-T6).
  - `pandas` (2.3.3) & `numpy` (2.2.6): Xử lý dữ liệu chuỗi thời gian tài chính.
  - `python-dotenv` (1.2.3): Quản lý bảo mật token và API keys.
  - `requests`, `aiohttp`, `beautifulsoup4`: Thu thập dữ liệu HTTP, XML lãi suất Vietcombank và RSS đa nguồn (CafeF, VNExpress).

---

## 2. Cấu trúc mã nguồn hiện tại

```
d:\DATA\vn-finance-hub/
├── .env                              # File cấu hình biến môi trường bí mật (Token Telegram, Gemini Key)
├── .env.example                      # Bản mẫu cấu hình cho người dùng (kèm GEMINI_MODEL=gemini-3.8-flash)
├── .gitignore                        # Bỏ qua file nhạy cảm và database khi git
├── requirements.txt                  # Danh mục dependencies
├── PLAN.md                           # Kế hoạch tổng thể & Tiến độ dự án
├── MEMORY.md                         # File ghi nhớ trạng thái và lịch sử dự án
│
├── config/
│   ├── __init__.py
│   └── settings.py                   # Nạp .env, danh mục VEOF, cấu hình Gemini Model (gemini-3.8-flash)
│
├── collectors/
│   ├── __init__.py
│   ├── fund_collector.py             # Lấy NAV quỹ VEOF & Top 10 cổ phiếu nắm giữ (Fmarket/Vnstock, fallback 2026)
│   ├── market_collector.py           # Lấy chỉ số VN-Index (OHLCV, % thay đổi, volume, TA: RSI 14, MACD)
│   ├── gold_collector.py             # Lấy giá vàng SJC mua/bán từ Vnstock Retail (fallback ~140tr)
│   ├── forex_collector.py            # Lấy tỷ giá ngoại tệ USD/VND, EUR/VND
│   ├── interest_rate_collector.py    # Lấy lãi suất tiết kiệm 12M Vietcombank làm Benchmark
│   └── news_collector.py             # Thu thập tin tức tài chính đa nguồn (CafeF + VNExpress RSS)
│
├── analysis/
│   ├── __init__.py
│   ├── fund_analyzer.py              # Tính lãi/lỗ từng lệnh mua, CAGR năm hóa, xu hướng NAV 7d/30d
│   ├── benchmark.py                  # [MỚI] So sánh 4 kênh đầu tư (Quỹ vs NH vs Lạm phát CPI vs Vàng), tính Alpha
│   ├── sentiment_analyzer.py         # [CHUẨN HÓA] Đo lường chỉ số Sợ hãi & Tham lam (Fear & Greed Index 0-100)
│   ├── forecaster.py                 # [CHUẨN HÓA] Mô hình Deep Learning PyTorch LSTM (Seed 42, 150 epochs, Confidence)
│   └── ai_analyst.py                 # Chuyên gia AI Gemini 3.8 Flash (RAG, Prompt 2 chiều, Chat Memory)
│
├── notifications/
│   ├── __init__.py
│   ├── telegram_bot.py               # Bot Telegram 2 chiều (/report, /market, /learn, /ask, /clear, Chat Memory)
│   └── message_formatter.py          # Format bản tin Telegram HTML thẩm mỹ cao (kèm TA, LSTM, News)
│
├── education/
│   ├── __init__.py
│   └── glossary.py                   # Bảng tra cứu thuật ngữ tài chính (NAV, CCQ, DCA, Lãi kép...)
│
├── data/
│   ├── __init__.py
│   └── database.py                   # SQLite lưu lịch sử NAV, chỉ số, snapshot danh mục
│
└── main.py                           # Điểm khởi chạy chính (Scheduler + Bot polling + Full AI/ML Pipeline)
```

---

## 3. Các tính năng AI & Định lượng đã hoàn thiện

### A. Phân tích Kỹ thuật (TA) & Tâm lý thị trường (Sentiment)
- `market_collector.py` tự động tính toán chỉ báo động lượng **RSI (14 ngày)** và **MACD / MACD Signal**.
- `sentiment_analyzer.py` **[ĐÃ CHUẨN HÓA]** Chuẩn hóa lại công thức Fear & Greed Index phân bổ trọng số: RSI (60%) map [30, 70] về [0, 1] và MACD Momentum Sigmoid (40%). Triệt tiêu hoàn toàn lỗi tràn biên độ, phản ánh chuẩn xác tâm lý (Neutral, Greed, Extreme Fear).

### B. Benchmark Lãi suất Tiết kiệm Vĩ mô
- `interest_rate_collector.py` cào bảng lãi suất XML chính thức từ Vietcombank (kỳ hạn 12 tháng) để làm thước đo phi rủi ro so sánh với quỹ VEOF.

### C. Dự báo Học sâu chuỗi thời gian (PyTorch LSTM)
- `forecaster.py` **[ĐÃ CHUẨN HÓA]** Lấy 30 phiên dữ liệu OHLCV gần nhất của VN-Index, chuẩn hóa bằng `MinMaxScaler`, khởi tạo mạng nơ-ron **LSTM** với seed cố định (`RANDOM_SEED = 42`) đảm bảo kết quả tái lập 100%. Huấn luyện 150 epochs trên CPU, tự động đánh giá `training_loss`, phân loại mức độ tin cậy (`confidence`: Trung bình / Thấp / Rất thấp) và đính kèm Disclaimer rủi ro tài chính rõ ràng.

### D. Hệ thống Tra cứu Tin tức Đa nguồn (Multi-source RSS RAG)
- `news_collector.py` quét đồng thời từ **CafeF** và **VNExpress Kinh doanh** để loại bỏ góc nhìn thiên lệch.
- Đính kèm link đọc trực tiếp trên Telegram và nạp các tin sốt dẻo nhất vào bộ nhớ của Gemini.

### E. Chat Memory 2 chiều & Lệnh Telegram Bot
- `telegram_bot.py` tích hợp bộ nhớ hội thoại tự động lưu 20 tin nhắn gần nhất theo từng `chat_id`.
- Hỗ trợ trò chuyện ngữ cảnh đa lượt (Multi-turn conversational AI).
- Bổ sung lệnh `/clear` để dọn sạch bộ nhớ khi muốn bắt đầu chủ đề mới.

### F. Công cụ Phân tích Benchmark Đa Kênh (`analysis/benchmark.py`)
- **[MỚI]** So sánh hiệu suất danh mục với 4 thước đo:
  1. Gửi tiết kiệm Vietcombank 12 tháng (tính Alpha vượt trội).
  2. Lạm phát tích lũy CPI theo phương trình Fisher (tính Real Return - Lợi nhuận thực sau khi trừ lạm phát).
  3. Giá vàng SJC và chỉ số VN-Index.
- Tự động sinh báo cáo tổng kết benchmark dạng bullet points đưa thẳng vào bản tin Telegram và context của AI.

### G. Chuẩn hóa Lợi nhuận Kép Năm Hóa (CAGR)
- `fund_analyzer.py` tích hợp hàm `calculate_cagr(pnl_pct, buy_date)`: Tính chính xác tỷ suất sinh lời gộp hàng năm (CAGR) theo số ngày nắm giữ thực tế.
- Khắc phục hiểu lầm giữa lãi tổng (+40% qua 3.6 năm tương đương ~9.69%/năm) và lãi suất thường niên, giúp so sánh chuẩn xác với kênh gửi tiết kiệm.

### H. Nâng cấp Google Gemini 3.8 Flash & Prompt Trung lập
- Cấu hình sang model **`gemini-3.8-flash`** (mới nhất từ Google AI Studio).
- Tái cấu trúc Prompt: Bỏ thiên kiến "cứ DCA là tốt", bổ sung đánh giá rủi ro 2 chiều (khi nào nên mua, khi nào nên thận trọng), đưa ngày/giờ, chu kỳ mùa vụ (Quý/Năm) và đối chiếu CAGR vs lãi suất NH trực tiếp vào ngữ cảnh suy luận.

### I. Cập nhật Dữ liệu Tham chiếu Fallback 2026
- `gold_collector.py`: Cập nhật giá vàng SJC fallback lên 139,500,000đ - 142,500,000đ (thay cho giá cũ 82 triệu).
- `fund_collector.py`: Cập nhật NAV VEOF fallback lên 30,745.09đ (thay cho giá cũ 32,191đ).
- Bổ sung cờ cảnh báo `warning` hiển thị trên bản tin nếu buộc phải sử dụng dữ liệu snapshot dự phòng.

---

## 4. Dữ liệu thực tế kiểm thử từ hệ thống (Live Test)

- **NAV Quỹ VEOF:** `30,745.09` đ (Cập nhật ngày gần nhất từ Fmarket).
- **Danh mục người dùng:** Vốn `299,695` đ -> Giá trị hiện tại `313,293` đ (Lãi: `+13,598` đ / `+4.54%`).
  - Lệnh 1 (2023): Mua giá 21,988đ -> Lãi `+39,757` đ (`+39.83%` | **CAGR: ~9.69%/năm** sau 3.6 năm).
  - Lệnh 2 (2025): Mua giá 35,375đ -> Tạm lỗ `-26,158` đ (`-13.09%` | Nắm giữ ngắn hạn, đang điều chỉnh).
- **Benchmark So sánh Lệnh 1 vs Ngân hàng:**
  - Lãi suất NH 12M: `4.60%/năm` -> Lãi gửi NH tương đương: `+17.36%`.
  - Hiệu suất vượt trội (Alpha): **`+22.64%`** (Quỹ vượt trội hơn ngân hàng).
  - Lợi nhuận thực sau lạm phát CPI 3.5%/năm: **`+23.87%`** (Bảo toàn sức mua và tăng trưởng thực dương).
- **VN-Index:** `1,280.50` điểm (Chỉ số Fear & Greed: Neutral 50/100).
- **Dự báo LSTM:** Dự báo xu hướng Tăng (seed 42, 150 epochs, confidence: Thấp, đính kèm disclaimer).
- **Giá vàng SJC:** Mua `139,500,000` đ - Bán `142,500,000` đ.
- **Tỷ giá USD/VND:** Mua chuyển khoản `25,780.00` - Bán `26,160.00`.
- **AI Engine:** Google Gemini 3.8 Flash (`gemini-3.8-flash`).

---

## 5. Hướng dẫn khởi chạy & Vận hành

### Bước 1: Cấu hình file `.env`
Mở file `d:\DATA\vn-finance-hub\.env` và điền:
```env
TELEGRAM_BOT_TOKEN=token_lay_tu_BotFather
TELEGRAM_CHAT_ID=id_chat_cua_ban
GEMINI_API_KEY=api_key_gemini_cua_ban
GEMINI_MODEL=gemini-3.8-flash
```

### Bước 2: Kích hoạt môi trường và khởi chạy
```powershell
conda activate vnfinance
cd d:\DATA\vn-finance-hub
python main.py
```

### Bước 3: Các lệnh trên Telegram
- `/start`: Hiển thị menu chức năng và hướng dẫn.
- `/report`: Xem ngay báo cáo danh mục VEOF và hiệu suất chi tiết.
- `/market`: Xem bức tranh liên thị trường (VN-Index, Chỉ báo TA, Điểm Tâm lý, Dự báo LSTM, Vàng SJC, Tỷ giá, Tin tức CafeF/VNExpress).
- `/learn <thuật ngữ>`: Tra cứu thuật ngữ tài chính (VD: `/learn nav`, `/learn dca`).
- `/ask <câu hỏi>`: Đặt câu hỏi kinh tế, tài chính cá nhân cho AI.
- `/clear`: Xóa lịch sử trò chuyện để bắt đầu ngữ cảnh mới với AI.
- *Nhắn tin tự do*: AI Gemini tự động tiếp nhận câu hỏi, nhớ ngữ cảnh cũ và đưa ra phân tích chuyên sâu.
