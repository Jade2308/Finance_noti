"""
Daily Tips - Mẹo tài chính cá nhân và tư duy đầu tư thông minh dành cho sinh viên & người mới.
"""

import random
from typing import Dict, Any, List

FINANCIAL_TIPS: List[Dict[str, str]] = [
    {
        "id": "tip_1",
        "title": "Quy tắc 50/30/20 trong chi tiêu",
        "category": "Quản lý ngân sách",
        "content": (
            "Chia thu nhập mỗi tháng làm 3 phần: "
            "50% cho nhu cầu thiết yếu (ăn ở, đi lại), 30% cho sở thích cá nhân, "
            "và ít nhất 20% cho tiết kiệm & đầu tư. Với sinh viên, chỉ cần bắt đầu từ 10% cũng rất tốt!"
        ),
        "takeaway": "Tiết kiệm trước khi chi tiêu, đừng chờ tiêu xong mới tiết kiệm số tiền còn thừa."
    },
    {
        "id": "tip_2",
        "title": "Sức mạnh thần kỳ của Lãi kép",
        "category": "Đầu tư dài hạn",
        "content": (
            "Nếu bạn tích lũy 300,000 đ/tháng từ năm 20 tuổi với lợi nhuận 12%/năm, "
            "sau 20 năm bạn sẽ có gần 300 triệu đồng, dù số vốn bạn thực bỏ ra chỉ là 72 triệu! "
            "Thời gian chính là đồng minh lớn nhất của tuổi trẻ."
        ),
        "takeaway": "Đầu tư sớm với số vốn nhỏ tốt hơn nhiều so với chờ có nhiều tiền mới bắt đầu."
    },
    {
        "id": "tip_3",
        "title": "Quỹ khẩn cấp: Tấm đệm an toàn trước giông bão",
        "category": "Quản trị rủi ro",
        "content": (
            "Trước khi đầu tư mạo hiểm, hãy luôn để dành một khoản tiền tương đương 3-6 tháng chi phí sinh hoạt "
            "trong tài khoản ngân hàng hoặc ví gửi linh hoạt. Khoản tiền này giúp bạn không phải bán tháo cổ phiếu/quỹ khi có sự cố bất ngờ."
        ),
        "takeaway": "Đừng bao giờ đầu tư bằng số tiền bạn cần dùng trong 6 tháng tới."
    },
    {
        "id": "tip_4",
        "title": "Chiến lược DCA: Khắc tinh của cảm xúc",
        "category": "Chiến lược đầu tư",
        "content": (
            "Thay vì đoán đáy đoán đỉnh, hãy mua đều đặn vào một ngày cố định trong tháng. "
            "Khi thị trường giảm, bạn mua được nhiều chứng chỉ quỹ hơn với giá rẻ. "
            "Khi thị trường tăng, danh mục của bạn sinh lời lớn."
        ),
        "takeaway": "Thời gian ở trong thị trường (Time in market) luôn thắng việc căn thời điểm (Timing the market)."
    },
    {
        "id": "tip_5",
        "title": "Lạm phát: Kẻ trộm âm thầm bào mòn túi tiền",
        "category": "Kinh tế vĩ mô",
        "content": (
            "Với mức lạm phát trung bình 3.5%/năm tại Việt Nam, sau 10 năm sức mua của 100 triệu đồng "
            "chỉ còn tương đương khoảng 70 triệu. Để tiền trong ngăn kéo đồng nghĩa với việc bạn đang tự làm mình nghèo đi mỗi ngày."
        ),
        "takeaway": "Đầu tư vào các tài sản sinh lời (Quỹ mở, Cổ phiếu, Vàng) là cách duy nhất bảo vệ sức mua."
    },
    {
        "id": "tip_6",
        "title": "Tài sản vs Tiêu sản (Rich Dad Poor Dad)",
        "category": "Tư duy tài chính",
        "content": (
            "Tài sản là thứ bỏ tiền vào túi bạn (Chứng chỉ quỹ, Cổ phiếu chia cổ tức, Kênh đầu tư sinh lời). "
            "Tiêu sản là thứ rút tiền khỏi túi bạn (Điện thoại xịn trả góp, xe cộ tốn xăng và mất giá). "
            "Người giàu tập trung mua tài sản trước, tiêu sản sau."
        ),
        "takeaway": "Hãy dùng tiền đẻ ra tiền để chi trả cho các sở thích cá nhân."
    },
    {
        "id": "tip_7",
        "title": "Bẫy tâm lý FOMO và FUD",
        "category": "Tâm lý thị trường",
        "content": (
            "FOMO (Sợ bỏ lỡ cơ hội) khiến bạn đu đỉnh khi thị trường đang hưng phấn. "
            "FUD (Sợ hãi và nghi ngờ) khiến bạn bán tháo đúng đáy khi thị trường rung lắc ngắn hạn. "
            "Nhà đầu tư quỹ mở thành công là người giữ được cái đầu lạnh."
        ),
        "takeaway": "Tham lam khi người khác sợ hãi, thận trọng khi người khác quá tham lam."
    },
    {
        "id": "tip_8",
        "title": "Đầu tư vào bản thân là khoản đầu tư tốt nhất",
        "category": "Phát triển bản thân",
        "content": (
            "Với số vốn dưới 500K/tháng, tỷ suất sinh lời 15%/năm cũng chỉ mang lại vài chục nghìn tiền lãi. "
            "Tài sản lớn nhất của bạn ở độ tuổi sinh viên là khả năng học hỏi để nâng cao thu nhập trong tương lai."
        ),
        "takeaway": "Học thêm kỹ năng AI, ngoại ngữ, chuyên môn để gia tăng dòng tiền thu nhập chủ động."
    }
]


def get_random_tip() -> Dict[str, str]:
    """Lấy ngẫu nhiên một mẹo tài chính."""
    return random.choice(FINANCIAL_TIPS)


def format_tip_html(tip: Dict[str, str]) -> str:
    """Format mẹo tài chính thành Telegram HTML."""
    return (
        f"💡 <b>MẸO TÀI CHÍNH HÔM NAY: {tip['title'].upper()}</b>\n"
        f"🏷 <i>Chủ đề: {tip['category']}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{tip['content']}\n\n"
        f"> 📌 <b>Bài học cốt lõi:</b>\n"
        f"> {tip['takeaway']}"
    )
