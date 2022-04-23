from __app__.shared.bot import Bot
from __app__.shared.portfolio import Portfolio
from strategy import Strategy
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Retrieve keys
keyVaultName: str = "kv-bot-mpeter"
KVUri: str = f"https://{keyVaultName}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)
apiKey, apiSecret = client.get_secret(
    "apiKey"), client.get_secret("apiSecret")

bot = Bot(Portfolio(100000000000.0))
bot.connectToAPI(apiKey.value, apiSecret.value)
bot.getTodaysRecomendation()

strategy = Strategy(bot)
strategy.runSimulation('BTCUSDT', "1 Jan 2022", "22 Apr 2022")
