# gotoconnect-log-collect
Python function to dump GoToConnect Call logs to Azure Storage for further analysis and reporting


# Testing

Since this Function is triggered based on a schedule, to test locally you can't use the normal http endpoint. Instead target the admin path at http://localhost:{port}/admin/functions/{function_name}

Using Powershell it would look like this:

```
Invoke-RestMethod -Method Post -uri http://localhost:7071/admin/functions/schedule-collect-gotoconnect-logs -ContentType 'application/json' -Body '{"input": "just another string"}'
```

You'll notice the body has some dummy input. Even though the function doesn't accept HTTP data, the admin endpoint will fail if you send a post without a body.