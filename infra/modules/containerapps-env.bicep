// Container Apps Environment Module for AI Security Reviewer

@description('Container Apps Environment name')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Application Insights connection string')
param appInsightsConnectionString string = ''

// ============================================================================
// Container Apps Environment
// ============================================================================

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'azure-monitor'
    }
    daprAIConnectionString: appInsightsConnectionString
    zoneRedundant: false
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Container Apps Environment ID')
output id string = containerAppsEnv.id

@description('Container Apps Environment name')
output name string = containerAppsEnv.name

@description('Container Apps Environment default domain')
output defaultDomain string = containerAppsEnv.properties.defaultDomain
