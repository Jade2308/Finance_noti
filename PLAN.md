# 📈 VN Finance Hub — Kế Hoạch Dự Án

> **Hệ thống theo dõi tài chính cá nhân toàn diện**
> Python · Telegram Bot · Gemini AI · Vnstock
>
> Ngày tạo: 30/09/2026
> Trạng thái: 🚀 **Hoàn thành Giai đoạn 1 + Giai đoạn 2 + Kiểm toán & Chuẩn hóa Tài chính/AI (Gemini 3.8 Flash + PyTorch LSTM + Benchmark Engine)**

---

## 1. Mục tiêu dự án

Xây dựng ứng dụng Python chạy trên VPS, tự động:

- Thu thập dữ liệu quỹ mở, thị trường chứng khoán, vàng, tỷ giá, kinh tế vĩ mô, tin tức
- Phân tích hiệu suất danh mục, so sánh với các benchmark
- Gửi báo cáo & cảnh báo qua Telegram Bot
- Tích hợp AI Gemini để nhận xét, đề xuất, trả lời câu hỏi tài chính
- Cung cấp công cụ tài chính cá nhân (DCA, so sánh kênh đầu tư, mục tiêu)

### Đối tượng sử dụng

- Sinh viên ngành AI, vốn đầu tư nhỏ (~300K VNĐ)
- Không có kiến thức tài chính → hệ thống cần giải thích đơn giản
- Đang đầu tư quỹ mở VEOF, muốn mở rộng sang nhiều quỹ/cổ phiếu

---

## 2. Danh mục đầu tư hiện tại

| Quỹ | Phiên GD | SL (CCQ) | Giá mua | Đầu tư | Lãi/Lỗ |
|------|----------|----------|---------|--------|--------|
| VEOF | 09/02/2023 | 4.54 | 21,988 đ | 99,825 đ | +46.41% ✅ |
| VEOF | 13/11/2025 | 5.65 | 35,375 đ | 199,870 đ | -9.00% ❌ |
| **Tổng** | | **10.19** | | **299,695 đ** | **~+9.45%** |

---

## 3. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                     VN FINANCE HUB                              │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  COLLECTORS  │   ANALYSIS   │    TOOLS     │   NOTIFICATIONS    │
│              │              │              │                    │
│ • Quỹ mở    │ • Hiệu suất  │ • DCA calc   │ • Telegram Bot     │
│ • Cổ phiếu  │ • Benchmark  │ • So sánh    │   (2 chiều)        │
│ • VN-Index  │ • Vĩ mô      │   kênh ĐT   │ • Cảnh báo         │
│ • Vàng SJC  │ • AI Gemini  │ • Mục tiêu   │   thông minh       │
│ • Tỷ giá    │              │   tài chính  │ • Báo cáo tự động  │
│ • Macro     │              │              │                    │
│ • Tin tức   │              │              │                    │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│                    SQLite · APScheduler · .env                   │
└─────────────────────────────────────────────────────────────────┘
```

### Luồng dữ liệu

```
Vnstock API ──┐
VinaCapital ──┤                                    ┌──→ Báo cáo ngày
CafeF RSS ────┼──→ Collectors ──→ Analyzers ──→ AI ┼──→ Cảnh báo
Giá vàng ─────┤         │                    │     └──→ Trả lời câu hỏi
Tỷ giá ───────┘         ▼                    ▼
                     SQLite DB          Telegram Bot
