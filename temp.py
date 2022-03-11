from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName: str = "kv-bot-mpeter"
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)
retrieved_secret = client.get_secret("apiKey")
print(f"Your secret is '{retrieved_secret.value}'.")
