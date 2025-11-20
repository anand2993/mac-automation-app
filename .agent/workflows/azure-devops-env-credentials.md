---
description: Setup .env file and Azure DevOps Pipeline credentials
---

# Azure DevOps Pipeline - Environment Variables & Credentials Setup

## Step 1: Create .env File Locally

### Create .env file in your project root
```bash
cd /Users/anandprakashmishra/Desktop/Danger/mac-automation-app
touch .env
```

### Add your credentials to .env
```bash
# Edit .env file with your credentials
cat > .env << 'EOF'
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_db
DB_USER=admin
DB_PASSWORD=your_secure_password

# API Keys
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here

# Azure Configuration
AZURE_STORAGE_ACCOUNT=mystorageaccount
AZURE_STORAGE_KEY=your_storage_key
AZURE_CONTAINER_NAME=mycontainer

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Other Services
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_email_password
EOF
```

### Add .env to .gitignore (IMPORTANT!)
```bash
# Make sure .env is in .gitignore to avoid committing secrets
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push
```

---

## Step 2: Create .env.example Template

Create a template file that shows what variables are needed (without actual values):

```bash
cat > .env.example << 'EOF'
# Database Configuration
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

# API Keys
API_KEY=
SECRET_KEY=

# Azure Configuration
AZURE_STORAGE_ACCOUNT=
AZURE_STORAGE_KEY=
AZURE_CONTAINER_NAME=

# Application Settings
ENVIRONMENT=
DEBUG=
LOG_LEVEL=

# Other Services
REDIS_URL=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
EOF

git add .env.example
git commit -m "Add .env.example template"
git push
```

---

## Step 3: Add Secrets to Azure DevOps

### Option A: Using Azure DevOps Web UI

1. **Navigate to your Azure DevOps project**:
   - Go to https://dev.azure.com/YOUR_ORGANIZATION/YOUR_PROJECT

2. **Go to Pipelines → Library**:
   - Click on "Pipelines" in the left sidebar
   - Click on "Library"

3. **Create a Variable Group**:
   - Click "+ Variable group"
   - Name it: `mac-automation-app-secrets`
   - Add variables one by one:
     - Click "+ Add"
     - Name: `DB_PASSWORD`
     - Value: `your_actual_password`
     - Click the 🔒 lock icon to make it secret
     - Click "Add" to save

4. **Add all your variables**:
   ```
   DB_HOST          = localhost
   DB_PORT          = 5432
   DB_NAME          = myapp_db
   DB_USER          = admin
   DB_PASSWORD      = ******** (secret)
   API_KEY          = ******** (secret)
   SECRET_KEY       = ******** (secret)
   AZURE_STORAGE_ACCOUNT = mystorageaccount
   AZURE_STORAGE_KEY     = ******** (secret)
   ENVIRONMENT      = production
   ```

5. **Save the Variable Group**

### Option B: Using Azure CLI

```bash
# Install Azure CLI
brew install azure-cli

# Login to Azure DevOps
az login
az devops configure --defaults organization=https://dev.azure.com/YOUR_ORGANIZATION project=YOUR_PROJECT

# Create variable group
az pipelines variable-group create \
  --name mac-automation-app-secrets \
  --variables \
    DB_HOST=localhost \
    DB_PORT=5432 \
    DB_NAME=myapp_db \
    DB_USER=admin

# Add secret variables (these will be encrypted)
az pipelines variable-group variable create \
  --group-id $(az pipelines variable-group list --query "[?name=='mac-automation-app-secrets'].id" -o tsv) \
  --name DB_PASSWORD \
  --value "your_secure_password" \
  --secret true

az pipelines variable-group variable create \
  --group-id $(az pipelines variable-group list --query "[?name=='mac-automation-app-secrets'].id" -o tsv) \
  --name API_KEY \
  --value "your_api_key" \
  --secret true
```

---

## Step 4: Create Azure Pipeline YAML

Create `azure-pipelines.yml` in your project root:

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'
  # Or use self-hosted agent:
  # name: 'Default'

variables:
  - group: mac-automation-app-secrets  # Reference the variable group

stages:
  - stage: Build
    displayName: 'Build and Test'
    jobs:
      - job: BuildJob
        displayName: 'Build Application'
        steps:
          - checkout: self
          
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.11'
              addToPath: true
            displayName: 'Set up Python'
          
          - script: |
              python -m pip install --upgrade pip
              pip install -r requirements.txt
            displayName: 'Install dependencies'
          
          # Create .env file from Azure DevOps secrets
          - script: |
              cat > .env << EOF
              DB_HOST=$(DB_HOST)
              DB_PORT=$(DB_PORT)
              DB_NAME=$(DB_NAME)
              DB_USER=$(DB_USER)
              DB_PASSWORD=$(DB_PASSWORD)
              API_KEY=$(API_KEY)
              SECRET_KEY=$(SECRET_KEY)
              AZURE_STORAGE_ACCOUNT=$(AZURE_STORAGE_ACCOUNT)
              AZURE_STORAGE_KEY=$(AZURE_STORAGE_KEY)
              ENVIRONMENT=$(ENVIRONMENT)
              DEBUG=false
              EOF
              echo ".env file created successfully"
            displayName: 'Create .env file from secrets'
            env:
              DB_PASSWORD: $(DB_PASSWORD)
              API_KEY: $(API_KEY)
              SECRET_KEY: $(SECRET_KEY)
              AZURE_STORAGE_KEY: $(AZURE_STORAGE_KEY)
          
          - script: |
              python -m pytest tests/ -v
            displayName: 'Run tests'
          
          - script: |
              python app/main.py
            displayName: 'Run application'
          
          # Clean up .env file after use
          - script: |
              rm -f .env
            displayName: 'Clean up .env file'
            condition: always()

  - stage: Deploy
    displayName: 'Deploy Application'
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployJob
        displayName: 'Deploy to Production'
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - script: |
                    echo "Deploying application..."
                    # Add your deployment commands here
                  displayName: 'Deploy'
