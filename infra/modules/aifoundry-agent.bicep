// Azure AI Foundry Agent Module for AI Security Reviewer
// Provides AI Agent Service configuration referencing Azure OpenAI
// Note: Azure AI Agent Service is accessed via Azure OpenAI endpoints.
// This module provisions the supporting AI Search + connects to OpenAI.

@description('Resource name prefix')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Azure OpenAI account name for agent backing')
param openAiAccountName string

@description('Azure AI Search service name for ASVS RAG')
param searchServiceName string

// ============================================================================
// References to existing resources
// ============================================================================

resource openAiAccount 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' existing = {
  name: openAiAccountName
}

resource searchService 'Microsoft.Search/searchServices@2024-03-01-preview' existing = {
  name: searchServiceName
}

// ============================================================================
// Outputs (endpoints resolved for Key Vault / app config)
// ============================================================================

@description('OpenAI endpoint for agent access')
output openAiEndpoint string = openAiAccount.properties.endpoint

@description('AI Search endpoint for RAG')
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'
