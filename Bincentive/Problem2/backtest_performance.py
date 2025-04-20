import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_performance(trades_df, initial_capital=100000):
    """
    計算回測績效指標：
      - 總報酬率：最終資金 / 初始資金 - 1
      - 年化報酬率：依據交易期間計算
      - 夏普值：以每日報酬率計算（無風險利率設 0）
      - 最大回撤 (MDD)
    並建立每日累積損益曲線 (Equity Curve)
    """
    # 依進場時間排序，並計算累積資產曲線
    trades_df = trades_df.sort_values(by='Entry_Time').copy()
    trades_df['Entry_Time'] = pd.to_datetime(trades_df['Entry_Time'])
    trades_df['Exit_Time'] = pd.to_datetime(trades_df['Exit_Time'])
    
    trades_df['Cumulative'] = trades_df['PnL'].cumsum() + initial_capital
    final_capital = trades_df['Cumulative'].iloc[-1] if not trades_df.empty else initial_capital
    total_return = final_capital / initial_capital - 1

    # 交易期間以第一筆進場到最後一筆出場
    if not trades_df.empty:
        start_date = trades_df['Entry_Time'].iloc[0]
        end_date = trades_df['Exit_Time'].iloc[-1]
        days = (end_date - start_date).days
    else:
        days = 0

    if days > 0:
        annualized_return = (1 + total_return) ** (365 / days) - 1
    else:
        annualized_return = 0

    # 以 Exit_Time 為基準，建立每日累積損益曲線
    equity_curve = trades_df[['Exit_Time', 'Cumulative']].dropna().set_index('Exit_Time')
    equity_curve = equity_curve.resample('D').ffill().dropna()
    equity_curve['Daily_Return'] = equity_curve['Cumulative'].pct_change().fillna(0)
    
    if equity_curve['Daily_Return'].std() != 0:
        sharpe_ratio = (equity_curve['Daily_Return'].mean() / equity_curve['Daily_Return'].std()) * np.sqrt(252)
    else:
        sharpe_ratio = 0

    equity_curve['Cumulative_Max'] = equity_curve['Cumulative'].cummax()
    equity_curve['Drawdown'] = equity_curve['Cumulative'] / equity_curve['Cumulative_Max'] - 1
    max_drawdown = equity_curve['Drawdown'].min()
    
    performance = {
        'Total Return': total_return,
        'Annualized Return': annualized_return,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown': max_drawdown
    }
    return performance, equity_curve

def plot_trades(preprocessed_df, trades_df, filename='price_chart.png'):
    """
    繪製價格走勢圖並標示出進場與出場點，並存成 PNG
    """
    # 將時間欄位轉成 datetime 格式，並設定為 index
    preprocessed_df['Open time'] = pd.to_datetime(preprocessed_df['Open time'])
    preprocessed_df = preprocessed_df.set_index('Open time')

    plt.figure(figsize=(14,7))
    plt.plot(preprocessed_df.index, preprocessed_df['Close'], label='Close Price', color='blue')
    
    # 從 trades_df 中取出進場和出場時間及價格
    trades_df['Entry_Time'] = pd.to_datetime(trades_df['Entry_Time'])
    trades_df['Exit_Time'] = pd.to_datetime(trades_df['Exit_Time'])
    
    plt.scatter(trades_df['Entry_Time'], trades_df['Entry_Price'], marker='^', color='green', s=100, label='Buy')
    plt.scatter(trades_df['Exit_Time'], trades_df['Exit_Price'], marker='v', color='red', s=100, label='Sell')
    
    plt.title('Price Chart with Buy & Sell Points')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"價格走勢圖已儲存為 {filename}")

def plot_equity_and_drawdown(equity_curve, filename='equity_drawdown.png'):
    """
    繪製累積損益曲線與回撤曲線，
    上圖為 Equity Curve，下圖為 Drawdown 曲線，並存成 PNG
    """
    fig, axs = plt.subplots(2, 1, figsize=(14,10), sharex=True)
    
    # 累積損益曲線
    axs[0].plot(equity_curve.index, equity_curve['Cumulative'], label='Equity Curve', color='purple')
    axs[0].set_title('Equity Curve / Cumulative PnL')
    axs[0].set_ylabel('Equity')
    axs[0].legend()
    axs[0].grid(True)
    
    # 回撤曲線
    axs[1].plot(equity_curve.index, equity_curve['Drawdown'], label='Drawdown', color='red')
    axs[1].set_title('Drawdown Curve')
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('Drawdown')
    axs[1].legend()
    axs[1].grid(True)
    
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"累積損益及回撤圖已儲存為 {filename}")

def main():
    # 讀取交易明細檔 (trade_details.csv)
    trades_df = pd.read_csv('trade_details.csv')
    
    # 計算績效指標及累積損益曲線
    performance, equity_curve = compute_performance(trades_df, initial_capital=100000)
    
    # 打印績效指標
    print("回測績效指標：")
    print("總報酬率: {:.2%}".format(performance['Total Return']))
    print("年化報酬率: {:.2%}".format(performance['Annualized Return']))
    print("夏普值: {:.2f}".format(performance['Sharpe Ratio']))
    print("最大回撤: {:.2%}".format(performance['Max Drawdown']))
    
    # 儲存每日資產曲線
    equity_curve.to_csv('equity_curve.csv')
    print("每日資產曲線已存檔至 equity_curve.csv")
    
    # 讀取預處理過的資料 (用來畫價格走勢圖)
    preprocessed_df = pd.read_csv('klines_BTC.csv')
    
    # 視覺化：價格圖標示買賣點，存成 PNG
    plot_trades(preprocessed_df, trades_df, filename='price_chart.png')
    
    # 視覺化：累積損益曲線與回撤曲線，存成 PNG
    plot_equity_and_drawdown(equity_curve, filename='equity_drawdown.png')

if __name__ == '__main__':
    main()
