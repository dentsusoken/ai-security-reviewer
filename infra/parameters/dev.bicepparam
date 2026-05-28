using 'main.bicep'

// Development environment parameters
param environment = 'dev'
param location = 'japaneast'
param baseName = 'aisecreviewer'

// Authentication (fill in after Entra ID app registration)
param entraIdTenantId = ''
param entraIdClientId = ''

// Azure OpenAI (fill in after resource creation)
param azureOpenAiEndpoint = ''
param azureOpenAiDeployment = 'gpt-4o'

// Container image
param backendImageTag = 'latest'
