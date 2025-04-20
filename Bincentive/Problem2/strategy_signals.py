import pandas as pd
import numpy as np
from datetime import datetime

def generate_trade_signals(df, fee_rate=0.0005, initial_capital=100000):
    """
    策略邏輯：
      - 當 OBV 從下向上穿越 OBV_MA5 時產生買進訊號 (Signal = 1)
      - 當 OBV 從上向下穿越 OBV_MA5 時產生出場訊號 (Signal = -1)
    模擬進出場：
      - 以當前收盤價進出場
      - 每次進場與出場均扣除單邊 5bp 費用
    回傳：
      - df: 原始 DataFrame 加上 'Signal' 欄位
      - trades: 交易明細清單，每筆包含：進場時間、出場時間、進場價、出場價、手續費、損益
    """
    df = df.copy()
    df['Signal'] = 0
    trades = []
    position = 0   # 0 表示空倉，1 表示持有多單
    entry_price = 0
    entry_time = None
    capital = initial_capital

    # 產生訊號：觀察 OBV 與 OBV_MA5 的交叉
    for i in range(1, len(df)):
        # 當前與前一根的 OBV 與均線
        prev_obv = df.at[i-1, 'OBV']
        prev_ma = df.at[i-1, 'OBV_MA5']
        curr_obv = df.at[i, 'OBV']
        curr_ma = df.at[i, 'OBV_MA5']
        
        # 檢查是否產生買進訊號：從下向上交叉
        if position == 0 and (prev_obv < prev_ma) and (curr_obv >= curr_ma):
            df.at[i, 'Signal'] = 1
            position = 1
            entry_price = df.at[i, 'Close']
            entry_time = df.at[i, 'Open time']
            # 扣除進場手續費
            entry_fee = entry_price * fee_rate
            capital -= entry_fee
            trade = {
                'Entry_Time': entry_time,
                'Entry_Price': entry_price,
                'Entry_Fee': entry_fee,
                'Exit_Time': None,
                'Exit_Price': None,
                'Exit_Fee': None,
                'PnL': None
            }
            trades.append(trade)
            
        # 出場訊號：持有部位且 OBV 從上向下穿越均線
        elif position == 1 and (prev_obv > prev_ma) and (curr_obv <= curr_ma):
            df.at[i, 'Signal'] = -1
            exit_price = df.at[i, 'Close']
            exit_time = df.at[i, 'Open time']
            exit_fee = exit_price * fee_rate
            # 以進出場價格計算獲利（本例僅計算單邊損益，不考慮槓桿）
            gross_profit = exit_price - entry_price
            net_profit = gross_profit - exit_fee
            capital += (net_profit)
            # 更新最後一筆交易明細
            trades[-1].update({
                'Exit_Time': exit_time,
                'Exit_Price': exit_price,
                'Exit_Fee': exit_fee,
                'PnL': net_profit
            })
            position = 0

    # 若最後仍有持倉，則以最後一筆資料平倉
    if position == 1:
        exit_price = df.at[len(df)-1, 'Close']
        exit_time = df.at[len(df)-1, 'Open time']
        exit_fee = exit_price * fee_rate
        gross_profit = exit_price - entry_price
        net_profit = gross_profit - exit_fee
        capital += (net_profit)
        trades[-1].update({
            'Exit_Time': exit_time,
            'Exit_Price': exit_price,
            'Exit_Fee': exit_fee,
            'PnL': net_profit
        })
        df.at[len(df)-1, 'Signal'] = -1

    return df, trades, capital

def main():
    # 讀取預處理過的資料
    df = pd.read_csv('factors_BTC.csv', parse_dates=['Open time'])
    
    # 依據策略產生交易訊號與模擬交易
    df_signals, trades, final_capital = generate_trade_signals(df, fee_rate=0.0005)
    
    # 儲存含策略訊號的資料 (若需要)
    df_signals.to_csv('preprocessed_with_signals.csv', index=False)
    
    # 儲存交易明細表
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv('trade_details.csv', index=False)
    
    print("策略訊號處理完成！")
    print("最終資金餘額: {:.2f}".format(final_capital))
    print("共 {} 筆交易明細已儲存至 trade_details.csv".format(len(trades)))

if __name__ == '__main__':
    main()
