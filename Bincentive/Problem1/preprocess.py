import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_binance_futures_klines(symbol='MINAUSDT', interval='1h',
                                 start_date='2025-01-01', end_date='2025-03-26', limit=1500):
    """
    從 Binance USDT 永續期貨撈取指定交易對的 K 線資料 (OHLCV)。
    回傳 DataFrame 格式，欄位包含 'Open time'、'Open'、'High'、'Low'、'Close'、'Volume'。
    """
    base_url = 'https://fapi.binance.com/fapi/v1/klines'
    
    # 轉換查詢日期為 timestamp (毫秒)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    start_time_ms = int(start_dt.timestamp() * 1000)
    end_time_ms = int(end_dt.timestamp() * 1000)
    
    all_data = []
    while True:
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
            'startTime': start_time_ms,
            'endTime': end_time_ms
        }
        resp = requests.get(base_url, params=params)
        data = resp.json()
        
        if not data or len(data) == 0:
            break
        
        all_data.extend(data)
        last_close_time = data[-1][6]  # K 線的收盤時間 (index=6)
        if last_close_time >= end_time_ms:
            break
        start_time_ms = last_close_time + 1

    # 轉為 DataFrame，並命名欄位
    df = pd.DataFrame(all_data, columns=[
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close time', 'Quote asset volume', 'Number of trades',
        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
    ])

    # 轉換數值型態
    numeric_cols = ['Open','High','Low','Close','Volume','Quote asset volume',
                    'Number of trades','Taker buy base asset volume','Taker buy quote asset volume']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # 轉換時間格式 (UTC) 並僅保留必要欄位
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms', utc=True)
    df = df[['Open time','Open','High','Low','Close','Volume']]
    return df

def fetch_binance_funding_rates(symbol='MINAUSDT', start_date='2025-01-01', end_date='2025-03-26', limit=1000):
    """
    從 Binance 永續期貨 API 撈取 funding rates 的歷史資料，
    並將 fundingTime 欄位轉換成 UTC，且重新命名為 "Open time"。
    """
    base_url = 'https://fapi.binance.com/fapi/v1/fundingRate'
    
    # 日期轉換為 timestamp (毫秒)
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt   = datetime.strptime(end_date, '%Y-%m-%d')
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms   = int(end_dt.timestamp() * 1000)
    
    all_data = []
    while True:
        params = {
            'symbol': symbol,
            'limit': limit,
            'startTime': start_ms,
            'endTime': end_ms
        }
        resp = requests.get(base_url, params=params)
        data = resp.json()
        if not data or len(data) == 0:
            break
        all_data.extend(data)
        if len(data) < limit:
            break
        last_time = int(data[-1]['fundingTime'])
        if last_time >= end_ms:
            break
        start_ms = last_time + 1
    
    df = pd.DataFrame(all_data)
    if not df.empty:
        df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms', utc=True)
        df['fundingRate'] = pd.to_numeric(df['fundingRate'], errors='coerce')
        # 將日期欄位重新命名為 "Open time"
        df.rename(columns={'fundingTime': 'Open time'}, inplace=True)
    return df

def fetch_okx_funding_rates(instId='MINA-USDT-SWAP', start_date='2025-01-01', end_date='2025-03-26', limit=100):
    """
    從 OKX API 撈取 funding rates 的歷史資料，
    處理 fundingTime 欄位可能為數字(毫秒級 timestamp)或 ISO8601 格式字串，
    並統一將日期欄位命名為 "Open time"。
    """
    base_url = 'https://www.okx.com/api/v5/public/funding-rate-history'
    params = {
        'instId': instId,
        'limit': limit
    }
    resp = requests.get(base_url, params=params)
    result = resp.json()
    if result.get('code') != '0':
        print("Error fetching OKX data:", result)
        return pd.DataFrame()
    
    data = result.get('data', [])
    df_okx = pd.DataFrame(data)
    if not df_okx.empty:
        try:
            df_okx['fundingTime_numeric'] = pd.to_numeric(df_okx['fundingTime'], errors='coerce')
        except Exception as e:
            print("轉換 fundingTime 為數值失敗:", e)
            df_okx['fundingTime_numeric'] = None

        # 過濾不合理的 timestamp（例如小於 0 或超過 2100-01-01 的 timestamp）
        df_okx = df_okx[(df_okx['fundingTime_numeric'].isnull()) | 
                        ((df_okx['fundingTime_numeric'] >= 0) & (df_okx['fundingTime_numeric'] <= 4102444800000))]
        
        if df_okx['fundingTime_numeric'].notnull().all():
            df_okx['fundingTime'] = pd.to_datetime(df_okx['fundingTime_numeric'], unit='ms', utc=True)
        else:
            df_okx['fundingTime'] = pd.to_datetime(df_okx['fundingTime'], utc=True)
        
        # 過濾指定區間資料
        start_dt = pd.to_datetime(start_date).tz_localize('UTC')
        end_dt   = pd.to_datetime(end_date).tz_localize('UTC')
        df_okx = df_okx[(df_okx['fundingTime'] >= start_dt) & (df_okx['fundingTime'] <= end_dt)]
        df_okx['fundingRate'] = pd.to_numeric(df_okx['fundingRate'], errors='coerce')
        df_okx = df_okx.drop(columns=['fundingTime_numeric'])
        # 重新命名日期欄位
        df_okx.rename(columns={'fundingTime': 'Open time'}, inplace=True)
    return df_okx

def main():
    # 設定查詢區間
    start_date = '2025-01-01'
    end_date   = '2025-03-26'
    
    # 撈取 Binance Futures K 線資料 (以 Binance API 為主體)
    df_futures = fetch_binance_futures_klines(symbol='MINAUSDT', interval='1h',
                                               start_date=start_date, end_date=end_date)
    
    # 撈取 funding rates 資料 (Binance 與 OKX)
    df_binance_funding = fetch_binance_funding_rates(symbol='MINAUSDT', start_date=start_date, end_date=end_date)
    df_okx_funding = fetch_okx_funding_rates(instId='MINA-USDT-SWAP', start_date=start_date, end_date=end_date)
    
    # 合併 funding rates 資料
    df_funding = pd.concat([df_binance_funding, df_okx_funding], ignore_index=True, sort=True)
    df_funding = df_funding.sort_values(by='Open time')
    
    # 使用 merge_asof 以 futures 資料為主體，根據 "Open time" 近似合併 funding rates 資料
    # 這裡設定容許誤差 tolerance 為 1 小時，可依實際需求調整
    df_futures = df_futures.sort_values("Open time")
    merged_df = pd.merge_asof(df_futures, df_funding, on="Open time", direction="backward", tolerance=timedelta(hours=1))
    
    # 若同一筆 futures 資料可能對應多筆 funding rate 資料，
    # 可進一步處理，例如保留最近一次或依照來源區分，這裡僅做簡單合併
    merged_df.to_csv('raw_MINAUSDT_futures.csv', index=False)
    print("合併後的資料已儲存至 raw_MINAUSDT_futures.csv")
    
if __name__ == '__main__':
    main()