```

---

## 4. Cấu trúc thư mục

```
vn-finance-hub/
│
├── .env                              # API keys (KHÔNG commit)
├── .env.example                      # Template
├── .gitignore
├── requirements.txt
├── README.md
├── PLAN.md                           # File này
│
├── config/
│   ├── __init__.py
│   └── settings.py                   # Cấu hình, danh mục, hằng số
│
├── collectors/                       # Thu thập dữ liệu
│   ├── __init__.py
│   ├── fund_collector.py             # NAV quỹ mở (VEOF, VESAF...)
│   ├── stock_collector.py            # Cổ phiếu & ETF
│   ├── market_collector.py           # VN-Index, HNX-Index
│   ├── gold_collector.py             # Giá vàng SJC, BTMC, thế giới
│   ├── forex_collector.py            # Tỷ giá USD/VND, EUR, JPY
│   ├── macro_collector.py            # Lãi suất SBV, CPI, lãi suất NH
│   └── news_collector.py             # Tin tức CafeF, VnExpress
│
├── analysis/                         # Phân tích
│   ├── __init__.py
│   ├── fund_analyzer.py              # Hiệu suất quỹ mở, xu hướng NAV
│   ├── stock_analyzer.py             # Phân tích kỹ thuật (RSI, MACD)
│   ├── benchmark.py                  # So sánh vs VN-Index, NH, lạm phát, vàng
│   ├── macro_analyzer.py             # Nhận xét tình hình vĩ mô
│   └── ai_analyst.py                 # Gemini AI tổng hợp & trả lời
│
├── tools/                            # Công cụ tài chính cá nhân
│   ├── __init__.py
│   ├── dca_calculator.py             # Tính toán chiến lược DCA
│   ├── investment_comparator.py      # So sánh kênh: quỹ vs NH vs vàng
│   ├── real_return_calculator.py     # Lợi nhuận thực (trừ lạm phát + phí)
│   └── goal_planner.py              # Lập mục tiêu tài chính
│
├── notifications/                    # Thông báo
│   ├── __init__.py
│   ├── telegram_bot.py               # Bot tương tác 2 chiều
│   ├── message_formatter.py          # Format tin nhắn đẹp
│   └── alert_manager.py              # Cảnh báo thông minh
│
├── education/                        # Giáo dục tài chính
│   ├── __init__.py
│   ├── glossary.py                   # Thuật ngữ tài chính giải thích đơn giản
│   └── daily_tips.py                 # Mẹo tài chính mỗi ngày
│
├── data/
│   ├── __init__.py
│   └── database.py                   # SQLite
│
└── main.py                           # Entry point
```

---

## 5. 6 Tầng dữ liệu

### Tầng 1 — Quỹ mở (Core)

| Dữ liệu | Nguồn | Tần suất |
|----------|-------|----------|
| NAV quỹ VEOF (và các quỹ khác) | Vnstock `Market().fund()` | 1 lần/ngày |
| Lịch sử NAV 90 ngày | Vnstock / VinaCapital AJAX API | 1 lần/ngày |
| Top cổ phiếu quỹ nắm giữ | Vnstock `fund().top_holding()` | 1 lần/tuần |
| Phí quản lý quỹ | Cấu hình thủ công | Khi thêm quỹ |

### Tầng 2 — Cổ phiếu & ETF (Mở rộng)

| Dữ liệu | Nguồn | Tần suất |
|----------|-------|----------|
| Giá cổ phiếu watchlist | Vnstock `Market().equity()` | Trong phiên |
| ETF (E1VFVN30, FUEVFVND) | Vnstock `Market().etf()` | 1 lần/ngày |
| OHLCV lịch sử | Vnstock `.ohlcv()` | 1 lần/ngày |
| Phân tích kỹ thuật (RSI, MACD, BB) | pandas-ta | Khi cần |

### Tầng 3 — Vàng & Tỷ giá

| Dữ liệu | Nguồn | Tần suất |
|----------|-------|----------|
| Giá vàng SJC (mua/bán) | Vnstock `Retail().gold('sjc')` | 2 lần/ngày |
| Giá vàng BTMC | Vnstock `Retail().gold('btmc')` | 2 lần/ngày |
| Tỷ giá USD/VND, EUR, JPY | Vnstock `Retail().exchange_rate()` | 1 lần/ngày |

### Tầng 4 — Kinh tế vĩ mô

| Dữ liệu | Nguồn | Tần suất |
|----------|-------|----------|
| Lãi suất SBV (tái cấp vốn) | Vnstock `Macro()` | 1 lần/tuần |
| CPI / Lạm phát | Vnstock `Macro().economy().cpi()` | 1 lần/tháng |
| Lãi suất tiết kiệm NH | Scrape webgia.com / CafeF | 1 lần/tuần |

### Tầng 5 — Tin tức

| Dữ liệu | Nguồn | Tần suất |
|----------|-------|----------|
| Top tin tài chính | vnstock-news (CafeF, VnExpress) | 1 lần/ngày |
| AI tóm tắt & đánh giá ảnh hưởng | Gemini API | 1 lần/ngày |

### Tầng 6 — Công cụ cá nhân

| Công cụ | Mô tả |
|---------|-------|
| DCA Calculator | Tính kế hoạch mua đều đặn mỗi tháng |
| So sánh kênh đầu tư | Quỹ mở vs Tiết kiệm NH vs Vàng vs Giữ tiền mặt |
| Lợi nhuận thực | Trừ lạm phát & phí quản lý quỹ |
| Mục tiêu tài chính | "Tôi muốn có 10 triệu trong 2 năm" → cần bỏ bao nhiêu/tháng |

---

## 6. Telegram Bot — Các lệnh

| Lệnh | Mô tả | Giai đoạn |
|-------|-------|-----------|
| `/start` | Menu chính với nút bấm | 1 |
| `/report` | Báo cáo danh mục ngay | 1 |
| `/market` | Tổng quan thị trường (VN-Index) | 1 |
| `/gold` | Giá vàng SJC hôm nay | 2 |
| `/forex` | Tỷ giá USD/VND | 2 |
| `/news` | Top 5 tin tức tài chính | 2 |
| `/compare` | So sánh hiệu suất vs benchmark | 2 |
| `/dca` | Tính kế hoạch DCA | 2 |
| `/learn` | Học thuật ngữ tài chính | 3 |
| `/goal` | Lập mục tiêu tài chính | 3 |
| `/ask [câu hỏi]` | Hỏi AI bất kỳ điều gì về tài chính | 2 |
| Tin nhắn tự do | AI tự động trả lời | 2 |

### Thông báo tự động

| Loại | Thời gian | Mô tả |
|------|-----------|-------|
| Báo cáo ngày | 18:00 T2-T6 | Tổng hợp danh mục + thị trường + AI nhận xét |
| Cảnh báo NAV giảm | Tức thì | Khi NAV giảm > 5% trong 7 ngày |
| Cảnh báo VN-Index | Tức thì | Khi VN-Index biến động > 3% trong ngày |
| Nhắc DCA | Ngày 1 mỗi tháng | Nhắc mua thêm đều đặn |
| Mẹo tài chính | 8:00 hàng ngày | 1 tip ngắn giúp học dần |

---

## 7. Hệ thống so sánh benchmark

Mỗi báo cáo sẽ so sánh danh mục với 4 benchmark:

| Benchmark | Ý nghĩa | Ví dụ |
|-----------|---------|-------|
| **VN-Index** | Thị trường chung | Quỹ +10% vs VN-Index +15% → Thua thị trường ❌ |
| **Gửi tiết kiệm NH** | Kênh an toàn nhất | Quỹ +10% vs NH +8% → Tốt hơn NH ✅ |
| **Lạm phát (CPI)** | Sức mua đồng tiền | Quỹ +5% vs CPI +4% → Thực lời 1% 😐 |
| **Vàng SJC** | Kênh truyền thống | Quỹ +10% vs Vàng +20% → Mua vàng tốt hơn ❌ |

---

## 8. Cảnh báo thông minh

| ID | Điều kiện | Mức độ | Hành động |
|----|-----------|--------|-----------|
| `nav_drop_7d` | NAV giảm > 5% trong 7 ngày | 🔴 Cao | Gửi ngay + AI giải thích |
| `nav_surge_30d` | NAV tăng > 10% trong 30 ngày | 🟡 TB | Gợi ý chốt lời |
| `vnindex_crash` | VN-Index giảm > 3% trong ngày | 🔴 Cao | Gửi ngay + ảnh hưởng đến quỹ |
| `gold_spike` | Vàng SJC tăng > 2% trong ngày | 🟡 TB | Tin báo + phân tích |
| `usd_rise` | USD/VND tăng > 1% | 🟡 TB | Cảnh báo vốn ngoại |
| `dca_monthly` | Ngày 1 mỗi tháng | 🟢 Thấp | Nhắc mua DCA |

---

## 9. Công nghệ sử dụng

| Thành phần | Công nghệ | Lý do chọn |
|------------|-----------|-----------|
| Ngôn ngữ | Python 3.13 | Đã cài sẵn, hệ sinh thái tài chính mạnh |
| Dữ liệu CK | vnstock 4.0+ | Thư viện VN phổ biến nhất, hỗ trợ quỹ mở/vàng/tỷ giá |
| Tin tức | vnstock-news | Tích hợp CafeF, VnExpress, hơn 21 nguồn |
| AI | Gemini 3.8 Flash (google-genai) | Bản Flash thông minh mới nhất, tối ưu phân tích tài chính |
| Bot | python-telegram-bot 21+ | Async, hỗ trợ inline keyboard, ổn định |
| Scheduler | APScheduler 3.x | In-process, cron + interval trigger |
| Database | SQLite | Không cần server, đủ dùng cho cá nhân |
| Config | python-dotenv | Bảo mật API key |
| Deploy | VPS + systemd | Chạy 24/7, tự restart |

### Dependencies

```
vnstock>=4.0.0
vnstock-news>=0.1.0
python-telegram-bot>=21.0
google-genai>=1.0.0
apscheduler>=3.10.0
python-dotenv>=1.0.0
pandas>=2.0.0
pandas-ta>=0.3.14b
requests>=2.31.0
beautifulsoup4>=4.12.0
aiohttp>=3.9.0
```

---

## 10. Lộ trình triển khai

### Giai đoạn 1 — MVP (Tuần 1, ~4-5 giờ) — ✅ HOÀN THÀNH 100%

> Mục tiêu: Có sản phẩm chạy được, nhận báo cáo mỗi ngày trên Telegram.

- [x] Setup project, tạo môi trường miniconda `vnfinance`, file .env
- [x] `config/settings.py` — cấu hình danh mục VEOF, .env, Gemini model
- [x] `collectors/fund_collector.py` — lấy NAV quỹ VEOF & Top 10 cổ phiếu
- [x] `collectors/market_collector.py` — lấy VN-Index
- [x] `analysis/fund_analyzer.py` — tính lãi/lỗ, xu hướng NAV 7d/30d
- [x] `analysis/ai_analyst.py` — Gemini phân tích + đề xuất
- [x] `notifications/telegram_bot.py` — bot gửi báo cáo
- [x] `notifications/message_formatter.py` — format tin nhắn đẹp HTML
- [x] `data/database.py` — SQLite lưu lịch sử NAV, chỉ số
- [x] `education/glossary.py` — bảng thuật ngữ tài chính
- [x] `main.py` — scheduler + entry point
- [x] Test end-to-end hoàn chỉnh trên local

### Giai đoạn 2 — Growth & AI Upgrade — ✅ HOÀN THÀNH 100%

> Mục tiêu: Bức tranh thị trường toàn diện, bot tương tác 2 chiều, ML/DL Forecaster, RAG & Benchmark Engine.

- [x] `collectors/gold_collector.py` — giá vàng SJC mua/bán (cập nhật snapshot fallback chuẩn 2026 ~140tr)
- [x] `collectors/forex_collector.py` — tỷ giá USD/VND Vietcombank
- [x] `collectors/news_collector.py` — tin tức đa nguồn (CafeF + VNExpress RSS)
- [x] `collectors/interest_rate_collector.py` — lãi suất tiết kiệm Vietcombank (Benchmark an toàn)
- [x] `analysis/benchmark.py` — **[MỚI]** So sánh 4 kênh đầu tư (Quỹ vs Ngân hàng vs Lạm phát CPI vs Vàng), tính Alpha và Lợi nhuận thực (Fisher equation)
- [x] `analysis/fund_analyzer.py` — **[NÂNG CẤP]** Tự động tính tỷ suất sinh lời năm hóa CAGR (Compound Annual Growth Rate) cho từng lệnh mua
- [x] `analysis/sentiment_analyzer.py` — **[CHUẨN HÓA]** Đo lường Fear & Greed Index (0-100) theo mô hình chuẩn hóa trọng số RSI (60%) + MACD Sigmoid (40%)
- [x] `analysis/forecaster.py` — **[CHUẨN HÓA]** Mô hình Deep Learning PyTorch LSTM cố định seed (42), huấn luyện 150 epochs, tính training loss, phân loại độ tin cậy và disclaimer rủi ro
- [x] Phân tích Kỹ thuật (TA) — tự động tính RSI (14) và MACD/Signal trong `market_collector.py`
- [x] Nâng cấp `ai_analyst.py` — nâng cấp sang model **Gemini 3.8 Flash**, loại bỏ thiên kiến DCA, phân tích rủi ro 2 chiều, bổ sung chu kỳ mùa vụ và so sánh CAGR vs lãi suất NH
- [x] Nâng cấp `notifications/message_formatter.py` — hiển thị CAGR, phân tích Benchmark đa kênh, cảnh báo fallback và disclaimer LSTM
- [x] Nâng cấp `telegram_bot.py` — Chat Memory SQLite, /clear, /market, /gold, /forex, /news, /compare, /dca, /alerts, /tip, /learn, /ask, chat tự do
- [x] `notifications/alert_manager.py` — **[MỚI]** Cảnh báo biến động đột biến trong ngày (realtime alert VN-Index, NAV, USD)
- [x] `tools/dca_calculator.py` — **[MỚI]** Công cụ tính toán kế hoạch tích lũy DCA chi tiết & lãi kép
- [x] `tools/investment_comparator.py` — **[MỚI]** So sánh 4 kênh đầu tư (Quỹ vs NH vs Vàng vs Giữ tiền mặt)

### Giai đoạn 3 — Scale & Tools — ⚡ ĐANG TRIỂN KHAI (50%)

> Mục tiêu: Hệ thống tài chính cá nhân hoàn chỉnh, đa quỹ & dashboard.

- [x] `education/daily_tips.py` — **[MỚI]** Mẹo tài chính cá nhân mỗi ngày lúc 08:00 sáng
- [ ] `collectors/stock_collector.py` — cổ phiếu & ETF
- [ ] `tools/goal_planner.py` — mục tiêu tài chính
- [ ] Hỗ trợ đa quỹ (VESAF, VIBF, VFF...)
- [ ] Dashboard web / mini app Telegram (tùy chọn)

---

## 11. Cấu hình cần chuẩn bị

### API Keys cần có

| Key | Cách lấy | Miễn phí? |
|-----|----------|-----------|
| Telegram Bot Token | @BotFather trên Telegram → `/newbot` | ✅ |
| Telegram Chat ID | `https://api.telegram.org/bot<TOKEN>/getUpdates` | ✅ |
| Gemini API Key | https://aistudio.google.com/apikey | ✅ (có quota) |

