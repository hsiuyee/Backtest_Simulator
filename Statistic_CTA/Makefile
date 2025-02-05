.PHONY: all preprocess add_factors add_alphas backtest plot_result run

# 各步驟
preprocess:
	$(CD) python3.12 preprocess.py

add_factors: preprocess
	$(CD) python3.12 add_factors.py

add_alphas: add_factors
	$(CD) python3.12 add_alphas.py

backtest: add_alphas
	$(CD) python3.12 backtest.py

plot_result: backtest
	$(CD) python3.12 plot_result.py

# 一鍵執行所有步驟
all: preprocess add_factors add_alphas backtest plot_result

# 執行所有步驟
run: all
