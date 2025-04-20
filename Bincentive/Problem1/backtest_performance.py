import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generate_cci_signals(df, upper=100, lower=-100):
    """
    根據 CCI 產生買賣訊號。
    預設:
      - CCI < -100 => Buy (超賣)
      - CCI > 100  => Sell (超買)
    回傳新的 DataFrame，包含 'Signal' 欄位:
      1 => Buy
     -1 => Sell
      0 => 無訊號
    """
    df = df.copy()
    df['Signal'] = 0
    
    # 當 CCI 從上往下穿越 lower => 產生買進訊號
    # 當 CCI 從下往上穿越 upper => 產生賣出訊號
    for i in range(1, len(df)):
        prev_cci = df.loc[i-1, 'CCI']
        curr_cci = df.loc[i, 'CCI']
        
        # 買進訊號: 由上而下穿越 lower
        if prev_cci >= lower and curr_cci < lower:
            df.loc[i, 'Signal'] = 1
        
        # 賣出訊號: 由下而上穿越 upper
        if prev_cci <= upper and curr_cci > upper:
            df.loc[i, 'Signal'] = -1
    
    return df

def plot_cci_signals(df, filename='cci_signals.png'):
    """
    視覺化價格與 CCI 指標，並在圖上標示買賣點。
    """
    # 將時間設為 index
    df['Open time'] = pd.to_datetime(df['Open time'])
    df.set_index('Open time', inplace=True)
    
    # 建立子圖
    fig, axs = plt.subplots(2, 1, figsize=(14,10), sharex=True)
    
    # 第一張子圖: 價格
    axs[0].plot(df.index, df['Close'], label='Close Price', color='blue')
    # 在買點畫綠色三角形向上，賣點畫紅色三角形向下
    buy_points = df[df['Signal'] == 1]
    sell_points = df[df['Signal'] == -1]
    axs[0].scatter(buy_points.index, buy_points['Close'], marker='^', color='green', s=100, label='Buy')
    axs[0].scatter(sell_points.index, sell_points['Close'], marker='v', color='red', s=100, label='Sell')
    
    axs[0].set_ylabel('Price')
    axs[0].set_title('MINAUSDT Price with CCI Signals')
    axs[0].legend()
    axs[0].grid(True)
    
    # 第二張子圖: CCI 指標
    axs[1].plot(df.index, df['CCI'], label='CCI', color='purple')
    axs[1].axhline(y=100, color='gray', linestyle='--', label='Upper = 100')
    axs[1].axhline(y=-100, color='gray', linestyle='--', label='Lower = -100')
    
    axs[1].set_ylabel('CCI')
    axs[1].set_xlabel('Date')
    axs[1].grid(True)
    axs[1].legend()
    
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"視覺化圖已儲存為 {filename}")

def main():
    # 讀取含 CCI 的資料
    df = pd.read_csv('mina_with_cci.csv')
    
    # 產生買賣訊號
    df_signals = generate_cci_signals(df, upper=100, lower=-100)
    
    # 繪製圖表 (價格 + CCI + 買賣點)
    plot_cci_signals(df_signals, filename='cci_signals.png')

if __name__ == '__main__':
    main()
