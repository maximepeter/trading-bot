from ..azureFunctions.computeRecomendation.src.bot import Bot
from ..azureFunctions.computeRecomendation.src.portfolio import Portfolio
from strategy import Strategy

bot = Bot(Portfolio(100000000000.0))
bot.connectToAPI()
bot.getTodaysRecomendation()

strategy = Strategy(bot)
