from ast import List
import pandas as pd
from __app__.shared.bot import Bot
from __app__.shared.utils import *


class Strategy:
    def __init__(self, bot: Bot) -> None:
        self.coinInfos: pd.DataFrame = pd.DataFrame()
        self.recommandations: pd.DataFrame = pd.DataFrame()
        self.window: int = 14
        self.bot: Bot = bot

    def initialization(self, historicalData: List) -> None:
        """Retrieve the coin's historical data provided by the binance client.

        Args:
            historicalData (List): coin's historical data
        """
        self.coinInfos = historicalData

    def sellOrbuyAccordingToRecommendation(self, reco: str, price: float, qty: float, date: str) -> None:
        """Generate the buy and sell recomendation according to the recomendations generated.

        Args:
            reco (str): The recomendation provided ['buy' or 'sell']
            price (float): The coin's price at the evaluation date
            qty (float): The quantity of coin to trade 
            date (str): The evaluation's date
        """
        if reco == 'buy':
            self.bot.buyStock(self.bot.symbols[0], qty, price)
            print(reco, qty, 'at', price, 'on the', date)
        elif reco == 'sell':
            self.bot.sellStock(self.bot.symbols[0], qty, price)
            print(reco, qty, 'at', price, 'on the', date)
        else:
            None

    def runSimulation(self, symbol: str, startDate: str, endDate: str) -> None:
        """Run a trading simulation 

        Args:
            symbol (str): Coin's symbol
            startDate (str): Simulation's start date
            endDate (str): Simulation's end date
        """
        print("Initial wallet", self.bot.getWallet())
        initialMoney = self.bot.getWallet()[0]

        # Initialization phase

        self.initialization(self.bot.getHistoricalData(
            symbol, startDate, endDate))
        initialPrice = self.coinInfos['price'].iloc[0]
        endPrice = self.coinInfos['price'].iloc[-1]

        # Indicators calculation

        rsi(self.coinInfos, self.window)
        macd(self.coinInfos)

        # Recomendation calculation

        generateRecomendationFromRsi(
            self.coinInfos, self.bot.rsiSellThreshold, self.bot.rsiBuyThreshold)
        generateRecomendationFromMacd(self.coinInfos)
        self.coinInfos['qty'] = (self.bot.getWallet()[0] / self.coinInfos['price']) * \
            1 * (100 - self.coinInfos['rsi']) / 100
        generateFinalRecomendation(self.coinInfos)

        # Filter on recomendations and general information only

        priceAndReco = self.coinInfos[[
            'price', 'qty', 'endRecomendation', 'date']]
        self.coinInfos[['date', 'price', 'rsi', 'macd', 'macdSignalLine', 'macdHistogram', 'macdRecomendation', 'rsiRecomendation', 'endRecomendation']].to_csv(
            "metrics.csv", sep=",")

        # Trades simulation according to the recomendations

        for i in range(len(priceAndReco)):
            self.sellOrbuyAccordingToRecommendation(
                reco=priceAndReco.iloc[i, 2], price=priceAndReco.iloc[i, 0], qty=priceAndReco.iloc[i, 1], date=priceAndReco.iloc[i, 3])
        endMoney = self.bot.getWallet(
        )[0] + self.bot.getWallet()[1] * priceAndReco.iloc[-1, 0]

        # Log the strategy performace vs the passive performance

        print("Do nothing performance", 100 *
              (endPrice - initialPrice)/initialPrice, "%")
        print("End wallet", self.bot.getWallet())
        print('Gain : ', 100 * (endMoney - initialMoney) / initialMoney, "%")
