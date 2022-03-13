from telnetlib import STATUS
import azure.functions as func
import requests
import datetime as dt
from computeRecomendation.src.bot import Bot
from computeRecomendation.src.portfolio import Portfolio
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


def main(timer: func.TimerRequest) -> None:
    keyVaultName: str = "kv-bot-mpeter"
    logicAppURL: str = "https://prod-73.westeurope.logic.azure.com:443/workflows/29e44456a25f4f8d93ba0fdee04491c2/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=2DEIah-cashNcjaD27jbQJfIB-PcEBFzUfNeCF_LUdA"
    KVUri: str = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    apiKey, apiSecret = client.get_secret(
        "apiKey"), client.get_secret("apiSecret")
    bot = Bot(Portfolio(100000000000.0))
    bot.connectToAPI(apiKey.value, apiSecret.value)
    recomendations = bot.getTodaysRecomendation()
    jsonData = []
    for reco in recomendations:
        jsonData.append(
            {
                'symbol': reco['symbol'],
                'price': round(reco['price'], 2),
                'rsi': round(reco['rsi'], 2),
                'macdHistogram': round(reco['macdHistogram'], 2),
                'recomendation': reco['finalRecomendation']
            }
        )
    payload = {
        'date': dt.datetime.now().strftime("%m/%d/%Y"),
        'recomendations': sorted(jsonData, key=lambda d: d['recomendation'])
    }
    requests.post(logicAppURL, json=payload)
