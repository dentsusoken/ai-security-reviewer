// Container Registry Module for AI Security Reviewer

@description('Container Registry name (must be globally unique)')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

// ============================================================================
// Container Registry
// ============================================================================

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Container Registry name')
output name string = acr.name

@description('Container Registry login server')
output loginServer string = acr.properties.loginServer

@description('Container Registry resource ID')
output resourceId string = acr.id
