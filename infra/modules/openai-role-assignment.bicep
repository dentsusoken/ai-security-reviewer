// Azure OpenAI Role Assignment Module
// Grants Cognitive Services User role to a principal (for Azure OpenAI access)

@description('Azure OpenAI account name')
param openAiAccountName string

@description('Principal ID to grant access')
param principalId string

// ============================================================================
// Existing Resources
// ============================================================================

resource openAiAccount 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' existing = {
  name: openAiAccountName
}

// ============================================================================
// Role Assignment
// ============================================================================

// Cognitive Services User built-in role
// ID: a97b65f3-24c7-4388-baec-2e87135dc908
var cognitiveServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(openAiAccount.id, principalId, cognitiveServicesUserRoleId)
  scope: openAiAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Role assignment ID')
output roleAssignmentId string = roleAssignment.id
