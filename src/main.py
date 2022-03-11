from bot import Bot
from portfolio import Portfolio
from strategy import Strategy

bot = Bot(Portfolio(100000000000.0))
bot.connectToAPI()
bot.getTodaysRecomendation()

strategy = Strategy(bot)
# strategy.runSimulation(bot.symbols[0], "1 Mar 2019", "11 Nov 2021")
# print(strategy.macd())
# print(bot.getExchangeInfos()["symbols"][0])
# print(bot.getSymbolPrice(coinSymbol="ETHBTC"))
