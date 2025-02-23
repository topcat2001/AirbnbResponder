# Airbnb Auto-Reply Azure Function

This Azure Function automatically responds to Airbnb guest emails using GPT-4.

## Setup Instructions

1. Install Azure CLI and Azure Functions Core Tools
```bash
brew install azure-cli
brew install azure-functions-core-tools@4
```

2. Login to Azure
```bash
az login
```

3. Create Azure Resources
```bash
# Create Resource Group
az group create --name airbnb-auto-reply --location eastus

# Create Storage Account
az storage account create --name airbnbautoreply --location eastus --resource-group airbnb-auto-reply --sku Standard_LRS

# Create Function App
az functionapp create --resource-group airbnb-auto-reply --consumption-plan-location eastus --runtime python --runtime-version 3.9 --functions-version 4 --name airbnb-auto-reply --storage-account airbnbautoreply --os-type linux
```

4. Configure Application Settings
```bash
az functionapp config appsettings set --name airbnb-auto-reply --resource-group airbnb-auto-reply --settings "OPENAI_API_KEY=your_key_here"
```

5. Deploy Required Files
- Upload these files to Azure:
  - `token.pickle` (Gmail credentials)
  - `client_secret.json` (Google OAuth credentials)
  - `airbnb_info.txt` (Your Airbnb listing information)

6. Deploy the Function
```bash
func azure functionapp publish airbnb-auto-reply
```

## Files
- `function_app.py`: Main Azure Function app
- `AirbnbReply.py`: Core email processing logic
- `requirements.txt`: Python dependencies

## Security Notes
- Store sensitive credentials in Azure Key Vault for production use
- Use Managed Identity for accessing Azure resources
- Regularly rotate API keys and credentials

## Monitoring
- View logs: Azure Portal > Function App > Monitor
- Set up alerts: Azure Portal > Function App > Alerts
- Check execution history: Azure Portal > Function App > Functions > timer_trigger > Monitor
