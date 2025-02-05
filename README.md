# Backtest_Simulator

## Statistic_CTA
### Description
* In **Statistic_CTA**, we backtest a CTA strategy.
* We use 11 months of 1-hour K-line data to analyze strategy performance.
* Our strategy is a directional trading strategy.
* The direction of the price trend is determined by the following method:
  1. Precompute the moving average (MV) and moving standard deviation (MSD).
  2. If the closing price is in the range \([MV + \text{threshold}_2 \times MSD, MV + \text{threshold}_1 \times MSD]\), we predict the trend will go down.
  3. Else if the closing price is in the range \([MV - \text{threshold}_1 \times MSD, MV - \text{threshold}_2 \times MSD]\), we predict the trend will go up.
  4. Else if the closing price is greater than \(MV + \text{threshold}_1 \times MSD\) or less than \(MV - \text{threshold}_1 \times MSD\), we stop loss.
* We long/short the spot based on the predicted direction and sell the spot when taking profit or stopping loss is required.
* The intuition behind this strategy is that we assume the closing price exhibits a "mean reversion" behavior.

### Run Code
To run **Statistic_CTA**, execute the following commands:
```sh
cd Statistic_CTA
make all
```

## ML_CTA
### Description
* In **ML_CTA**, we backtest a CTA strategy.
* We use 11 months of 1-hour K-line data to analyze strategy performance.
* Our strategy is also a directional trading strategy.
* The direction of the price trend is determined by the following method:
  1. Use XGBoost to predict the next return.
  2. If the predicted return is higher than the threshold, we predict the direction of the price trend to be either up or down.
* We long/short the spot based on the predicted direction and sell the spot when taking profit or stopping loss based on the ATR index.
* The intuition behind this strategy is that if the ML model predicts well, we can take profit by forecasting price movements.

### Run Code
To run **ML_CTA**, execute the following commands:
```sh
cd ML_CTA
make all
```