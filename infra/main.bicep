// AI Security Reviewer - Main Bicep Entry Point
// Deploys all required Azure resources for the application

targetScope = 'resourceGroup'

// ============================================================================
// Parameters
// ============================================================================

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Base name for resources')
param baseName string = 'aisecreviewer'

@description('Entra ID tenant ID for authentication')
param entraIdTenantId string = ''

@description('Entra ID client ID for backend API')
param entraIdClientId string = ''

// Note: Azure OpenAI is provisioned by this template, not passed as parameter

@description('Azure OpenAI deployment name')
param azureOpenAiDeployment string = 'gpt-4o'

@description('Container image tag for backend')
param backendImageTag string = 'latest'

// ============================================================================
// Variables
// ============================================================================

var resourcePrefix = '${baseName}-${environment}'
var tags = {
  project: 'ai-security-reviewer'
  environment: environment
  managedBy: 'bicep'
}

// ============================================================================
// Modules
// ============================================================================

// Container Registry for backend images
module acr 'modules/containerregistry.bicep' = {
  name: 'acr-deployment'
  params: {
    name: replace('cr${baseName}${environment}', '-', '')
    location: location
    tags: tags
  }
}

// Key Vault for secrets management
module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault-deployment'
  params: {
    name: 'kv-${resourcePrefix}'
    location: location
    tags: tags
    entraIdTenantId: entraIdTenantId
  }
}

// Cosmos DB for data persistence
module cosmosDb 'modules/cosmosdb.bicep' = {
  name: 'cosmosdb-deployment'
  params: {
    name: 'cosmos-${resourcePrefix}'
    location: location
    tags: tags
  }
}

// Azure OpenAI for AI analysis
module openAi 'modules/openai.bicep' = {
  name: 'openai-deployment'
  params: {
    name: 'oai-${resourcePrefix}'
    location: location
    tags: tags
    deploymentName: azureOpenAiDeployment
  }
}

// Application Insights for monitoring
module appInsights 'modules/appinsights.bicep' = {
  name: 'appinsights-deployment'
  params: {
    name: 'appi-${resourcePrefix}'
    location: location
    tags: tags
  }
}

// Container Apps Environment
module containerAppsEnv 'modules/containerapps-env.bicep' = {
  name: 'containerapps-env-deployment'
  params: {
    name: 'cae-${resourcePrefix}'
    location: location
    tags: tags
    appInsightsConnectionString: appInsights.outputs.connectionString
  }
}

// Backend Container App
module backendApp 'modules/containerapp.bicep' = {
  name: 'backend-app-deployment'
  params: {
    name: 'ca-${resourcePrefix}-api'
    location: location
    tags: tags
    containerAppsEnvId: containerAppsEnv.outputs.id
    containerRegistryName: acr.outputs.name
    containerRegistryLoginServer: acr.outputs.loginServer
    imageName: 'aisecreviewer-api'
    imageTag: backendImageTag
    targetPort: 8000
    envVars: [
      { name: 'ENVIRONMENT', value: environment }
      { name: 'AUTH_DISABLED', value: 'false' }
      { name: 'AZURE_COSMOS_ENDPOINT', value: cosmosDb.outputs.endpoint }
      { name: 'AZURE_COSMOS_DATABASE', value: cosmosDb.outputs.databaseName }
      { name: 'AZURE_OPENAI_ENDPOINT', value: openAi.outputs.endpoint }
      { name: 'AZURE_OPENAI_DEPLOYMENT', value: azureOpenAiDeployment }
      { name: 'ENTRA_TENANT_ID', value: entraIdTenantId }
      { name: 'ENTRA_CLIENT_ID', value: entraIdClientId }
      { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.outputs.connectionString }
    ]
  }
  // Dependencies are implicit through parameter references
}

// Static Web App for frontend
module staticWebApp 'modules/staticwebapp.bicep' = {
  name: 'staticwebapp-deployment'
  params: {
    name: 'swa-${resourcePrefix}'
    location: 'eastasia' // SWA has limited regions
    tags: tags
    backendUrl: backendApp.outputs.fqdn
  }
}

// ============================================================================
// Role Assignments
// ============================================================================

// Grant backend app access to Cosmos DB
module cosmosRoleAssignment 'modules/cosmos-role-assignment.bicep' = {
  name: 'cosmos-role-assignment'
  params: {
    cosmosAccountName: cosmosDb.outputs.name
    principalId: backendApp.outputs.identityPrincipalId
  }
}

// Grant backend app access to Key Vault
module keyVaultRoleAssignment 'modules/keyvault-role-assignment.bicep' = {
  name: 'keyvault-role-assignment'
  params: {
    keyVaultName: keyVault.outputs.name
    principalId: backendApp.outputs.identityPrincipalId
  }
}

// Grant backend app access to Azure OpenAI
module openAiRoleAssignment 'modules/openai-role-assignment.bicep' = {
  name: 'openai-role-assignment'
  params: {
    openAiAccountName: openAi.outputs.name
    principalId: backendApp.outputs.identityPrincipalId
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Backend API URL')
output backendUrl string = 'https://${backendApp.outputs.fqdn}'

@description('Frontend URL')
output frontendUrl string = staticWebApp.outputs.defaultHostname

@description('Container Registry login server')
output acrLoginServer string = acr.outputs.loginServer

@description('Cosmos DB endpoint')
output cosmosEndpoint string = cosmosDb.outputs.endpoint

@description('Key Vault URI')
output keyVaultUri string = keyVault.outputs.uri

@description('Application Insights connection string')
output appInsightsConnectionString string = appInsights.outputs.connectionString

@description('Azure OpenAI endpoint')
output openAiEndpoint string = openAi.outputs.endpoint
