// Key Vault Module for AI Security Reviewer
// Stores secrets for Azure OpenAI, GitHub PAT, etc.

@description('Key Vault name')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Entra ID tenant ID')
param entraIdTenantId string = ''

// ============================================================================
// Key Vault
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: !empty(entraIdTenantId) ? entraIdTenantId : subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    // Note: enablePurgeProtection is intentionally omitted to allow updates to existing vaults
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Key Vault name')
output name string = keyVault.name

@description('Key Vault URI')
output uri string = keyVault.properties.vaultUri

@description('Key Vault resource ID')
output resourceId string = keyVault.id
