// Azure AI Search Module for AI Security Reviewer
// Provides RAG-based ASVS requirement retrieval for security agents

@description('Azure AI Search resource name')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Search service SKU')
@allowed(['free', 'basic', 'standard'])
param sku string = 'basic'

// ============================================================================
// Azure AI Search Service
// ============================================================================

resource searchService 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    semanticSearch: sku == 'free' ? 'disabled' : 'free'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Azure AI Search resource name')
output name string = searchService.name

@description('Azure AI Search endpoint')
output endpoint string = 'https://${searchService.name}.search.windows.net'