```

---

## Step 5: Alternative - Using Azure Key Vault (Recommended for Production)

### Setup Azure Key Vault

1. **Create Key Vault in Azure Portal**:
   ```bash
   # Using Azure CLI
   az keyvault create \
     --name mac-automation-keyvault \
     --resource-group your-resource-group \
     --location eastus
   ```

2. **Add secrets to Key Vault**:
   ```bash
   az keyvault secret set --vault-name mac-automation-keyvault --name DB-PASSWORD --value "your_password"
   az keyvault secret set --vault-name mac-automation-keyvault --name API-KEY --value "your_api_key"
   az keyvault secret set --vault-name mac-automation-keyvault --name SECRET-KEY --value "your_secret_key"
   ```

3. **Update azure-pipelines.yml to use Key Vault**:
   ```yaml
   variables:
     - group: mac-automation-app-secrets
     - name: azureSubscription
       value: 'YOUR_SERVICE_CONNECTION_NAME'
     - name: keyVaultName
       value: 'mac-automation-keyvault'

   steps:
     - task: AzureKeyVault@2
       inputs:
         azureSubscription: $(azureSubscription)
         KeyVaultName: $(keyVaultName)
         SecretsFilter: '*'
         RunAsPreJob: true
       displayName: 'Fetch secrets from Azure Key Vault'
     
     - script: |
         cat > .env << EOF
         DB_PASSWORD=$(DB-PASSWORD)
         API_KEY=$(API-KEY)
         SECRET_KEY=$(SECRET-KEY)
         EOF
       displayName: 'Create .env from Key Vault secrets'
   ```

---

## Step 6: Using .env in Your Python Application

### Install python-dotenv
```bash
pip install python-dotenv
echo "python-dotenv" >> requirements.txt
```

### Load .env in your code

Update `app/main.py`:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
db_host = os.getenv('DB_HOST')
db_password = os.getenv('DB_PASSWORD')
api_key = os.getenv('API_KEY')
environment = os.getenv('ENVIRONMENT', 'development')

print(f"Running in {environment} environment")
print(f"Connecting to database at {db_host}")

# Use the variables in your application
def get_database_connection():
    return {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
```

---

## Step 7: Commit and Push Pipeline Configuration

```bash
# Add the pipeline file
git add azure-pipelines.yml
git add requirements.txt
git add .env.example
git commit -m "Add Azure DevOps pipeline with environment configuration"
git push
```

---

## Step 8: Setup Pipeline in Azure DevOps

1. **Go to Azure DevOps**:
   - Navigate to Pipelines → Pipelines
   - Click "New Pipeline"

2. **Connect to GitHub**:
   - Select "GitHub"
   - Authorize Azure Pipelines
   - Select your repository: `mac-automation-app`

3. **Configure Pipeline**:
   - Select "Existing Azure Pipelines YAML file"
   - Choose `azure-pipelines.yml`
   - Click "Continue"

4. **Review and Run**:
   - Review the YAML
   - Click "Run"

---

## Security Best Practices

### ✅ DO:
- Always add `.env` to `.gitignore`
- Use Variable Groups for shared secrets
- Mark sensitive values as "secret" in Azure DevOps
- Use Azure Key Vault for production secrets
- Rotate credentials regularly
- Use different credentials for dev/staging/prod
- Clean up `.env` files after pipeline runs

### ❌ DON'T:
- Never commit `.env` files to Git
- Don't hardcode secrets in code
- Don't log secret values
- Don't share secrets in plain text
- Don't use production credentials in development

---

## Troubleshooting

### .env file not loading
```bash
# Check if python-dotenv is installed
pip list | grep python-dotenv

# Verify .env file exists
ls -la .env

# Check file permissions
chmod 600 .env
```

### Variables not available in pipeline
```bash
# Verify variable group is linked in azure-pipelines.yml
# Check variable group permissions in Azure DevOps Library
# Ensure variables are not marked as "Let users override this value"
```

### Secret values showing as empty
```bash
# Secret variables in Azure DevOps are masked in logs
# Use: echo "##vso[task.setvariable variable=myVar;issecret=true]value"
# To debug, check if variable exists (don't print value):
# [ -z "$DB_PASSWORD" ] && echo "DB_PASSWORD is not set" || echo "DB_PASSWORD is set"
```

---

## Quick Reference Commands

```bash
# Create .env locally
touch .env && nano .env

# Add to gitignore
echo ".env" >> .gitignore

# Test .env loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DB_HOST'))"

# View Azure DevOps variable groups
az pipelines variable-group list --output table

# Update a secret in variable group
az pipelines variable-group variable update \
  --group-id GROUP_ID \
  --name VARIABLE_NAME \
  --value "new_value" \
  --secret true
```
