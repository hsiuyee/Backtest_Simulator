import pandas as pd
import numpy as np

# 讀取 CSV 文件
file_path = "klines_BTC.csv"  # 請替換成你的檔案路徑
df = pd.read_csv(file_path)

        # # 設定 window_size
        # window_size = 100

        # # 計算滾動標準差 (Rolling Std)
        # df["Rolling_Std_Close"] = df["Close"].rolling(window=window_size).std()

        # # 計算滾動平均 (Rolling Mean)
        # df["Rolling_Mean_Close"] = df["Close"].rolling(window=window_size).mean()
# 設定 window_size
window_size = 150
gamma = 0.8  # 設定 Gamma Decay 系數

# 計算 Gamma Decay 權重
weights = np.array([gamma**i for i in range(window_size)])
weights /= weights.sum()  # 進行歸一化，使權重總和為 1

# 計算滾動標準差 (Rolling Std) 加上 Gamma Decay
df["Rolling_Std_Close"] = df["Close"].rolling(window=window_size).apply(
    lambda x: np.sqrt(np.dot(weights[::-1], (x - np.dot(x, weights[::-1]))**2)), raw=True
)

# 計算滾動平均 (Rolling Mean) 加上 Gamma Decay
df["Rolling_Mean_Close"] = df["Close"].rolling(window=window_size).apply(
    lambda x: np.dot(x, weights[::-1]), raw=True
)


# 計算 ATR (Average True Range)
df["High-Low"] = df["High"] - df["Low"]
df["High-PrevClose"] = abs(df["High"] - df["Close"].shift(1))
df["Low-PrevClose"] = abs(df["Low"] - df["Close"].shift(1))

df["TR"] = df[["High-Low", "High-PrevClose", "Low-PrevClose"]].max(axis=1)
df["ATR"] = df["TR"].rolling(window=window_size).mean()

# 移除不必要的中間列
df.drop(columns=["High-Low", "High-PrevClose", "Low-PrevClose", "TR"], inplace=True)

# 存回檔案
output_path = "klines_BTC_factors.csv"
df.to_csv(output_path, index=False)

print(f"計算完成，結果已儲存至 {output_path}")
