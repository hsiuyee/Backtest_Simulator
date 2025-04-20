.PHONY: all preprocess add_factors backtest_performance clean

all: preprocess add_factors backtest_performance

preprocess:
	python3.12 preprocess.py
	
add_factors:
	python3.12 add_factors.py

backtest_performance:
	python3.12 backtest_performance.py

clean:
	@echo "No clean steps defined."
