# Overview
This repository hosts a trading that aims to trade crypto currency throught the Binance APIs. It is a serverless tool that runs on an Azure function on my personal subscription. 

# Strategy

The main point for this trading bot is to be able to provide the right recomendation at the right time. To do so the first approach is to provide trend trading recomendations. These recomendations are based on these indicators :
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- Exponential Moving Average (EMA)