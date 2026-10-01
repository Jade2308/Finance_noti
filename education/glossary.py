"""
Bảng giải thích thuật ngữ tài chính - Dành cho người mới bắt đầu.
Ngôn ngữ đơn giản, dễ hiểu, có ví dụ thực tế.
"""

FINANCE_GLOSSARY = {
    "nav": {
        "term": "NAV (Net Asset Value)",
        "vi": "Giá trị tài sản ròng trên một chứng chỉ quỹ",
        "explain": (
            "Giống như 'giá' của 1 chứng chỉ quỹ tại một thời điểm. "
            "NAV = (Tổng giá trị tài sản quỹ đang giữ - Các khoản nợ/chi phí) / Tổng số CCQ đang lưu hành. "
            "Khi các cổ phiếu quỹ nắm giữ tăng giá, NAV sẽ tăng theo -> Bạn có lời."
        ),
        "example": "Nếu NAV của VEOF tăng từ 32,191đ lên 35,000đ thì khoản đầu tư của bạn tăng giá trị tương ứng."
    },
    "ccq": {
        "term": "CCQ (Chứng chỉ quỹ)",
        "vi": "Chứng chỉ quỹ",
        "explain": (
            "Là chứng chỉ xác nhận quyền sở hữu của bạn đối với một phần vốn của quỹ mở. "
            "Nó tương tự như 1 'cổ phiếu' của quỹ, chứng minh bạn đang sở hữu bao nhiêu phần trong quỹ đó."
        ),
        "example": "Bạn mua 10.19 CCQ quỹ VEOF, nghĩa là bạn đang sở hữu 10.19 phần giá trị trong quỹ VEOF."
    },
    "quy_mo": {
        "term": "Quỹ mở (Open-ended Mutual Fund)",
        "vi": "Quỹ đầu tư mở",
        "explain": (
            "Là quỹ do công ty quản lý quỹ chuyên nghiệp điều hành (như VinaCapital, Dragon Capital). "
            "Nhiều nhà đầu tư góp tiền lại -> Chuyên gia tài chính của quỹ dùng số tiền đó phân bổ vào danh mục "
            "hàng chục cổ phiếu lớn, giảm thiểu rủi ro thua lỗ so với việc tự mua 1 mã cổ phiếu."
        ),
        "example": "Thay vì bạn phải có hàng trăm triệu để mua cả FPT, VCB, HPG... thì bạn chỉ cần 100K mua VEOF là gián tiếp sở hữu tất cả."
    },
    "vnindex": {
        "term": "VN-Index",
        "vi": "Chỉ số chứng khoán sàn HOSE (TP.HCM)",
        "explain": (
            "Là chỉ số đo lường biến động vốn hóa của tất cả các cổ phiếu niêm yết trên Sở Giao dịch Chứng khoán TP.HCM. "
            "Nó đóng vai trò như 'nhiệt kế' đo sức khỏe của toàn bộ thị trường chứng khoán Việt Nam."
        ),
        "example": "VN-Index tăng mạnh thường kéo theo giá các cổ phiếu trong quỹ tăng và ngược lại."
    },
    "dca": {
        "term": "DCA (Dollar-Cost Averaging)",
        "vi": "Chiến lược trung bình giá",
        "explain": (
            "Chiến lược đầu tư một số tiền cố định theo định kỳ (ví dụ mỗi tháng trích 200,000đ mua CCQ), "
            "bất kể giá thị trường đang cao hay thấp. Giúp hạn chế cảm xúc tâm lý và tối ưu giá vốn dài hạn."
        ),
        "example": "Tháng này giá cao mua được ít CCQ, tháng sau giá giảm mua được nhiều CCQ hơn -> Trung bình giá luôn hợp lý."
    },
    "benchmark": {
        "term": "Benchmark",
        "vi": "Chỉ số tham chiếu / So sánh",
        "explain": (
            "Tiêu chuẩn dùng để so sánh xem kết quả đầu tư của bạn hay của quỹ có thực sự tốt hay không. "
            "Ví dụ so sánh lợi nhuận quỹ với chỉ số VN-Index hoặc lãi suất gửi tiết kiệm ngân hàng."
        ),
        "example": "Nếu quỹ VEOF lời 10%/năm mà VN-Index chỉ tăng 5% thì quỹ đang hoạt động rất tốt (vượt benchmark)."
    },
    "lai_kep": {
        "term": "Lãi kép (Compound Interest)",
        "vi": "Lãi mẹ đẻ lãi con",
        "explain": (
            "Lợi nhuận sinh ra từ vốn gốc tiếp tục được tái đầu tư để sinh thêm lợi nhuận mới ở các kỳ tiếp theo. "
            "Thời gian đầu tư càng dài, sức mạnh của lãi kép càng tăng theo cấp số nhân."
        ),
        "example": "200K/tháng tích lũy đều đặn sau 10 năm với mức sinh lời 12%/năm sẽ tạo ra tài sản lớn gấp nhiều lần vốn bỏ ra."
    },
    "phi_quan_ly": {
        "term": "Phí quản lý quỹ (Management Fee)",
        "vi": "Phí chi trả cho đội ngũ quản lý quỹ",
        "explain": (
            "Khoản phí hàng năm (thường 1% - 2%) để trả cho các chuyên gia phân tích và vận hành quỹ. "
            "Phí này được tính trừ dần trực tiếp vào NAV hàng ngày, bạn không phải trả thêm tiền mặt."
        ),
        "example": "NAV được công bố đã là con số sau khi trừ phí quản lý."
    },
    "cpi": {
        "term": "CPI / Lạm phát",
        "vi": "Chỉ số giá tiêu dùng / Mức độ mất giá của tiền",
        "explain": (
            "Đo lường mức tăng giá của hàng hóa dịch vụ theo thời gian. Lợi nhuận đầu tư cần phải cao hơn lạm phát "
            "thì tài sản thực của bạn mới thực sự tăng trưởng."
        ),
        "example": "Nếu lạm phát là 4%/năm và quỹ lời 10%/năm thì lợi nhuận thực tế (sức mua tăng thêm) là ~6%/năm."
    }
}


