import pandas as pd

# 讀取 CSV 文件
file_path = "klines_BTC.csv"  # 請替換成你的檔案路徑
df = pd.read_csv(file_path)

# 設定 window_size
window_size = 24

# 計算滾動標準差 (Rolling Std)
df["Rolling_Std_Close"] = df["Close"].rolling(window=window_size).std()

# 計算滾動平均 (Rolling Mean)
df["Rolling_Mean_Close"] = df["Close"].rolling(window=window_size).mean()

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
