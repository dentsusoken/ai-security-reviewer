// Azure OpenAI Module for AI Security Reviewer
// Creates Azure OpenAI resource with GPT-4o deployment

@description('Azure OpenAI resource name')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('OpenAI model deployment name')
param deploymentName string = 'gpt-4o'

@description('OpenAI model name')
param modelName string = 'gpt-4o'

@description('Model version')
param modelVersion string = '2024-05-13'

@description('Deployment capacity (tokens per minute in thousands)')
param capacityTokensPerMinute int = 30

// ============================================================================
// Azure OpenAI Account
// ============================================================================

resource openAI 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: name
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// ============================================================================
// GPT-4o Deployment
// ============================================================================

resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openAI
  name: deploymentName
  sku: {
    name: 'Standard'
    capacity: capacityTokensPerMinute
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    raiPolicyName: 'Microsoft.Default'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Azure OpenAI resource name')
output name string = openAI.name

@description('Azure OpenAI endpoint')
output endpoint string = openAI.properties.endpoint

@description('Azure OpenAI deployment name')
output deploymentName string = gpt4oDeployment.name

@description('Azure OpenAI resource ID')
output resourceId string = openAI.id
