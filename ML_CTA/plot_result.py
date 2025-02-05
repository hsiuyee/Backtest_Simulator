import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from backtest import backtesting

def plot_result(df, initial_balance=10000, save_path="./backtest_results"):
    """
    視覺化回測結果，分開計算 Training & Testing 的績效指標，包括累積報酬、最大回撤、Sharpe Ratio 和 Win Ratio。

    :param df: 包含回測結果的 DataFrame，應包含 'PnL', 'Close', 'buy signal', 'sell signals' 等欄位
    :param initial_balance: 初始資金
    """
    import os
    os.makedirs(save_path, exist_ok=True)  # 確保儲存資料夾存在
    
    plt.style.use("dark_background")  # 設定背景為黑色

    # 計算測試集的分界點
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]  # 訓練集
    df_test = df.iloc[split_idx:]  # 測試集

    # **計算累積報酬 (Cumulative PnL)**
    df['PnL'].fillna(0, inplace=True)  # 填補空值
    df['Cumulative PnL'] = df['PnL'].cumsum() + initial_balance  # 計算累積報酬

    df_train['Cumulative PnL'] = df_train['PnL'].cumsum() + initial_balance
    df_test['Cumulative PnL'] = df_test['PnL'].cumsum() + df_train['Cumulative PnL'].iloc[-1]  # 讓測試集接續

    # **計算最大回撤 (Max Drawdown)**
    df['Peak'] = df['Cumulative PnL'].cummax()
    df['Drawdown'] = (df['Cumulative PnL'] - df['Peak']) / df['Peak']

    df_train['Peak'] = df_train['Cumulative PnL'].cummax()
    df_train['Drawdown'] = (df_train['Cumulative PnL'] - df_train['Peak']) / df_train['Peak']

    df_test['Peak'] = df_test['Cumulative PnL'].cummax()
    df_test['Drawdown'] = (df_test['Cumulative PnL'] - df_test['Peak']) / df_test['Peak']

    max_drawdown_train = df_train['Drawdown'].min()
    max_drawdown_test = df_test['Drawdown'].min()

    # **計算 Sharpe Ratio**
    daily_return_train = df_train['PnL'] / initial_balance  # 訓練集日報酬
    daily_return_test = df_test['PnL'] / initial_balance  # 測試集日報酬

    sharpe_ratio_train = daily_return_train.mean() / (daily_return_train.std() + 1e-8) * np.sqrt(252)
    sharpe_ratio_test = daily_return_test.mean() / (daily_return_test.std() + 1e-8) * np.sqrt(252)

    # **計算 Win Ratio**
    total_trades_train = (df_train['PnL'] != 0).sum()
    winning_trades_train = (df_train['PnL'] > 0).sum()
    win_ratio_train = winning_trades_train / total_trades_train if total_trades_train > 0 else 0

    total_trades_test = (df_test['PnL'] != 0).sum()
    winning_trades_test = (df_test['PnL'] > 0).sum()
    win_ratio_test = winning_trades_test / total_trades_test if total_trades_test > 0 else 0

    # **顯示績效指標**
    print(f"🔹 Final Balance (Train): {df_train['Cumulative PnL'].iloc[-1]:.2f}")
    print(f"🔹 Final Balance (Test): {df_test['Cumulative PnL'].iloc[-1]:.2f}")
    print(f"🔹 Sharpe Ratio (Train): {sharpe_ratio_train:.2f}")
    print(f"🔹 Sharpe Ratio (Test): {sharpe_ratio_test:.2f}")
    print(f"🔹 Max Drawdown (Train): {max_drawdown_train:.2%}")
    print(f"🔹 Max Drawdown (Test): {max_drawdown_test:.2%}")
    print(f"🔹 Win Ratio (Train): {win_ratio_train:.2%} ({winning_trades_train}/{total_trades_train})")
    print(f"🔹 Win Ratio (Test): {win_ratio_test:.2%} ({winning_trades_test}/{total_trades_test})")

    # **📊 繪製累積報酬變化圖**
    plt.figure(figsize=(12, 6))
    plt.plot(df['Cumulative PnL'], label='Cumulative PnL', color='cyan')
    plt.axvline(x=split_idx, color='yellow', linestyle='--', label="Train-Test Split")
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
    plt.axvline(x=split_idx, color='yellow', linestyle='--', label="Train-Test Split")
    plt.title("Price Movement & Trading Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.savefig(f"{save_path}/price_signals.png", dpi=300, bbox_inches='tight')
    plt.show()

    print(f"✅ 所有圖表已儲存至 {save_path}/")


if __name__ == '__main__':
    file_path = "klines_BTC_factors_with_direction.csv"  # 替換為你的實際檔案路徑
    df = pd.read_csv(file_path)
    df_backtesting = backtesting(df)
    plot_result(df_backtesting)
