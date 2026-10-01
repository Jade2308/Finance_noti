"""
Market Forecaster - Dự báo xu hướng thị trường sử dụng Deep Learning (LSTM).

⚠️ QUAN TRỌNG VỀ ĐỘ TIN CẬY:
- Đây là mô hình thống kê đơn biến (chỉ dùng giá đóng cửa).
- Chỉ dự báo xu hướng ngắn hạn (1 phiên tiếp theo), không phải dự báo giá chính xác.
- Kết quả mang tính tham khảo, KHÔNG phải cơ sở để ra quyết định mua/bán.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Seed cố định để kết quả tái lập được (reproducible) mỗi lần chạy
RANDOM_SEED = 42


class MarketForecaster:
    """Sử dụng mô hình Học sâu (LSTM) để dự báo xu hướng VN-Index."""

    def __init__(self):
        self.look_back = 30  # Sử dụng 30 phiên gần nhất để dự báo phiên tiếp theo

    def _prepare_data(self, df):
        """Chuẩn bị dữ liệu cho mô hình Time Series."""
        from sklearn.preprocessing import MinMaxScaler

        data = df['close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        X, y = [], []
        for i in range(self.look_back, len(scaled_data)):
            X.append(scaled_data[i - self.look_back:i, 0])
            y.append(scaled_data[i, 0])

        return np.array(X), np.array(y), scaler, scaled_data

    def _run_lstm_sync(self, df) -> Dict[str, Any]:
        """
        Phần CPU-intensive chạy đồng bộ trong thread riêng biệt.
        Được gọi qua run_in_executor để không block event loop.
        """
        if df is None or len(df) < 60:
            return {"error": "Không đủ dữ liệu lịch sử (cần ít nhất 60 phiên)."}

        try:
            import torch
            import torch.nn as nn

            # Đặt seed cố định để kết quả tái lập được
            torch.manual_seed(RANDOM_SEED)
            np.random.seed(RANDOM_SEED)

            # 1. Chuẩn bị dữ liệu
            X, y, scaler, scaled_data = self._prepare_data(df)
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            X_tensor = torch.tensor(X, dtype=torch.float32)
            y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1)

            # 2. Định nghĩa mô hình LSTM
            class SimpleLSTM(nn.Module):
                def __init__(self, input_size=1, hidden_size=32, num_layers=1, output_size=1):
                    super(SimpleLSTM, self).__init__()
                    self.hidden_size = hidden_size
                    self.num_layers = num_layers
                    self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                    self.fc = nn.Linear(hidden_size, output_size)

                def forward(self, x):
                    h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                    c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                    out, _ = self.lstm(x, (h0.detach(), c0.detach()))
                    out = self.fc(out[:, -1, :])
                    return out

            model = SimpleLSTM()
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

            # 3. Huấn luyện 150 epochs
            EPOCHS = 150
            model.train()
            final_loss = 0.0
            for epoch in range(EPOCHS):
                outputs = model(X_tensor)
                optimizer.zero_grad()
                loss = criterion(outputs, y_tensor)
                loss.backward()
                optimizer.step()
                final_loss = loss.item()

            # 4. Dự báo phiên tiếp theo
            last_sequence = scaled_data[-self.look_back:]
            last_seq_tensor = torch.tensor(last_sequence, dtype=torch.float32).view(1, self.look_back, 1)

            model.eval()
            with torch.no_grad():
                predicted_scaled = model(last_seq_tensor).item()

            predicted_value = scaler.inverse_transform([[predicted_scaled]])[0][0]
            current_value = df['close'].iloc[-1]

            change = predicted_value - current_value
            change_pct = (change / current_value) * 100

            if abs(change_pct) < 0.2:
                trend = "Đi ngang"
            elif change > 0:
                trend = "Tăng"
            else:
                trend = "Giảm"

            # Đánh giá mức độ tin cậy dựa trên final loss
            # Loss < 0.001 → mô hình học tốt; Loss > 0.005 → kém tin cậy
            if final_loss < 0.001:
                confidence = "Trung bình"
            elif final_loss < 0.005:
                confidence = "Thấp"
            else:
                confidence = "Rất thấp"

            return {
                "model": "LSTM (PyTorch, 1 biến, 30 phiên look-back)",
                "predicted_next_day": float(predicted_value),
                "predicted_change_pct": float(change_pct),
                "trend_forecast": trend,
                "training_loss": round(final_loss, 6),
                "confidence": confidence,
                "disclaimer": "⚠️ Dự báo thống kê ngắn hạn (1 phiên), chỉ mang tính tham khảo. Không phải khuyến nghị đầu tư.",
                "error": False,
            }

        except ImportError:
            return {"error": "Chưa cài đặt PyTorch hoặc Scikit-Learn."}
        except Exception as e:
            logger.error("[Forecaster] Lỗi mô hình LSTM: %s", e)
            return {"error": f"Lỗi mô hình LSTM: {e}"}

    def predict_trend_lstm(self, df) -> Dict[str, Any]:
        """
        Wrapper đồng bộ — giữ lại để backward-compatible.
        Dùng async_predict_trend_lstm trong main.py để tránh block event loop.
        """
        return self._run_lstm_sync(df)

    async def async_predict_trend_lstm(self, df, timeout_seconds: float = 30.0) -> Dict[str, Any]:
        """
        Chạy LSTM trong ThreadPoolExecutor để không block asyncio event loop.
        Bổ sung timeout để tránh treo luồng nếu dữ liệu bất thường.
        """
        loop = asyncio.get_event_loop()
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self._run_lstm_sync, df),
                timeout=timeout_seconds,
            )
            return result
        except asyncio.TimeoutError:
            logger.error("[Forecaster] LSTM training quá thời gian quy định (%s s). Bỏ qua dự báo.", timeout_seconds)
            return {"error": f"Quá thời gian huấn luyện LSTM ({timeout_seconds}s).", "disclaimer": "⚠️ Bỏ qua dự báo do timeout."}

