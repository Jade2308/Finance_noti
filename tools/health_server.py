"""
Health Server - Cung cấp HTTP Web Server nhẹ phục vụ Healthcheck cho Render.com/Cloud.
Mở cổng theo biến môi trường PORT (mặc định 10000 trên Render).
Hỗ trợ UptimeRobot ping định kỳ để giữ ứng dụng luôn thức 24/7.
"""

import http.server
import logging
import os
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health", "/healthz", "/ping"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VN Finance Hub - Status</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .card {{
            background: #1e293b;
            padding: 2.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            max-width: 480px;
            width: 90%;
            border: 1px solid #334155;
            text-align: center;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            background: #064e3b;
            color: #34d399;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.875rem;
            margin-bottom: 1.25rem;
        }}
        .dot {{
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            margin-right: 6px;
            box-shadow: 0 0 10px #10b981;
        }}
        h1 {{
            font-size: 1.5rem;
            margin: 0 0 0.75rem 0;
            color: #ffffff;
        }}
        p {{
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.5;
            margin: 0 0 1.5rem 0;
        }}
        .info-box {{
            background: #0f172a;
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: left;
            font-size: 0.85rem;
            border: 1px solid #1e293b;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }}
        .info-row:last-child {{
            margin-bottom: 0;
        }}
        .label {{
            color: #64748b;
        }}
        .value {{
            color: #e2e8f0;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">
            <span class="dot"></span>
            Hệ Thống Đang Hoạt Động (24/7)
        </div>
        <h1>VN Finance Hub</h1>
        <p>Hệ thống Quản trị & Giám sát Tài chính Cá nhân Toàn diện đang chạy nền.</p>
        <div class="info-box">
            <div class="info-row">
                <span class="label">Thời gian máy chủ:</span>
                <span class="value">{now_str}</span>
            </div>
            <div class="info-row">
                <span class="label">Nền tảng:</span>
                <span class="value">Render Web Service</span>
            </div>
            <div class="info-row">
                <span class="label">Telegram Bot:</span>
                <span class="value" style="color: #34d399;">Active</span>
            </div>
            <div class="info-row">
                <span class="label">Cron Scheduler:</span>
                <span class="value" style="color: #34d399;">18:00 T2-T6</span>
            </div>
        </div>
    </div>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Tắt bớt log request định kỳ của UptimeRobot để không làm nghẽn console
        pass


def start_health_server(port: int = None) -> threading.Thread:
    """Khởi động Web server nhẹ chạy ngầm trên một daemon thread."""
    if port is None:
        port = int(os.getenv("PORT", "10000"))

    server = http.server.HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info("🟢 Healthcheck HTTP Server đã khởi động tại cổng 0.0.0.0:%d", port)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server_thread
