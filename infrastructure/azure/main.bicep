// Azure OpenAI Assistant 인프라를 위한 Bicep 템플릿
// Azure Storage Account, Azure Cognitive Search, Azure Functions 등을 생성

@description('환경 (dev, staging, production)')
@allowed(['dev', 'staging', 'production'])
param environment string = 'dev'

@description('Agent 이름')
param agentName string = 'customer-support-agent'

@description('Azure 리전')
param location string = resourceGroup().location

@description('Azure Cognitive Search SKU')
@allowed(['free', 'basic', 'standard', 'standard2', 'standard3'])
param searchSku string = environment == 'production' ? 'standard' : 'basic'

@description('Storage Account SKU')
@allowed(['Standard_LRS', 'Standard_GRS', 'Standard_RAGRS', 'Premium_LRS'])
param storageSku string = 'Standard_LRS'

// 변수 정의
var storageAccountName = '${agentName}kb${environment}${uniqueString(resourceGroup().id)}'
var searchServiceName = '${agentName}-search-${environment}-${uniqueString(resourceGroup().id)}'
var functionAppName = '${agentName}-functions-${environment}-${uniqueString(resourceGroup().id)}'
var appInsightsName = '${agentName}-insights-${environment}-${uniqueString(resourceGroup().id)}'

// Storage Account (Knowledge Base 문서 저장용)
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: storageSku
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
  tags: {
    Project: 'Agentic-AI-Ops'
    Environment: environment
    ManagedBy: 'Bicep'
  }
}

// Blob Container (Knowledge Base 문서용)
resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccount::storageAccount::default
  name: 'knowledge-base'
  properties: {
    publicAccess: 'None'
  }
}

// Azure Cognitive Search (벡터 스토어용)
resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  sku: {
    name: searchSku
  }
  properties: {
    replicaCount: environment == 'production' ? 2 : 1
    partitionCount: environment == 'production' ? 2 : 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
  }
  tags: {
    Project: 'Agentic-AI-Ops'
    Environment: environment
    ManagedBy: 'Bicep'
  }
}

// Application Insights (모니터링용)
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: environment == 'production' ? 90 : 30
  }
  tags: {
    Project: 'Agentic-AI-Ops'
    Environment: environment
    ManagedBy: 'Bicep'
  }
}

// Azure Functions App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${functionAppName}-plan'
  location: location
  sku: {
    name: environment == 'production' ? 'Y1' : 'Y1' // Consumption Plan
    tier: 'Dynamic'
  }
  kind: 'functionapp'
  tags: {
    Project: 'Agentic-AI-Ops'
    Environment: environment
    ManagedBy: 'Bicep'
  }
}

// Azure Functions App (도구 구현용)
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'AZURE_SEARCH_ENDPOINT'
          value: 'https://${searchService.name}.search.windows.net'
        }
        {
          name: 'AZURE_SEARCH_ADMIN_KEY'
          value: searchService.listAdminKeys().primaryKey
        }
        {
          name: 'STORAGE_ACCOUNT_NAME'
          value: storageAccount.name
        }
      ]
      pythonVersion: '3.11'
    }
    httpsOnly: true
  }
  identity: {
    type: 'SystemAssigned'
  }
  tags: {
    Project: 'Agentic-AI-Ops'
    Environment: environment
    ManagedBy: 'Bicep'
  }
}

// Storage Account에 대한 Functions 액세스 권한
resource storageBlobDataContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, functionApp.id, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// 출력값
output storageAccountName string = storageAccount.name
output storageAccountConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
output searchServiceName string = searchService.name
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'
output searchServiceAdminKey string = searchService.listAdminKeys().primaryKey
output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
