import os
from azure.storage.blob import BlobServiceClient
from azure.storage.blob._models import BlobPrefix
from azure.identity import ClientSecretCredential
import logging

logger = logging.getLogger('app')

STORAGE_URL = os.getenv('AZURE_STORAGE_ACCOUNT_URL')
if not STORAGE_URL:
  raise ValueError("Need to define AZURE_STORAGE_ACCOUNT_URL")

CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
if not CONTAINER_NAME:
  raise ValueError("Need to define AZURE_STORAGE_CONTAINER_NAME")

TENANT_ID = os.getenv("AZURE_TENANT_ID")
if not TENANT_ID:
    raise ValueError("Need to define TENANT_ID environment variable")

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
if not CLIENT_ID:
    raise ValueError("Need to define CLIENT_ID environment variable")

CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
if not CLIENT_SECRET:
    raise ValueError("Need to define CLIENT_SECRET environment variable")


class AzureStorage:

    def __init__(self, app_config):
        
        self.account_url = STORAGE_URL
        self.container_name = CONTAINER_NAME
        
        # Get a token credential for authentication
        token_credential = ClientSecretCredential(
            TENANT_ID,
            CLIENT_ID,
            CLIENT_SECRET
        )
        
        # Create the BlobServiceClient and connect to the storage container
        try:
            self.blob_service_client = BlobServiceClient(account_url=self.account_url, credential=token_credential)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
        except Exception as e:
            logger.error(e)