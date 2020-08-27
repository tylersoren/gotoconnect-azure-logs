# GoToConnect Log Collection
This project creates a Python Azure function to dump GoToConnect Call logs to Azure Storage for further analysis and reporting. It creates a separate CSV per day and uploads to separate folders per year and month. 

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

Authentication to GoToConnect is via OAuth and requires that you first create a developer OAuth client at https://developer.logmeininc.com/clients. You will need to keep the client id and secret for input into the application configuration. This requires a callback URL but since this application will not be a web app, you can make it something like http://localhost

Since the application assumes the role of a user, the user must first authorize the application to operate on their behalf to be granted an Authorization token. This token is then passed to the auth API to get an Access Token which is what is used to actually authenticate to the different service APIs and is valid for one hour.  Along with the Access Token, you are given a Refresh Token. This Refresh Token can be used to get new tokens without having to go through the authorization process every time as long as the client authorization scope hasn't changed.  

This whole process is targeted at user interaction via web client and is not well suited to an automated service agent. To work around this, we can manually go through the initial Authorization process and retrieve the refresh token which can then be continually used by our application until it is revoked.

To get a refresh token plug your client ID from the Oauth client you created into this URL in a web browser `https://authentication.logmeininc.com/oauth/authorize?client_id=<client_id>&response_type=code`. This will direct you to an authorization page where you need to log in to GoToConnect and authorize the application.  After successful login it should redirect you to the redirect url appended with `?code=<authorization_code>`. Copy that code and use it to retrieve the first access token and refresh token by posting to the API as follows. {BASIC_AUTH} is the base64 encoded form of `<client_id>:<client_secret>`

```
curl https://authentication.logmeininc.com/oauth/token -H 'Authorization: Basic {BASIC_AUTH}' 
  -H 'Content-Type: application/x-www-form-urlencoded' 
  --data 'grant_type=authorization_code&redirect_uri={REDIRECT_URI}&
    client_id={CLIENT_ID}&code={AUTHORIZATION_CODE}'
```

The API should return with an access_token and refresh_token field.  The refresh_token is required as an application configuration parameter.

Further details on this process are found in the documentation under the [Authorization Code Grant Flow](https://developer.goto.com/Authentication#section/Authorization-Flows/Authorization-Code-Grant)

# Testing

Since this Function is triggered based on a schedule, to test locally you can't use the normal http endpoint. Instead target the admin path at http://localhost:{port}/admin/functions/{function_name}

Using Powershell it would look like this:

```
Invoke-RestMethod -Method Post -uri http://localhost:7071/admin/functions/schedule-collect-gotoconnect-logs -ContentType 'application/json' -Body '{"input": "just another string"}'
```

You'll notice the body has some dummy input. Even though the function doesn't accept HTTP data, the admin endpoint will fail if you send a post without a body.

# Deployment

The app can be deployed manually using the Azure Function Core Tools or by using the VS Code Azure Functions extension.  Using VS code, you can right click on the repo folder and select 'Deploy to Function App'.

(Details on deployment via pipeline to be added)

# References

* [GoToConnect API docs](https://developer.goto.com/GoToConnect)
* [LogMeIn Authentication API docs](https://developer.goto.com/Authentication)
* [Developing Azure Functions in VS Code](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code)
* [Azure Function Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash)