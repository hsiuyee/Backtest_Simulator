import pandas as pd
import numpy as np

def compute_OBV(df):
    """
    計算 OBV (On Balance Volume)
      - 當日收盤價大於前一日，累加當日成交量
      - 當日收盤價小於前一日，扣除當日成交量
      - 否則 OBV 不變
    """
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return obv

def main():
    # 讀入原始 K 線資料
    df = pd.read_csv('klines_BTC.csv')
    
    # 假設原始資料中 'Open time' 為時間欄位，已轉換成 pandas datetime 格式（若尚未轉換，可自行轉換）
    df['Open time'] = pd.to_datetime(df['Open time'])
    
    # 依需求，若有其他資料處理步驟也可在此處加入
    
    # 計算 OBV 指標
    df['OBV'] = compute_OBV(df)
    
    # 計算 5 期 OBV 均線
    df['OBV_MA5'] = df['OBV'].rolling(window=25).mean()
    
    # 儲存預處理結果
    df.to_csv('factors_BTC.csv', index=False)
    print("預處理完成，結果存檔至 factors_BTC.csv")

if __name__ == '__main__':
    main()
