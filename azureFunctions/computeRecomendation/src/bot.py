import binance as bn
import pandas as pd
import datetime as dt
import computeRecomendation.src.utils as utils
from ast import List
from typing import Dict
from computeRecomendation.src.portfolio import Portfolio


class Bot:
    def __init__(self, portfolio: Portfolio):
        self.client: bn.Client = None
        self.symbols: List = ["BTCUSDT", "ETHUSDT",
                              "SOLUSDT", "SANDUSDT", "FTMUSDT"]
        self.portfolio: Portfolio = portfolio
        self.rsiBuyThreshold = 35
        self.rsiSellThreshold = 65

    # Update of the attributes

    def setAllSymbols(self) -> None:
        output = []
        for coin in self.getExchangeInfos()["symbols"]:
            output.append(coin["symbol"])
        self.symbols = output

    # APIs interaction
    def connectToAPI(self, apiKey, apiSecret) -> None:
        self.client = bn.Client(apiKey, apiSecret)

    def getExchangeInfos(self) -> Dict:
        return self.client.get_exchange_info()

    def getSymbolPrice(self, coinSymbol: str) -> Dict:
        return float(self.client.get_avg_price(symbol=coinSymbol)["price"])

    def getHistoricalData(self, symbol: str, startDate: str, endDate: str) -> List:
        # The date format should be d m, y like 1 Dec, 2021
        # It returns only the close value for simplification purpose
        rawList = self.client.get_historical_klines(
            symbol, self.client.KLINE_INTERVAL_1DAY, startDate, endDate)
        return pd.DataFrame(list(map(lambda x: (dt.datetime.fromtimestamp(int(x[0] / 1000)).strftime("%d %B, %Y"), float(x[4])), rawList)), columns=["date", "price"])

    def getLastNDays(self, symbol: str, n: int) -> List:
        currentDate = dt.datetime.today()
        currentDateMinusNdays = currentDate - dt.timedelta(days=n)
        formattedDate = "{:%d %b %Y}".format(currentDateMinusNdays)
        rawList = self.client.get_historical_klines(
            symbol=symbol, interval=self.client.KLINE_INTERVAL_1DAY, start_str=formattedDate)
        return pd.DataFrame(list(map(lambda x: (dt.datetime.fromtimestamp(int(x[0] / 1000)).strftime("%d %B, %Y"), float(x[4])), rawList)), columns=["date", "price"])

    def getTodaysRecomendation(self) -> List:
        outputs = []
        window = 40
        for symbol in self.symbols:
            df = self.getLastNDays(symbol, window)
            rsiAndMacd = utils.rsi(df, 14)
            rsiAndMacd["macd"] = utils.macd(rsiAndMacd)
            utils.macdSignalLine(rsiAndMacd)
            utils.macdHistogram(rsiAndMacd)
            utils.generateRecomendationFromMacd(rsiAndMacd)
            utils.generateRecomendationFromRsi(
                rsiAndMacd, self.rsiSellThreshold, self.rsiBuyThreshold)
            utils.generateFinalRecomendation(rsiAndMacd)
            output = {
                "symbol": symbol,
                "rsi": rsiAndMacd.at[window, "rsi"],
                "macdHistogramYesterday": rsiAndMacd.at[window, "macdHistogram"],
                "macdHistogramToday": rsiAndMacd.at[window, "macdHistogram"],
                "macdRecomendation": rsiAndMacd.at[window, "macdRecomendation"],
                "rsiRecomendation": rsiAndMacd.at[window, "rsiRecomendation"],
                "finalRecomendation": rsiAndMacd.at[window, "endRecomendation"]
            }
            outputs.append(output)
        print(outputs)
        return outputs

    # Trading methods

    def buyStock(self, symbol: str, nbStocks: float, price: float) -> None:
        self.portfolio.updateWallet(
            price, nbStocks, "buy")

    def sellStock(self, symbol: str, nbStocks: float, price: float) -> None:
        self.portfolio.updateWallet(price, nbStocks, "sell")

    def getWallet(self) -> float:
        return self.portfolio.getWallet()
