import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from backtest import backtesting


def plot_result(df, initial_balance=10000, save_path="./backtest_results"):
    """
    視覺化回測結果，包括累積報酬、最大回撤、Sharpe Ratio 和 Win Ratio。

    :param df: 包含回測結果的 DataFrame，應包含 'PnL', 'Close', 'buy signal', 'sell signals' 等欄位
    :param initial_balance: 初始資金
    """
    import os
    os.makedirs(save_path, exist_ok=True)  # 確保存儲資料夾存在
    
    plt.style.use("dark_background")  # 設定背景為黑色

    # **計算累積報酬 (Cumulative PnL)**
    df['PnL'].fillna(0, inplace=True)  # 填補空值
    df['Cumulative PnL'] = df['PnL'].cumsum() + initial_balance  # 計算累積報酬

    # **計算最大回撤 (Max Drawdown)**
    df['Peak'] = df['Cumulative PnL'].cummax()
    df['Drawdown'] = (df['Cumulative PnL'] - df['Peak']) / df['Peak']
    max_drawdown = df['Drawdown'].min()  # 取最小值（最大回撤）

    # **計算 Sharpe Ratio**
    daily_return = df['PnL'] / initial_balance  # 假設 PnL 為每日報酬
    sharpe_ratio = daily_return.mean() / (daily_return.std() + 1e-8) * np.sqrt(252)  # 年化 Sharpe Ratio

    # **計算 Win Ratio**
    total_trades = (df['PnL'] != 0).sum()  # 交易總數
    winning_trades = (df['PnL'] > 0).sum()  # 獲利交易數
    win_ratio = winning_trades / total_trades if total_trades > 0 else 0  # 避免除以 0

    # **顯示績效指標**
    print(f"🔹 Final Balance: {df['Cumulative PnL'].iloc[-1]:.2f}")
    print(f"🔹 Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"🔹 Max Drawdown: {max_drawdown:.2%}")
    print(f"🔹 Win Ratio: {win_ratio:.2%} ({winning_trades}/{total_trades})")

    # **📊 繪製累積報酬變化圖**
    plt.figure(figsize=(12, 6))
    plt.plot(df['Cumulative PnL'], label='Cumulative PnL', color='cyan')
    plt.fill_between(df.index, df['Cumulative PnL'], df['Peak'], color='red', alpha=0.3, label="Drawdown")
    plt.title("Cumulative PnL & Drawdown")
    plt.xlabel("Time")
    plt.ylabel("PnL")
    plt.legend()
    plt.grid()
    plt.savefig(f"{save_path}/cumulative_pnl.png", dpi=300, bbox_inches='tight')
    plt.show()

    # **📊 繪製價格走勢與交易信號**
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label="Close Price", color='white')
    plt.scatter(df.index[df['buy signal'] == 1], df['Close'][df['buy signal'] == 1], color='green', label="Buy Signal", marker="^", alpha=1)
    plt.scatter(df.index[df['sell signals'] == 1], df['Close'][df['sell signals'] == 1], color='red', label="Sell Signal", marker="v", alpha=1)
    plt.title("Price Movement & Trading Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.savefig(f"{save_path}/price_signals.png", dpi=300, bbox_inches='tight')
    plt.show()

    # **📊 繪製 PnL 變化圖**
    plt.figure(figsize=(12, 4))
    plt.plot(df['PnL'], label='Daily PnL', color='orange')
    plt.axhline(y=0, color='white', linestyle='--', alpha=0.6)
    plt.title("Daily PnL")
    plt.xlabel("Time")
    plt.ylabel("PnL")
    plt.legend()
    plt.grid()
    plt.savefig(f"{save_path}/daily_pnl.png", dpi=300, bbox_inches='tight')
    plt.show()

    print(f"✅ 所有圖表已儲存至 {save_path}/")


if __name__ == '__main__':
    file_path = "klines_BTC_factors_with_direction.csv"  # 替換為你的實際檔案路徑
    df = pd.read_csv(file_path)
    df_backtesting = backtesting(df)
    plot_result(df_backtesting)