def get_term_explanation(keyword: str) -> str:
    """Tra cứu một thuật ngữ tài chính."""
    key = keyword.strip().lower()
    # Normalize some common search terms
    key_map = {
        "nav": "nav",
        "ccq": "ccq",
        "chứng chỉ quỹ": "ccq",
        "quỹ mở": "quy_mo",
        "quy mo": "quy_mo",
        "vn-index": "vnindex",
        "vnindex": "vnindex",
        "dca": "dca",
        "benchmark": "benchmark",
        "lãi kép": "lai_kep",
        "lai kep": "lai_kep",
        "phí": "phi_quan_ly",
        "phi quan ly": "phi_quan_ly",
        "lạm phát": "cpi",
        "cpi": "cpi",
    }
    
    target_key = key_map.get(key, key)
    data = FINANCE_GLOSSARY.get(target_key)
    if not data:
        return f"❓ Chưa có giải thích cho từ khóa: '{keyword}'. Bạn có thể gõ /ask để hỏi AI trực tiếp nhé!"
    
    return (
        f"📖 <b>{data['term']} ({data['vi']})</b>\n\n"
        f"💡 <b>Giải thích:</b>\n{data['explain']}\n\n"
        f"🔍 <b>Ví dụ:</b>\n{data['example']}"
    )


def list_all_terms() -> str:
    """Danh sách các thuật ngữ hỗ trợ tra cứu."""
    lines = ["📚 <b>DANH SÁCH THUẬT NGỮ TÀI CHÍNH:</b>\n"]
    for k, v in FINANCE_GLOSSARY.items():
        lines.append(f"• <code>{k}</code>: {v['term']} - {v['vi']}")
    lines.append("\n👉 <i>Gõ lệnh <code>/learn &lt;từ_khóa&gt;</code> để xem chi tiết!</i>")
    return "\n".join(lines)
