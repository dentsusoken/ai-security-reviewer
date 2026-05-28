// Container App Module for AI Security Reviewer Backend

@description('Container App name')
param name string

@description('Azure region')
param location string

@description('Resource tags')
param tags object = {}

@description('Container Apps Environment ID')
param containerAppsEnvId string

@description('Container Registry name')
param containerRegistryName string

@description('Container Registry login server')
param containerRegistryLoginServer string

@description('Container image name')
param imageName string

@description('Container image tag')
param imageTag string = 'latest'

@description('Container target port')
param targetPort int = 8000

@description('Environment variables')
param envVars array = []

// Note: Key Vault access is granted via separate role assignment module

@description('CPU cores')
param cpu string = '0.5'

@description('Memory in Gi')
param memory string = '1.0Gi'

@description('Minimum replicas')
param minReplicas int = 1

@description('Maximum replicas')
param maxReplicas int = 3

// ============================================================================
// Container Registry Reference
// ============================================================================

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

// ============================================================================
// Container App
// ============================================================================

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnvId
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: false
          maxAge: 3600
        }
      }
      registries: [
        {
          server: containerRegistryLoginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: '${containerRegistryLoginServer}/${imageName}:${imageTag}'
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: envVars
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-rule'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Container App name')
output name string = containerApp.name

@description('Container App FQDN')
output fqdn string = containerApp.properties.configuration.ingress.fqdn

@description('Container App identity principal ID')
output identityPrincipalId string = containerApp.identity.principalId

@description('Container App resource ID')
output resourceId string = containerApp.id
