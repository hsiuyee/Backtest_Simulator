import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def load_data(file_path, N):
    """
    讀取 CSV 文件，計算未來 N 小時的報酬，並處理 NaN 值
    :param file_path: CSV 檔案路徑
    :param N: 預測 N 小時後的報酬
    :return: pandas DataFrame
    """
    df = pd.read_csv(file_path)
    df['Future_Return_N'] = (df['Close'].shift(-N) - df['Close']) / df['Close']
    df['Future_Return_N'] *= 100
    df.dropna(inplace=True)
    return df

def prepare_features(df):
    """
    定義技術指標作為特徵，並準備 X (特徵矩陣) 和 y (目標變數)
    :param df: pandas DataFrame
    :return: X (特徵矩陣), y (預測目標)
    """
    features = [
        # 'Open', 'High', 'Low', 'Close', 'Volume',
                # 'Taker buy base asset volume', 'Taker buy quote asset volume', 
                'Rolling_Std_Close', 'Rolling_Mean_Close', 'ATR']
    # features = ['Rolling_Std_Close']

    X = df[features]
    y = df['Future_Return_N']

    return X, y

def train_xgboost(X, y, test_size=0.7):
    """
    訓練 XGBoost 模型，並計算 MAE
    :param X: 特徵矩陣
    :param y: 目標變數
    :param test_size: 測試集比例 (預設 20%)
    :return: 訓練好的 XGBoost 模型, 測試集 y 值, 預測值, MAE
    """
    # 分割訓練集與測試集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)

    # 訓練 XGBoost 模型
    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100)
    model.fit(X_train, y_train)

    # 預測未來 N 小時報酬
    y_pred = model.predict(X)

    # 計算 Mean Absolute Error (MAE)
    mae = mean_absolute_error(y_test, model.predict(X_test))

    return model, y_pred, mae

def get_direction(df, threshold=0.05):
    """
    根據預測結果產生交易信號，並儲存結果
    :param df: pandas DataFrame，應包含 Predicted_Return 欄位
    :param threshold: 設定交易閾值
    """
    df['direction'] = 0
    df.loc[df['Predicted_Return'] > threshold, 'direction'] = 1   # Long
    df.loc[df['Predicted_Return'] < -threshold, 'direction'] = -1  # Short
    
    # 儲存結果
    df.to_csv("klines_BTC_factors_with_direction.csv", index=False)
    print("✅ Direction 已加入，結果儲存為 klines_BTC_factors_with_direction.csv")

if __name__ == "__main__":
    file_path = "klines_BTC_factors.csv"
    N = 24 * 10

    # 讀取數據
    df = load_data(file_path, N)

    # 準備特徵
    X, y = prepare_features(df)

    # 訓練模型 & 預測
    model, y_pred, mae = train_xgboost(X, y)

    # 將預測結果加入 df
    df['Predicted_Return'] = y_pred

    print(f"MAE: {mae:.4f}")

    # 產生交易信號
    get_direction(df)
