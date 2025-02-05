import pandas as pd
import matplotlib.pyplot as plt

# 設定 Pandas 選項
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

plt.style.use('dark_background')

def get_direction(df, threshold1=4, threshold2=2):
    """
    根據價格突破均線標準差範圍來判定趨勢方向
    :param df: DataFrame, 必須包含 'Close', 'Rolling_Mean_Close', 'Rolling_Std_Close' 欄位
    :param threshold: 標準差倍數閥值, 預設為 3
    :return: 更新後的 DataFrame
    """
    trend = 0
    directions = [0] * len(df)  # 預先建立長度相同的陣列，避免錯誤

    for i in range(len(df)):
        if df.at[i, 'Close'] > df.at[i, 'Rolling_Mean_Close'] + threshold1 * df.at[i, 'Rolling_Std_Close']:
                trend = -2
        elif df.at[i, 'Close'] < df.at[i, 'Rolling_Mean_Close'] - threshold1 * df.at[i, 'Rolling_Std_Close']:
                trend = -2
        elif df.at[i, 'Close'] > df.at[i, 'Rolling_Mean_Close'] + threshold2 * df.at[i, 'Rolling_Std_Close'] and \
             df.at[i, 'Close'] < df.at[i, 'Rolling_Mean_Close'] + threshold1 * df.at[i, 'Rolling_Std_Close']:
                trend = -1
        elif df.at[i, 'Close'] < df.at[i, 'Rolling_Mean_Close'] - threshold2 * df.at[i, 'Rolling_Std_Close'] and \
             df.at[i, 'Close'] > df.at[i, 'Rolling_Mean_Close'] - threshold1 * df.at[i, 'Rolling_Std_Close']:
                trend = 1
        directions[i] = trend  # 直接賦值，確保索引正確

    df.loc[:, 'direction'] = directions  # 確保 direction 正確加入 df
    return df

if __name__ == '__main__':
    file_path = "klines_BTC_factors.csv"  # 替換為你的實際檔案路徑
    df = pd.read_csv(file_path)

    # 確保 'Rolling_Mean_Close' 和 'Rolling_Std_Close' 存在
    if 'Rolling_Mean_Close' not in df.columns or 'Rolling_Std_Close' not in df.columns:
        print("請先計算 'Rolling_Mean_Close' 和 'Rolling_Std_Close'!")
    else:
        df = get_direction(df)
        print(df[['Close', 'Rolling_Mean_Close', 'Rolling_Std_Close', 'direction']].head(10))

        # 存回 CSV，確保 direction 寫入
        df.to_csv("klines_BTC_factors_with_direction.csv", index=False)
        print("Direction 已加入，結果儲存為 klines_BTC_factors_with_direction.csv")
