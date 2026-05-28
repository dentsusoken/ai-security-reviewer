// Cosmos DB Role Assignment Module
// Grants Data Contributor role to a principal (typically Container App managed identity)

@description('Cosmos DB account name')
param cosmosAccountName string

@description('Principal ID to grant access')
param principalId string

// ============================================================================
// Existing Resources
// ============================================================================

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' existing = {
  name: cosmosAccountName
}

// ============================================================================
// Role Definition
// ============================================================================

// Cosmos DB Built-in Data Contributor Role
// ID: 00000000-0000-0000-0000-000000000002
var cosmosDataContributorRoleId = '00000000-0000-0000-0000-000000000002'

// ============================================================================
// Role Assignment
// ============================================================================

resource roleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-05-15' = {
  parent: cosmosAccount
  name: guid(cosmosAccount.id, principalId, cosmosDataContributorRoleId)
  properties: {
    roleDefinitionId: '${cosmosAccount.id}/sqlRoleDefinitions/${cosmosDataContributorRoleId}'
    principalId: principalId
    scope: cosmosAccount.id
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Role assignment ID')
output roleAssignmentId string = roleAssignment.id
