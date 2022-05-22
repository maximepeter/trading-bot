from ast import List
from typing import Dict
import binance as bn
import pandas as pd
import datetime as dt
from .utils import *
from .portfolio import Portfolio


class Bot:
    def __init__(self, portfolio: Portfolio):
        self.client: bn.Client = None
        self.symbols: List = ["BTCUSDT", "XRPBUSD", "ETHUSDT",
                              "SOLUSDT", "SANDUSDT", "FTMUSDT",
                              "ADAUSDT", "BNBBUSD", "LUNABUSD", "AVAXBUSD", "DOTBUSD", "DOGEBUSD"]
        self.portfolio: Portfolio = portfolio
        self.rsiBuyThreshold = 45
        self.rsiSellThreshold = 65

    def getExchangeInfos(self) -> List:
        """Return rate limits and list of symbols

        Returns:
            List: List of product dictionaries
        """
        return self.client.get_exchange_info()

    def setAllSymbols(self) -> None:
        """Update the symbols attribute
        """
        output = []
        for coin in self.getExchangeInfos()["symbols"]:
            output.append(coin["symbol"])
        self.symbols = output

    def connectToAPI(self, apiKey: str, apiSecret: str) -> None:
        """Create the client to connect to the binance's API

        Args:
            apiKey (str): API's key retrieved from the key vault
            apiSecret (str): API's secret retrieved from the key vault
        """
        self.client = bn.Client(apiKey, apiSecret)

    def getSymbolPrice(self, coinSymbol: str) -> float:
        """Get the price for a given coin

        Args:
            coinSymbol (str): Coin's symbol

        Returns:
            float: Current coin's price
        """
        return float(self.client.get_avg_price(symbol=coinSymbol)["price"])

    def getHistoricalData(self, symbol: str, startDate: str, endDate: str) -> List:
        """Get the historical closed prices for a given coin.

        Args:
            symbol (str): Coin to get price information
            startDate (str): Retrieval start date
            endDate (str): Retrieval end date

        Returns:
            List: List of the tuples (timestamp, price).
        """
        # The date format should be d m, y like 1 Dec, 2021
        # It returns only the close value for simplification purpose
        rawList = self.client.get_historical_klines(
            symbol, self.client.KLINE_INTERVAL_1DAY, startDate, endDate)
        return pd.DataFrame(list(map(lambda x: (dt.datetime.fromtimestamp(int(x[0] / 1000)).strftime("%d %B, %Y"), float(x[4])), rawList)), columns=["date", "price"])

    def getLastNDays(self, symbol: str, n: int) -> List:
        """Get the closed prices for a given coin for the last n days.

        Args:
            symbol (str): Coin to get price information
            n (int): Number of days

        Returns:
            List: List of the tuples (timestamp, price).
        """
        currentDate = dt.datetime.today()
        currentDateMinusNdays = currentDate - dt.timedelta(days=n)
        formattedDate = "{:%d %b %Y}".format(currentDateMinusNdays)
        rawList = self.client.get_historical_klines(
            symbol=symbol, interval=self.client.KLINE_INTERVAL_1DAY, start_str=formattedDate)
        return pd.DataFrame(list(map(lambda x: (dt.datetime.fromtimestamp(int(x[0] / 1000)).strftime("%d %B, %Y"), float(x[4])), rawList)), columns=["date", "price"])

    def getTodaysRecomendation(self) -> List:
        """Calculate the recomendation of the day for coins defined a Bot's level.

        Returns:
            List: List of today's recomendation for each coin.
        """
        outputs = []
        window = 40
        for symbol in self.symbols:
            df = self.getLastNDays(symbol, window)
            rsi(df, 14)
            macd(df)
            generateRecomendationFromMacd(df)
            generateRecomendationFromRsi(
                df, self.rsiSellThreshold, self.rsiBuyThreshold)
            generateFinalRecomendation(df)
            output = {
                "symbol": symbol,
                "price": df.at[window, 'price'],
                "rsi": df.at[window, "rsi"],
                "macdHistogram": df.at[window, "macdHistogram"],
                "macdRecomendation": df.at[window, "macdRecomendation"],
                "rsiRecomendation": df.at[window, "rsiRecomendation"],
                "finalRecomendation": df.at[window, "endRecomendation"]
            }
            outputs.append(output)
        return outputs

    # Trading methods

    def buyStock(self, symbol: str, nbStocks: float, price: float) -> None:
        """Update the bot's portfolio after a buy trade.

        Args:
            symbol (str): Coin's symbol
            nbStocks (float): Number of stock to buy
            price (float): Coin's price when the purchase is done
        """
        self.portfolio.updateWallet(
            price, nbStocks, "buy")

    def sellStock(self, symbol: str, nbStocks: float, price: float) -> None:
        """Update the bot's portfolio after a sell trade.

        Args:
            symbol (str): Coin's symbol
            nbStocks (float): Number of stock to sell
            price (float): Coin's price when the sell is done
        """
        self.portfolio.updateWallet(price, nbStocks, "sell")

    def getWallet(self) -> float:
        """Wallet's status retrieval

        Returns:
            float: Wallet's value
        """
        return self.portfolio.getWallet()
