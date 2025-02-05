def backtesting(df):
    balance = 100000
    signals = [0] * len(df)
    buy_signals = [0] * len(df)
    sell_signals = [0] * len(df)
    buy_position = [None] * len(df)
    sell_position = [None] * len(df)
    long_entry_price = None
    short_entry_price = None
    exit_price = None
    entry_prices = [None] * len(df)
    exit_prices = [None] * len(df)
    stop_loss = None
    take_profit = None
    lot = 1
    pnl = [None] * len(df)

    for i in range(1, len(df)-1):
        signals[i] = 0
        buy_signals[i] = 0
        sell_signals[i] = 0
        buy_position[i] = buy_position[i-1]
        sell_position[i] = sell_position[i-1]

        # long, take profit and stop loss
        if buy_position[i] == True:
            # take profit (trend, reversion)
            if df.at[i, 'Close'] >= long_entry_price:
                take_profit = (df.at[i, 'Close'] - long_entry_price) * lot
                balance += take_profit
                buy_position[i] = None
                exit_price = df.at[i, 'Close']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
            # stop loss
            elif df.at[i, 'direction'] == -2:
                stop_loss = (long_entry_price - df.at[i, 'Close']) * lot
                balance -= stop_loss
                buy_position[i] = None
                exit_price = df.at[i, 'Close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss

        # short, take profit and stop loss
        if sell_position[i] == True:
            # take profit (trend, reversion)
            if df.at[i, 'Close'] <= short_entry_price:
                take_profit = (short_entry_price - df.at[i, 'Close']) * lot
                balance += take_profit
                sell_position[i] = None
                exit_price = df.at[i, 'Close']
                exit_prices[i] = exit_price
                pnl[i] = take_profit
            # stop loss
            elif df.at[i, 'direction'] == -2:
                stop_loss = (df.at[i, 'Close'] - short_entry_price) * lot
                balance -= stop_loss
                sell_position[i] = None
                exit_price = df.at[i, 'Close']
                exit_prices[i] = exit_price
                pnl[i] = - stop_loss

        if df.at[i, 'direction'] == 1 and buy_position[i] == None:
            buy_signals[i] = 1
            buy_position[i] = True
            long_entry_price = df.at[i, 'Close']
        if df.at[i, 'direction'] == -1 and sell_position[i] == None:
            sell_signals[i] = 1
            sell_position[i] = True
            short_entry_price = df.at[i, 'Close']

    df['buy signal'] = buy_signals
    df['buy position'] = buy_position
    df['sell signals'] = sell_signals
    df['sell position'] = sell_position
    df['long entry price'] = long_entry_price
    df['short entry price'] = short_entry_price
    df['exit price'] = exit_prices
    df['PnL'] = pnl
    return df