import pandas as pd
import numpy as np

def compute_cci(df, n=20):
    """
    計算 CCI (Commodity Channel Index)
    CCI = (Typical Price - SMA of TP) / (0.015 * Mean Deviation)
    其中 Typical Price = (High + Low + Close) / 3
    n 為週期，預設 20。
    """
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    sma_tp = tp.rolling(n).mean()
    mad = abs(tp - sma_tp).rolling(n).mean()  # Mean Absolute Deviation
    cci = (tp - sma_tp) / (0.015 * mad)
    return cci

def main():
    # 讀取第一步產生的原始資料
    df = pd.read_csv('raw_MINAUSDT_futures.csv', parse_dates=['Open time'])
    
    # 計算 CCI，預設週期 n=20 (可自行調整)
    df['CCI'] = compute_cci(df, n=30)
    
    # 儲存含 CCI 的結果
    df.to_csv('mina_with_cci.csv', index=False)
    print("計算 CCI 完成，結果已儲存至 mina_with_cci.csv")

if __name__ == '__main__':
    main()
