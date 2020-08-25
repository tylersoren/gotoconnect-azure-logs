import os
from azure.storage.blob import BlobServiceClient
import logging
import time

logger = logging.getLogger('app')

storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
if not storage_account:
  raise ValueError("Need to define AZURE_STORAGE_ACCOUNT_NAME")

container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
if not container_name:
  raise ValueError("Need to define AZURE_STORAGE_CONTAINER_NAME")

key = os.getenv("AZURE_STORAGE_KEY")
if not key:
    raise ValueError("Need to define AZURE_STORAGE_KEY environment variable")

class AzureStorage:

    def __init__(self):

        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={key};EndpointSuffix=core.windows.net"
        self.container = container_name     
        # Create the BlobServiceClient and connect to the storage container
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        except Exception as e:
            logger.error(e)

    def write_file(self, path_to_file, path=""):
        filename = os.path.basename(path_to_file)
        try:
            # Create a blob client using the local file name as the name for the blob
            blob_client = self.blob_service_client.get_blob_client(container=self.container,
                                                                   blob=(path + filename))
        
            logger.info("Uploading " + filename + " to Azure Storage on path: " + path)

            # Upload the file and measure upload time
            elapsed_time = time.time()
            with open(path_to_file, "rb") as data:
                blob_client.upload_blob(data)
            elapsed_time = round(time.time() - elapsed_time, 2)
            logger.info("Upload succeeded after " + str(elapsed_time) + " seconds for: " + filename)

        except Exception as e:
            logger.error(e)