# 📈 VN Finance Hub

> **Hệ thống Quản trị & Giám sát Tài chính Cá nhân Toàn diện**  
> Tích hợp: **Python 3.11** · **Telegram Bot 2 chiều** · **Google Gemini 3.8 Flash** · **PyTorch LSTM** · **Vnstock & Macro Data**

---

## 🌟 Giới thiệu

**VN Finance Hub** là nền tảng theo dõi và phân tích tài chính cá nhân dành cho nhà đầu tư Việt Nam (đặc biệt phù hợp cho sinh viên, nhà đầu tư mới với số vốn nhỏ). Hệ thống tự động thu thập dữ liệu thị trường đa chiều, tính toán hiệu suất định lượng chuẩn mực, và ứng dụng AI phân tích liên thị trường chuyên sâu.

```
┌─────────────────────────────────────────────────────────────────┐
│                     VN FINANCE HUB                              │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  COLLECTORS  │   ANALYSIS   │  BENCHMARK   │   NOTIFICATIONS    │
│              │              │              │                    │
│ • Quỹ VEOF   │ • CAGR gộp   │ • vs Bank    │ • Telegram Bot     │
│ • VN-Index   │ • PyTorch    │   Vietcombank│   tương tác 2 chiều│
│ • Vàng SJC   │   LSTM Model │ • vs Lạm phát│ • Cảnh báo         │
│ • USD/VND    │ • Fear&Greed │   CPI Fisher │   thông minh       │
│ • Tin đa RSS │ • Gemini 3.8 │ • vs Vàng    │ • Báo cáo tự động  │
│ • Lãi suất NH│   Flash AI   │ • vs VN-Index│   18:00 T2-T6      │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│           SQLite Database · APScheduler · Python-dotenv         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Các Tính Năng Nổi Bật

### 1. Phân Tích Danh Mục & Chuẩn Mực Tài Chính (CAGR & Benchmark)
- **Tính toán lãi/lỗ chi tiết:** Theo dõi từng lệnh mua theo thời gian thực (giá vốn, giá trị thị trường, % lãi/lỗ).
- **Tỷ suất sinh lời kép năm hóa (CAGR):** Tính toán chính xác theo số ngày nắm giữ (`calculate_cagr`), khắc phục ngộ nhận giữa lãi gộp nhiều năm và lãi suất thường niên.
- **Benchmark Engine 4 Kênh:**
  - So sánh với **Lãi suất tiết kiệm Vietcombank 12 tháng** (tính chỉ số Alpha vượt trội).
  - So sánh với **Lạm phát CPI** theo phương trình Fisher (đo lường Real Return - Lợi nhuận thực bảo toàn sức mua).
  - So sánh với **VN-Index** và **Giá vàng SJC**.

### 2. Trí Tuệ Nhân Tạo AI Quant Analyst (Gemini 3.8 Flash)
- **Model:** Sử dụng **`gemini-3.8-flash`** — mô hình thế hệ mới nhất với tốc độ phản hồi nhanh và tư duy suy luận tài chính vượt trội.
- **Prompt Engineering Khách quan:** Phân tích rủi ro 2 chiều (nêu rõ khi nào nên tiếp tục DCA, khi nào nên thận trọng), giải thích căn nguyên vĩ mô (tỷ giá, dòng vốn ngoại, KQKD doanh nghiệp), gắn ngữ cảnh mùa vụ (Quý/Năm) và đối chiếu trực tiếp CAGR vs Lãi suất ngân hàng.
- **Chat Memory 2 Chiều:** Lưu giữ ngữ cảnh 20 tin nhắn gần nhất qua Telegram, hỗ trợ trò chuyện đa lượt (multi-turn conversation) và lệnh `/clear`.

### 3. Học Sâu Chuỗi Thời Gian (PyTorch LSTM Forecaster)
- Mạng nơ-ron **LSTM** dự báo xu hướng phiên kế tiếp của VN-Index dựa trên 30 phiên look-back.
- **Cố định hạt giống ngẫu nhiên (`RANDOM_SEED = 42`):** Kết quả tái lập 100%, không bị sai lệch giữa các lần chạy.
- Huấn luyện 150 epochs, đo lường `training_loss`, tự động phân loại mức độ tin cậy (`confidence`) và đính kèm Disclaimer cảnh báo rủi ro tài chính chuẩn mực.

### 4. Chỉ Số Tâm Lý Thị Trường (Fear & Greed Index)
- Chuẩn hóa toán học khoa học kết hợp:
  - **RSI (14 ngày):** Trọng số 60%, ánh xạ chuẩn tắc từ dải [30, 70] về [0, 1].
  - **MACD Momentum:** Trọng số 40%, áp dụng hàm kích hoạt Sigmoid để làm mượt độ lệch giữa MACD và Signal.
- Thang đo 0–100 với các nhãn định tính: Extreme Fear, Fear, Neutral, Greed, Extreme Greed.

### 5. Thu Thập Dữ Liệu Thời Gian Thực Đa Nguồn & Fallback 2026
- **Quỹ mở VEOF:** Vnstock Fmarket API + VinaCapital AJAX + Database Cache + Snapshot tham chiếu 2026.
- **VN-Index:** Dữ liệu OHLCV, khối lượng giao dịch, tính toán tức thời RSI & MACD.
- **Vàng SJC:** Tỷ giá mua/bán từ Vnstock Retail (Fallback cập nhật mốc 139.5 - 142.5 triệu VNĐ/lượng).
- **Tỷ giá ngoại tệ:** USD/VND, EUR/VND ngân hàng Vietcombank.
- **Lãi suất vĩ mô:** Bảng XML lãi suất tiền gửi chính thức từ Vietcombank.
- **Tin tức tài chính:** Quét đồng thời RSS từ CafeF và VNExpress Kinh doanh.

---

## 🛠️ Cài Đặt & Khởi Chạy

### 1. Chuẩn bị môi trường (Miniconda)
```powershell
# Tạo môi trường với Python 3.11
conda create -n vnfinance python=3.11 -y
conda activate vnfinance

