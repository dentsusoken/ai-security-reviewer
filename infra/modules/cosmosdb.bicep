// Cosmos DB Module for AI Security Reviewer
// Creates NoSQL database with containers for reviews, findings, and agent runs

@description('Cosmos DB account name')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Database name')
param databaseName string = 'ai-security-reviewer'

@description('Enable free tier (only one per subscription)')
param enableFreeTier bool = false

// ============================================================================
// Cosmos DB Account
// ============================================================================

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    enableFreeTier: enableFreeTier
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    // Disable key-based access - use Managed Identity only
    disableLocalAuth: false // Set to true after RBAC is configured
  }
}

// ============================================================================
// Database
// ============================================================================

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmosAccount
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

// ============================================================================
// Containers
// ============================================================================

// Review Sessions Container
resource reviewSessionsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'reviewSessions'
  properties: {
    resource: {
      id: 'reviewSessions'
      partitionKey: {
        paths: ['/userId']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          { path: '/status/?'}
          { path: '/inputType/?'}
          { path: '/startedAt/?'}
          { path: '/*'}
        ]
        excludedPaths: [
          { path: '/"_etag"/?'}
        ]
        compositeIndexes: [
          [
            { path: '/userId', order: 'ascending' }
            { path: '/startedAt', order: 'descending' }
          ]
        ]
      }
      defaultTtl: -1 // No expiration
    }
  }
}

// Findings Container
resource findingsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'findings'
  properties: {
    resource: {
      id: 'findings'
      partitionKey: {
        paths: ['/reviewSessionId']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          { path: '/severity/?'}
          { path: '/resolutionState/?'}
          { path: '/*'}
        ]
        excludedPaths: [
          { path: '/"_etag"/?'}
          { path: '/codeSnippet/?'} // Don't index large text
          { path: '/fixedCode/?'}
        ]
      }
    }
  }
}

// Agent Runs Container
resource agentRunsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'agentRuns'
  properties: {
    resource: {
      id: 'agentRuns'
      partitionKey: {
        paths: ['/reviewSessionId']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          { path: '/state/?'}
          { path: '/agentName/?'}
          { path: '/*'}
        ]
        excludedPaths: [
          { path: '/"_etag"/?'}
        ]
      }
      defaultTtl: 2592000 // 30 days
    }
  }
}

// Ownership Verifications Container (for DAST)
resource ownershipContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'ownershipVerifications'
  properties: {
    resource: {
      id: 'ownershipVerifications'
      partitionKey: {
        paths: ['/targetHost']
        kind: 'Hash'
      }
      defaultTtl: 604800 // 7 days
    }
  }
}

// Export Jobs Container
resource exportJobsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'exportJobs'
  properties: {
    resource: {
      id: 'exportJobs'
      partitionKey: {
        paths: ['/reviewSessionId']
        kind: 'Hash'
      }
      defaultTtl: 2592000 // 30 days
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Cosmos DB account name')
output name string = cosmosAccount.name

@description('Cosmos DB endpoint')
output endpoint string = cosmosAccount.properties.documentEndpoint

@description('Database name')
output databaseName string = database.name

@description('Cosmos DB resource ID')
output resourceId string = cosmosAccount.id
