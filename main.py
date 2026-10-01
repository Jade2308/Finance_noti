"""
VN Finance Hub - Entry point chính của ứng dụng.
Tích hợp Scheduler tự động, Telegram Bot tương tác 2 chiều và Chuyên gia AI phân tích liên thị trường.
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    DAILY_REPORT_HOUR,
    DAILY_REPORT_MINUTE,
    DB_PATH,
    FUND_PORTFOLIO,
    WATCHLIST_INDICES,
)
from data.database import FinanceDatabase
from collectors.fund_collector import FundDataCollector
from collectors.market_collector import MarketDataCollector
from collectors.gold_collector import GoldCollector
from collectors.forex_collector import ForexCollector
from collectors.interest_rate_collector import InterestRateCollector
from collectors.news_collector import NewsCollector
from analysis.fund_analyzer import FundAnalyzer
from analysis.ai_analyst import AIAnalyst
from analysis.sentiment_analyzer import SentimentAnalyzer
from analysis.forecaster import MarketForecaster
from analysis.benchmark import BenchmarkAnalyzer
from notifications.telegram_bot import FinanceTelegramBot
from notifications.message_formatter import MessageFormatter
from notifications.alert_manager import AlertManager
from tools.dca_calculator import DCACalculator
from tools.investment_comparator import InvestmentComparator
from tools.health_server import start_health_server
from education.daily_tips import get_random_tip, format_tip_html

# Thiết lập logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("VNFinanceHub")

# TTL cache dữ liệu thị trường (giây) — tránh gọi API nhiều lần trong 1 phiên
_DATA_CACHE_TTL = 600  # 10 phút


class VNFinanceHubApp:
    """Ứng dụng quản trị và giám sát tài chính liên thị trường VN Finance Hub."""

    def __init__(self):
        logger.info("Initializing VN Finance Hub components...")

        # 1. Database
        self.db = FinanceDatabase(DB_PATH)

        # 2. Collectors (Quỹ mở, VN-Index, Vàng SJC, Ngoại tệ, Lãi suất, Tin tức)
        self.fund_collector = FundDataCollector(db_instance=self.db)
        self.market_collector = MarketDataCollector(db_instance=self.db)
        self.gold_collector = GoldCollector()
        self.forex_collector = ForexCollector()
        self.interest_collector = InterestRateCollector()
        self.news_collector = NewsCollector()

        # 3. Analyzers & Forecasters
        self.fund_analyzer = FundAnalyzer()
        self.forecaster = MarketForecaster()

        # 4. AI Analyst
        self.ai_analyst = AIAnalyst(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)

        # 5. Message Formatter & Alerts & Tools
        self.formatter = MessageFormatter()
        self.alert_manager = AlertManager()
        self.dca_calculator = DCACalculator()
        self.comparator = InvestmentComparator()

        # 6. Telegram Bot
        self.bot = FinanceTelegramBot(
            token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,
            app_controller=self,
        )

        # 7. Scheduler
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        # Cache dữ liệu thị trường — tránh thu thập lại mỗi lần user gõ lệnh
        self._data_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: float = 0.0

    # ─────────────────────────────── Data Collection ───────────────────────────────

    async def collect_and_analyze(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Thu thập dữ liệu thời gian thực và phân tích danh mục toàn diện.
        Kết quả được cache trong 10 phút (_DATA_CACHE_TTL).
        """
        now = time.monotonic()
        if (
            not force_refresh
            and self._data_cache is not None
            and (now - self._cache_timestamp) < _DATA_CACHE_TTL
        ):
            cache_age = int(now - self._cache_timestamp)
            logger.info("Dùng dữ liệu cache (%d giây trước). Bỏ qua thu thập API.", cache_age)
            return self._data_cache

        logger.info("Đang thu thập dữ liệu thị trường...")

        # A. Lấy NAV cho các quỹ trong danh mục
        current_navs: Dict[str, float] = {}
        for fund in FUND_PORTFOLIO:
            code = fund["fund_code"]
            nav_data = self.fund_collector.get_fund_nav(code)
            current_navs[code] = nav_data["nav"]

        # B. Lấy chỉ số thị trường VN-Index
        market_data = self.market_collector.get_vnindex()

        # C. Lấy giá vàng SJC, Tỷ giá USD và Lãi suất
        gold_data = self.gold_collector.get_gold_prices()
        forex_data = self.forex_collector.get_exchange_rates()
        macro_data = self.interest_collector.get_vcb_interest_rates()

        # D. Lấy Top cổ phiếu quỹ VEOF nắm giữ
        fund_holdings = self.fund_collector.get_top_holdings("VEOF")

        # E. Phân tích hiệu suất danh mục
        portfolio_analysis = self.fund_analyzer.analyze_portfolio(
            portfolio_config=FUND_PORTFOLIO,
            current_navs=current_navs,
        )

        # F. Lấy lịch sử và phân tích xu hướng NAV của quỹ chính (VEOF)
        nav_history = self.fund_collector.get_nav_history("VEOF", limit=30)
        nav_trend = self.fund_analyzer.analyze_nav_trend(nav_history)

        # G. Đánh giá tâm lý thị trường (Fear & Greed)
        sentiment_data = SentimentAnalyzer.calculate_fear_and_greed(market_data)

        # H. Dự báo LSTM chạy trong ThreadPoolExecutor
        forecast_data: Dict[str, Any] = {}
        hist_df = self.market_collector.get_historical_vnindex()
        if hist_df is not None:
            logger.info("Đang huấn luyện mô hình LSTM trong thread riêng biệt...")
            forecast_data = await self.forecaster.async_predict_trend_lstm(hist_df)

        # I. Lấy tin tức tài chính mới nhất
        news_data = self.news_collector.get_latest_financial_news(limit=5)

        result = {
            "current_navs": current_navs,
            "market_data": market_data,
            "gold_data": gold_data,
            "forex_data": forex_data,
            "macro_data": macro_data,
            "fund_holdings": fund_holdings,
            "portfolio_analysis": portfolio_analysis,
            "nav_trend": nav_trend,
            "sentiment_data": sentiment_data,
            "forecast_data": forecast_data,
            "news_data": news_data,
        }

        # Lưu cache
        self._data_cache = result
        self._cache_timestamp = time.monotonic()
        logger.info("Thu thập dữ liệu hoàn tất. Cache sẽ hết hạn sau %d giây.", _DATA_CACHE_TTL)
        return result

    def _invalidate_cache(self):
        """Xóa cache để lần gọi tiếp theo sẽ thu thập lại từ API."""
        self._data_cache = None
        self._cache_timestamp = 0.0

    # ─────────────────────────────── Daily Report ───────────────────────────────

    async def generate_and_send_daily_report(self):
        """Tạo và gửi báo cáo phân tích liên thị trường & tâm lý dòng tiền lúc 18:00."""
        logger.info("Bắt đầu quy trình lập báo cáo tài chính hàng ngày...")
        try:
            # force_refresh=True: báo cáo hàng ngày luôn dùng dữ liệu mới nhất
            data = await self.collect_and_analyze(force_refresh=True)

            # Hỏi AI phân tích chuyên sâu
            logger.info("Đang yêu cầu AI Gemini phân tích thị trường và nguyên nhân vĩ mô...")
            ai_commentary = await self.ai_analyst.generate_deep_market_intelligence(
                portfolio_analysis=data["portfolio_analysis"],
                nav_trend=data["nav_trend"],
                market_data=data["market_data"],
                gold_data=data["gold_data"],
                forex_data=data["forex_data"],
                macro_data=data["macro_data"],
                fund_holdings=data["fund_holdings"],
                sentiment_data=data["sentiment_data"],
                forecast_data=data["forecast_data"],
                news_data=data["news_data"],
            )

            # Lấy CPI từ macro_data thực tế, fallback 3.5% nếu không có
            cpi_annual_pct = data.get("macro_data", {}).get("cpi_annual_pct", 3.5)

            # Lấy bank rate từ macro_data
            bank_rate = data["macro_data"].get("benchmark_12m", 4.6) if data.get("macro_data") else 4.6

            # Benchmark loop toàn bộ quỹ
            all_transactions = []
            for fund_analysis in data.get("portfolio_analysis", {}).get("funds", []):
                all_transactions.extend(fund_analysis.get("transactions", []))

            benchmark_summary = BenchmarkAnalyzer.generate_benchmark_summary(
                transactions=all_transactions,
                bank_rate_12m=bank_rate,
                cpi_annual_pct=cpi_annual_pct,
            )

            # Format bản tin
            report_text = self.formatter.format_daily_report(
                portfolio_analysis=data["portfolio_analysis"],
                market_data=data["market_data"],
                nav_trend=data["nav_trend"],
                ai_commentary=ai_commentary,
                gold_data=data["gold_data"],
                forex_data=data["forex_data"],
                sentiment_data=data["sentiment_data"],
                forecast_data=data["forecast_data"],
                news_data=data["news_data"],
                benchmark_summary=benchmark_summary,
            )

            # Gửi qua Telegram
            if self.bot.is_configured():
                await self.bot.send_broadcast_message(report_text)
                self.db.save_notification_log("DAILY_REPORT", report_text, "SENT_TELEGRAM")
                logger.info("Đã gửi báo cáo thành công qua Telegram.")
            else:
                logger.warning("Telegram Bot Token chưa được điền trong .env. Báo cáo hiển thị tại Console:")
                print("\n" + "=" * 60)
                print(report_text)
                print("=" * 60 + "\n")
                self.db.save_notification_log("DAILY_REPORT", report_text, "LOGGED_CONSOLE")

        except Exception as e:
            logger.error("Lỗi trong quá trình lập báo cáo hàng ngày: %s", e, exc_info=True)

    async def send_morning_financial_tip(self):
        """Gửi mẹo tài chính thông minh vào 8:00 sáng hàng ngày."""
        logger.info("Đang chuẩn bị gửi mẹo tài chính buổi sáng...")
        tip_msg = self.get_daily_tip_text()
        if self.bot.is_configured():
            await self.bot.send_broadcast_message(tip_msg)
            self.db.save_notification_log("MORNING_TIP", tip_msg, "SENT_TELEGRAM")
            logger.info("Đã gửi mẹo tài chính buổi sáng thành công.")
        else:
            print("\n[MẸO TÀI CHÍNH BUỔI SÁNG]\n" + tip_msg + "\n")

    # ─────────────────────────────── Controller methods ───────────────────────────────

    async def get_quick_report_text(self) -> str:
        """Sinh chuỗi báo cáo nhanh cho lệnh /report. Dùng cache."""
        data = await self.collect_and_analyze()
        return self.formatter.format_quick_portfolio(data["portfolio_analysis"])

    async def get_quick_market_text(self) -> str:
        """Sinh chuỗi liên thị trường cho lệnh /market. Dùng cache."""
        data = await self.collect_and_analyze()
        return self.formatter.format_quick_market(
            market_data=data["market_data"],
            gold_data=data["gold_data"],
            forex_data=data["forex_data"],
            sentiment_data=data["sentiment_data"],
            forecast_data=data["forecast_data"],
            news_data=data["news_data"],
        )

    async def get_gold_text(self) -> str:
        """Sinh chuỗi chi tiết giá vàng SJC cho lệnh /gold."""
        data = await self.collect_and_analyze()
        return self.formatter.format_gold_detail(data["gold_data"])

    async def get_forex_text(self) -> str:
        """Sinh chuỗi tỷ giá ngoại tệ cho lệnh /forex."""
        data = await self.collect_and_analyze()
        return self.formatter.format_forex_detail(data["forex_data"])

    async def get_news_text(self) -> str:
        """Sinh chuỗi tin tức tài chính cho lệnh /news."""
        data = await self.collect_and_analyze()
        return self.formatter.format_news_detail(data["news_data"])

    async def get_comparison_text(self, capital: float = 1_000_000.0, years: int = 3) -> str:
        """Sinh chuỗi so sánh các kênh đầu tư cho lệnh /compare."""
        data = await self.collect_and_analyze()
        bank_rate = data["macro_data"].get("benchmark_12m", 4.6) if data.get("macro_data") else 4.6
        comp_data = self.comparator.compare_channels(
            initial_capital=capital,
            years=years,
            bank_rate_pct=bank_rate,
        )
        return self.comparator.format_comparison_html(comp_data)

    async def get_dca_text(self, monthly_amount: float = 300_000.0, years: int = 3) -> str:
        """Sinh chuỗi kế hoạch DCA cho lệnh /dca."""
        data = await self.collect_and_analyze()
        bank_rate = data["macro_data"].get("benchmark_12m", 4.6) if data.get("macro_data") else 4.6
        plan = self.dca_calculator.calculate_dca_plan(
            monthly_amount=monthly_amount,
            years=years,
            bank_rate_pct=bank_rate,
        )
        return self.dca_calculator.format_dca_html(plan)

    async def get_alerts_text(self) -> str:
        """Sinh chuỗi cảnh báo thị trường tức thời cho lệnh /alerts."""
        data = await self.collect_and_analyze()
        alerts = self.alert_manager.evaluate_market_alerts(
            market_data=data.get("market_data"),
            nav_trend=data.get("nav_trend"),
            gold_data=data.get("gold_data"),
            forex_data=data.get("forex_data"),
        )
        return self.alert_manager.format_alerts_html(alerts)

    def get_daily_tip_text(self) -> str:
        """Sinh chuỗi mẹo tài chính cho lệnh /tip."""
        tip = get_random_tip()
        return format_tip_html(tip)

    async def get_portfolio_context_for_ai(self) -> Dict[str, Any]:
        """
        Cung cấp toàn bộ bức tranh liên thị trường để AI trả lời câu hỏi chính xác.
        Dùng cache — tránh thu thập lại từ đầu + train LSTM lại mỗi lần user hỏi.
        """
        data = await self.collect_and_analyze()
        return {
            "portfolio": data["portfolio_analysis"],
            "market": data["market_data"],
            "gold": data["gold_data"],
            "forex": data["forex_data"],
            "macro_data": data["macro_data"],
            "fund_holdings": data["fund_holdings"],
            "forecast_data": data["forecast_data"],
            "news_data": data["news_data"],
        }

    # ─────────────────────────────── Scheduler ───────────────────────────────

    def setup_scheduler(self):
        """Thiết lập lịch chạy báo cáo hàng ngày và mẹo tài chính."""
        # 1. Báo cáo phân tích chuyên sâu chiều (18:00 T2-T6)
        self.scheduler.add_job(
            self.generate_and_send_daily_report,
            CronTrigger(
                day_of_week="mon-fri",
                hour=DAILY_REPORT_HOUR,
                minute=DAILY_REPORT_MINUTE,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="daily_finance_report",
            name=f"Báo cáo tài chính hàng ngày lúc {DAILY_REPORT_HOUR:02d}:{DAILY_REPORT_MINUTE:02d}",
            replace_existing=True,
        )
        logger.info(
            "Đã lập lịch báo cáo tự động: T2 - T6 vào %02d:%02d",
            DAILY_REPORT_HOUR,
            DAILY_REPORT_MINUTE,
        )

        # 2. Mẹo tài chính buổi sáng (08:00 hàng ngày)
        self.scheduler.add_job(
            self.send_morning_financial_tip,
            CronTrigger(
                hour=8,
                minute=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="morning_financial_tip",
            name="Mẹo tài chính buổi sáng lúc 08:00",
            replace_existing=True,
        )
        logger.info("Đã lập lịch mẹo tài chính buổi sáng: Mỗi ngày lúc 08:00")

    # ─────────────────────────────── Main run ───────────────────────────────

    async def run(self):
        """Khởi động toàn bộ hệ thống."""
        # Khởi động Healthcheck Web Server cho Render / Cloud PaaS
        start_health_server()

        logger.info("=" * 60)
        logger.info("🚀 VN FINANCE HUB - BẮT ĐẦU HOẠT ĐỘNG")
        logger.info("=" * 60)

        # Lập lịch
        self.setup_scheduler()
        self.scheduler.start()

        # Chạy thử 1 lần tạo báo cáo để xác minh mọi module hoạt động trơn tru
        logger.info("Đang chạy kiểm tra báo cáo ban đầu...")
        await self.generate_and_send_daily_report()

        # Nếu bot đã được cấu hình, khởi chạy Telegram Bot Polling
        if self.bot.is_configured():
            logger.info("Khởi động Telegram Bot Interactive Polling...")
            application = self.bot.build_application()
            await application.initialize()
            await self.bot.register_menu_button(application.bot)
            await application.start()
            await application.updater.start_polling()

            # Giữ tiến trình chạy liên tục
            try:
                while True:
                    await asyncio.sleep(3600)
            except (KeyboardInterrupt, SystemExit):
                logger.info("Đang dừng dịch vụ...")
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
        else:
            logger.info("Hệ thống đang chạy nền kiểm tra định kỳ (Không có Telegram Bot polling).")
            try:
                while True:
                    await asyncio.sleep(3600)
            except (KeyboardInterrupt, SystemExit):
                pass

        self.scheduler.shutdown()
        logger.info("Dịch vụ VN Finance Hub đã dừng an toàn.")


def main():
    """Hàm khởi chạy chính."""
    app = VNFinanceHubApp()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nĐã tắt chương trình theo yêu cầu người dùng.")


if __name__ == "__main__":
    main()
