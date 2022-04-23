from ast import List
import pandas as pd
from __app__.shared.bot import Bot
from __app__.shared.utils import *


class Strategy:
    def __init__(self, bot: Bot) -> None:
        self.historicalTimeSerie: pd.DataFrame = pd.DataFrame()
        self.recommandations: pd.DataFrame = pd.DataFrame()
        self.window: int = 14
        self.bot: Bot = bot

    def initialization(self, historicalData: List) -> None:
        self.historicalTimeSerie = historicalData

    def sellOrbuyAccordingToRecommendation(self, reco: str, price: float, qty: float, date: str) -> None:
        if reco == 'buy':
            self.bot.buyStock(self.bot.symbols[0], qty, price)
            print(reco, qty, 'at', price, 'on the', date)
        elif reco == 'sell':
            self.bot.sellStock(self.bot.symbols[0], qty, price)
            print(reco, qty, 'at', price, 'on the', date)
        else:
            None

    def runSimulation(self, symbol: str, startDate: str, endDate: str) -> None:
        print("Initial wallet", self.bot.getWallet())
        initialMoney = self.bot.getWallet()[0]
        self.initialization(self.bot.getHistoricalData(
            symbol, startDate, endDate))
        evaluation = rsi(self.historicalTimeSerie, self.window)
        macd(evaluation)
        initialPrice = evaluation['price'].iloc[0]
        endPrice = evaluation['price'].iloc[-1]
        generateRecomendationFromRsi(
            evaluation, self.bot.rsiSellThreshold, self.bot.rsiBuyThreshold)
        generateRecomendationFromMacd(evaluation)
        evaluation['qty'] = (self.bot.getWallet()[0] / evaluation['price']) * \
            1 * (100 - evaluation['rsi']) / 100
        generateFinalRecomendation(evaluation)
        print(evaluation)
        priceAndReco = evaluation[[
            'price', 'qty', 'endRecomendation', 'date']]
        evaluation[['date', 'price', 'rsi', 'macd', 'macdSignalLine', 'macdHistogram', 'macdRecomendation', 'rsiRecomendation', 'endRecomendation']].to_csv(
            "metrics.csv", sep=",")
        for i in range(len(priceAndReco)):
            self.sellOrbuyAccordingToRecommendation(
                reco=priceAndReco.iloc[i, 2], price=priceAndReco.iloc[i, 0], qty=priceAndReco.iloc[i, 1], date=priceAndReco.iloc[i, 3])
        endMoney = self.bot.getWallet(
        )[0] + self.bot.getWallet()[1] * priceAndReco.iloc[-1, 0]
        print("Do nothing performance", (endPrice - initialPrice)/initialPrice)
        print("End wallet", self.bot.getWallet())
        print('Gain : ', 100 * (endMoney - initialMoney) / initialMoney, "%")
