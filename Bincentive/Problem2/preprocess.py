import requests
import pandas as pd
from datetime import datetime, timedelta


# 設定 pandas 顯示選項
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def fetch_kline_price_data(symbol, interval, start_date, end_date):
    """
    從 Binance 抓取指定交易對的 K 線數據，包含開高低收量以及 Taker Buy 數據。
    :param symbol: 交易對 (如 'BTCUSDT')
    :param interval: 時間間隔 (如 '1h')
    :param start_date: 開始時間 (如 '2022-01-01')
    :param end_date: 結束時間 (如 '2023-11-30')
    :return: 整理後的 DataFrame
    """
    API_Library = 'v1/klines'
    start_time = datetime.strptime(start_date, '%Y-%m-%d')
    end_time = datetime.strptime(end_date, '%Y-%m-%d')
    # print(start_time, end_time)

    price_data = []

    while start_time < end_time:
        start_time_ms = int(start_time.timestamp() * 1000)
        url = f'https://fapi.binance.com/fapi/{API_Library}?symbol={symbol}&interval={interval}&limit=1500&startTime={start_time_ms}'

        resp = requests.get(url)
        data = resp.json()
        if not data:
            break
        price_data.extend(data)

        # 更新 start_time 為當前抓取到的最後一筆數據的 Close time
        last_entry = data[-1]
        last_close_time = last_entry[6]  # 'Close time' 是數據中的第 7 個元素
        # [
        #   [
        #     1499040000000,      // Kline open time
        #     "0.01634790",       // Open price
        #     "0.80000000",       // High price
        #     "0.01575800",       // Low price
        #     "0.01577100",       // Close price
        #     "148976.11427815",  // Volume
        #     1499644799999,      // Kline Close time
        #     "2434.19055334",    // Quote asset volume
        #     308,                // Number of trades
        #     "1756.87402397",    // Taker buy base asset volume
        #     "28.46694368",      // Taker buy quote asset volume
        #     "0"                 // Unused field, ignore.
        #   ]
        # ]
        start_time = datetime.fromtimestamp(last_close_time / 1000.0)
        start_time_ms = last_close_time + 1

    # 將數據建立為 DataFrame，並指定列名
    price_data = pd.DataFrame(price_data, columns=[
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
        'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
        'Taker buy quote asset volume', 'Ignore'
    ])

    # 清理數據，將所有欄位轉換為數字格式，並刪除包含 NaN 的行
    price_data = price_data.apply(pd.to_numeric, errors='coerce').dropna()

    # 將時間轉換為可讀格式
    price_data['Open time'] = pd.to_datetime(price_data['Open time'], unit='ms')
    price_data['Close time'] = pd.to_datetime(price_data['Close time'], unit='ms')

    # 提取所需的 OHLC 以及 Taker Buy 數據
    extracted_df = price_data[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                               'Taker buy base asset volume', 'Taker buy quote asset volume']]

    extracted_df = extracted_df[
        (extracted_df['Open time'] >= pd.to_datetime(start_date)) &
        (extracted_df['Open time'] < pd.to_datetime(end_date) + timedelta(days=1))
    ]

    return extracted_df


if __name__ == '__main__':
  # symbols
  symbols = ['BTCUSDT']
  interval = '4h'
  start_date = '2021-01-01'
  end_date = '2025-3-24'

  # merge to DataFrame
  all_data = []
  for symbol in symbols:
      df = fetch_kline_price_data(symbol, interval, start_date, end_date)
      df['Symbol'] = symbol  # 標示交易對
      all_data.append(df)

  # reindex
  final_df = pd.concat(all_data, ignore_index=True)

  # save to csv
  final_df.to_csv('klines_BTC.csv', index=False)
  print(final_df.head(100))