### File `.env` mẫu

```env
# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Gemini AI
GEMINI_API_KEY=

# Lịch báo cáo (giờ VN)
DAILY_REPORT_HOUR=18
DAILY_REPORT_MINUTE=0
```

---

## 12. Kiểm thử

### Giai đoạn 1

```bash
# Kiểm tra lấy NAV
python -c "from collectors.fund_collector import FundDataCollector; \
           print(FundDataCollector().get_fund_nav('VEOF'))"

# Kiểm tra VN-Index
python -c "from collectors.market_collector import MarketDataCollector; \
           print(MarketDataCollector().get_vnindex())"

# Kiểm tra Telegram
# → Nhận được tin nhắn test

# Kiểm tra full flow
python main.py
# → Nhận được báo cáo đầy đủ trên Telegram
```

### Giai đoạn 2

```bash
# Giá vàng, tỷ giá, tin tức
# → Dữ liệu trả về đúng format

# Bot tương tác
# → Gõ /gold, /forex, /news, /compare trên Telegram → nhận kết quả

# Cảnh báo
# → Test với dữ liệu giả lập → nhận cảnh báo đúng
```

### Deploy VPS

```bash
# systemd service
sudo systemctl enable finance-hub
sudo systemctl start finance-hub
sudo journalctl -u finance-hub -f
```

---

## 13. Rủi ro & Giải pháp

| Rủi ro | Xác suất | Giải pháp |
|--------|----------|-----------|
| Vnstock API thay đổi/lỗi | Trung bình | Fallback sang VinaCapital AJAX API |
| Gemini API quota hết | Thấp | Cache kết quả, giảm tần suất gọi |
| VPS restart/crash | Thấp | systemd tự restart, log errors |
| Dữ liệu NAV trễ | Thấp | Retry 3 lần, thông báo lỗi qua Telegram |
| Telegram rate limit | Rất thấp | Delay 0.5s giữa các tin nhắn |

---

## 14. Disclaimer

> ⚠️ **QUAN TRỌNG**: Ứng dụng này chỉ mang tính chất hỗ trợ thông tin và
> tham khảo. KHÔNG phải lời khuyên đầu tư chuyên nghiệp. AI có thể đưa ra
> phân tích sai. Mọi quyết định đầu tư đều là trách nhiệm cá nhân.
