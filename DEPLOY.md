# Deploying PDFChatbot to Azure (Container Image)

This guide covers deploying the PDF Chatbot as a Docker container to **Azure Container Apps**.

## Architecture

```
User → Azure Container Apps (HTTPS) → Docker Container
                                        ├── Streamlit Frontend (:8501)
                                        └── FastAPI Backend (:8000)
```

Both services run inside a single container managed by `supervisord`.

---

## Prerequisites

1. **Docker Desktop** — [Install](https://docs.docker.com/desktop/install/windows-install/)
2. **Azure CLI** — [Install](https://aka.ms/installazurecliwindows)
3. **Azure Subscription** — [Free tier](https://azure.microsoft.com/free/)

Login to Azure:
```powershell
az login
```

---

## Option 1: One-Command Deployment (Recommended)

Run the deployment script from the project root:

```powershell
.\deploy-azure.ps1
```

This will:
1. Create an Azure Resource Group
2. Create an Azure Container Registry (ACR)
3. Build & push the Docker image
4. Create a Container Apps Environment
5. Deploy the app with your `.env` secrets
6. Print the live URL

### Customize Parameters

```powershell
.\deploy-azure.ps1 -ResourceGroup "my-rg" -Location "eastus" -AcrName "myacr" -AppName "mychatbot"
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `-ResourceGroup` | `pdfchatbot-rg` | Azure Resource Group name |
| `-Location` | `centralindia` | Azure region |
| `-AcrName` | `pdfchatbotacr` | Container Registry name (must be globally unique) |
| `-AppName` | `pdfchatbot` | Container App name |
| `-ImageTag` | `latest` | Docker image tag |

---

## Option 2: Step-by-Step Manual Deployment

### 1. Build the Docker Image Locally

```powershell
docker build -t pdfchatbot .
```

### 2. Test Locally

```powershell
docker run -p 8501:8501 -p 8000:8000 --env-file .env pdfchatbot
```

Visit [http://localhost:8501](http://localhost:8501) to verify it works.

### 3. Create Azure Resources

```powershell
# Create Resource Group
az group create --name pdfchatbot-rg --location centralindia

# Create Container Registry
az acr create --resource-group pdfchatbot-rg --name pdfchatbotacr --sku Basic --admin-enabled true

# Login to ACR
az acr login --name pdfchatbotacr
```

### 4. Tag and Push Image

```powershell
$ACR_SERVER = az acr show --name pdfchatbotacr --query loginServer --output tsv

docker tag pdfchatbot "${ACR_SERVER}/pdfchatbot:latest"
docker push "${ACR_SERVER}/pdfchatbot:latest"
```

### 5. Deploy to Container Apps

```powershell
# Install/update extension
az extension add --name containerapp --upgrade --yes
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait

# Create environment
az containerapp env create --name pdfchatbot-env --resource-group pdfchatbot-rg --location centralindia

# Get ACR credentials
$ACR_USER = az acr credential show --name pdfchatbotacr --query username --output tsv
$ACR_PASS = az acr credential show --name pdfchatbotacr --query "passwords[0].value" --output tsv

# Deploy
az containerapp create `
    --name pdfchatbot `
    --resource-group pdfchatbot-rg `
    --environment pdfchatbot-env `
    --image "${ACR_SERVER}/pdfchatbot:latest" `
    --registry-server $ACR_SERVER `
    --registry-username $ACR_USER `
    --registry-password $ACR_PASS `
    --target-port 8501 `
    --ingress external `
    --cpu 2 --memory 4Gi `
    --min-replicas 0 --max-replicas 3 `
    --env-vars OLLAMA_MODEL="your-model" OLLAMA_BASE_URL="your-url" OLLAMA_API_KEY="your-key"
```

### 6. Get Your App URL

```powershell
az containerapp show --name pdfchatbot --resource-group pdfchatbot-rg --query "properties.configuration.ingress.fqdn" --output tsv
```

---

## Managing Your Deployment

### View Logs
```powershell
az containerapp logs show --name pdfchatbot --resource-group pdfchatbot-rg --follow
```

### Update After Code Changes
```powershell
docker build -t "${ACR_SERVER}/pdfchatbot:latest" .
docker push "${ACR_SERVER}/pdfchatbot:latest"
az containerapp update --name pdfchatbot --resource-group pdfchatbot-rg --image "${ACR_SERVER}/pdfchatbot:latest"
```

### Scale Configuration
```powershell
# Always-on (no cold starts)
az containerapp update --name pdfchatbot --resource-group pdfchatbot-rg --min-replicas 1

# Scale to zero (saves cost)
az containerapp update --name pdfchatbot --resource-group pdfchatbot-rg --min-replicas 0
```

### Custom Domain
```powershell
# Add custom domain
az containerapp hostname add --name pdfchatbot --resource-group pdfchatbot-rg --hostname chatbot.yourdomain.com

# Bind managed certificate (free TLS)
az containerapp hostname bind --name pdfchatbot --resource-group pdfchatbot-rg --hostname chatbot.yourdomain.com --environment pdfchatbot-env --validation-method CNAME
```

### Delete Everything
```powershell
az group delete --name pdfchatbot-rg --yes --no-wait
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Container keeps restarting | Check logs: `az containerapp logs show ...`. Likely a missing env var. |
| Cold start is slow (~30-60s) | Expected due to ML model loading. Set `--min-replicas 1` to avoid. |
| Upload fails | Container Apps has a 30MB default request limit. For larger PDFs, adjust in Container App settings. |
| ACR name taken | ACR names must be globally unique. Try a different `--AcrName`. |
| `az containerapp` not found | Run `az extension add --name containerapp --upgrade --yes` |

---

## Cost Estimate

With **Azure Container Apps** (Consumption plan):

| Usage | Estimated Monthly Cost |
|-------|----------------------|
| Low traffic (scale to zero) | **$0 - $5** (free tier covers most) |
| Moderate (always-on, 1 replica) | **~$30 - $50** |
| High (auto-scaling) | **Varies by usage** |

The free tier includes **180,000 vCPU-seconds** and **360,000 GiB-seconds** per month.
