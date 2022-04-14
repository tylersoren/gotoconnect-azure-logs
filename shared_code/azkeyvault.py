import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class KeyVault():
  def __init__(self) -> None:
    key_vault_name = os.environ["KEY_VAULT_NAME"]
    if not key_vault_name:
      raise ValueError("Need to define KEY_VAULT_NAME")
    KVUri = f"https://{key_vault_name}.vault.azure.net"

    credential = DefaultAzureCredential()
    self.client = SecretClient(vault_url=KVUri, credential=credential)


  def get_secret(self, secret_name):
    return self.client.get_secret(secret_name)

  def set_secret(self, secret_name, secret_value):
    self.client.set_secret(secret_name, secret_value)





