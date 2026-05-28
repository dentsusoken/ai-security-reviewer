// Static Web App Module for AI Security Reviewer Frontend

@description('Static Web App name')
param name string

@description('Azure region (limited for SWA)')
@allowed(['eastasia', 'westus2', 'centralus', 'westeurope'])
param location string = 'eastasia'

@description('Resource tags')
param tags object = {}

@description('Backend API URL for linking')
param backendUrl string = ''

// ============================================================================
// Static Web App
// ============================================================================

resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    provider: 'Custom'
    buildProperties: {
      skipGithubActionWorkflowGeneration: true
    }
  }
}

// App Settings for Backend URL
resource staticWebAppSettings 'Microsoft.Web/staticSites/config@2023-12-01' = {
  parent: staticWebApp
  name: 'appsettings'
  properties: {
    VITE_API_BASE_URL: !empty(backendUrl) ? 'https://${backendUrl}' : ''
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Static Web App name')
output name string = staticWebApp.name

@description('Static Web App default hostname')
output defaultHostname string = staticWebApp.properties.defaultHostname

// Note: Deployment token should be retrieved separately via CLI for security
