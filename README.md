# GoToConnect Log Collection
Python Azure function to dump GoToConnect Call logs to Azure Storage for further analysis and reporting. Creates a separate CSV per day and uploads to separate folders per year and month. 

# Setup

The following environment variables are required to configure various settings and keys:

* DAYS_TO_RETRIEVE(optional) - How many days worth of reports to retrieve. Defaults to 1 with the intention of running the function daily.
* START_DAY(optional) - Starting day in relation to today. i.e -1 is yesterday, -5 is 5 days ago. Defaults to -1. Must be a negative number
* AZURE_STORAGE_KEY - Storage access key for the Azure Storage account
* AZURE_STORAGE_ACCOUNT_NAME - Storage Account name
* AZURE_STORAGE_CONTAINER_NAME - Container in the storage account to upload to. Should be dedicated to this function.
* GOTOCONNECT_REFRESH_TOKEN - Refresh token for retrieving new access tokens. Details on collecting this under 'Authentication'
* GOTOCONNECT_CLIENT_ID - OAuth client ID
* GOTOCONNECT_CLIENT_SECRET - OAuth client secret

For testing this can be set in the local.settings.json file under Values. In the Azure Function, they can be set as Application Settings in Configuration.

## Authentication

(details to come)


# Testing

Since this Function is triggered based on a schedule, to test locally you can't use the normal http endpoint. Instead target the admin path at http://localhost:{port}/admin/functions/{function_name}

Using Powershell it would look like this:

```
Invoke-RestMethod -Method Post -uri http://localhost:7071/admin/functions/schedule-collect-gotoconnect-logs -ContentType 'application/json' -Body '{"input": "just another string"}'
```

You'll notice the body has some dummy input. Even though the function doesn't accept HTTP data, the admin endpoint will fail if you send a post without a body.

# Deployment

(details to come)

# References