# Di chuyển vào thư mục dự án
cd d:\DATA\vn-finance-hub

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt
```

### 2. Cấu hình file `.env`
Tạo file `.env` tại thư mục gốc (hoặc sao chép từ `.env.example`):
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_from_ai_studio
GEMINI_MODEL=gemini-3.8-flash

# Lịch gửi báo cáo tự động (Asia/Ho_Chi_Minh)
DAILY_REPORT_HOUR=18
DAILY_REPORT_MINUTE=0

# Database
DB_PATH=finance_hub.db
```

### 3. Chạy hệ thống
```powershell
conda activate vnfinance
python main.py
```

---

## 📱 Các Lệnh Telegram Bot

| Lệnh | Chức năng |
|------|-----------|
| `/start` | Menu hướng dẫn và các phím chức năng |
| `/report` | Xem báo cáo nhanh danh mục (vốn, NAV, lãi/lỗ, CAGR từng lệnh) |
| `/market` | Bức tranh thị trường: VN-Index, TA, Fear & Greed, Vàng SJC, Ngoại tệ, Tin tức |
| `/learn <từ_khóa>` | Tra cứu thuật ngữ tài chính (NAV, CCQ, DCA, CAGR, Lãi kép...) |
| `/ask <câu_hỏi>` | Hỏi đáp chuyên gia tài chính AI Gemini 3.8 Flash |
| `/clear` | Xóa bộ nhớ trò chuyện để bắt đầu chủ đề mới |
| *Nhắn tin tự do* | AI tự động tiếp nhận câu hỏi, nhớ ngữ cảnh và giải thích chuyên sâu |

---

## ⚠️ Tuyên Bố Miễn Trừ Trách Nhiệm (Disclaimer)
> Toàn bộ thông tin, số liệu, dự báo AI và mô hình học sâu trong hệ thống này chỉ nhằm mục đích nghiên cứu, học tập và tham khảo quản lý tài chính cá nhân. **Đây KHÔNG phải là lời khuyên đầu tư tài chính chuyên nghiệp.** Mọi quyết định giao dịch tài chính đều là trách nhiệm cá nhân của người dùng.
