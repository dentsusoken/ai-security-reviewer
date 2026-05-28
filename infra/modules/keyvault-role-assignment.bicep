// Key Vault Role Assignment Module
// Grants Secrets User role to a principal (typically Container App managed identity)

@description('Key Vault name')
param keyVaultName string

@description('Principal ID to grant access')
param principalId string

// ============================================================================
// Existing Resources
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// ============================================================================
// Role Assignment
// ============================================================================

// Key Vault Secrets User built-in role
// ID: 4633458b-17de-408a-b874-0445c86b69e6
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, principalId, keyVaultSecretsUserRoleId)
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Role assignment ID')
output roleAssignmentId string = roleAssignment.id
