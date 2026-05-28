/**
 * MSAL configuration for Azure Entra ID authentication.
 */
import { Configuration, LogLevel, BrowserCacheLocation } from '@azure/msal-browser';

// Environment variables for MSAL configuration
const clientId = import.meta.env.VITE_AZURE_CLIENT_ID || '';
const tenantId = import.meta.env.VITE_AZURE_TENANT_ID || '';
const redirectUri = import.meta.env.VITE_AZURE_REDIRECT_URI || window.location.origin;

/**
 * MSAL configuration object.
 */
export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri,
    postLogoutRedirectUri: window.location.origin,
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: BrowserCacheLocation.SessionStorage,
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) {
          return;
        }
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            return;
          case LogLevel.Warning:
            console.warn(message);
            return;
          case LogLevel.Info:
            if (import.meta.env.DEV) {
              console.info(message);
            }
            return;
          case LogLevel.Verbose:
            if (import.meta.env.DEV) {
              console.debug(message);
            }
            return;
          default:
            return;
        }
      },
      logLevel: import.meta.env.DEV ? LogLevel.Info : LogLevel.Warning,
    },
  },
};

/**
 * Scopes for acquiring access token.
 */
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
};

/**
 * Scopes for API access.
 */
export const apiRequest = {
  scopes: [`api://${clientId}/access_as_user`],
};

/**
 * Check if MSAL is properly configured.
 */
export function isMsalConfigured(): boolean {
  return Boolean(clientId && tenantId);
}
