import keycloak from './keycloak';

const API_BASE_URL = 'http://localhost:8080/api';

/**
 * Generic API call function with automatic token handling
 */
const callApi = async (endpoint, options = {}) => {
  // Ensure token is fresh
  try {
    await keycloak.updateToken(30); // Refresh if expires in 30 seconds
  } catch (error) {
    console.error('Failed to refresh token:', error);
    keycloak.login();
    return;
  }

  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${keycloak.token}`
    }
  };

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);
    
    if (response.status === 401) {
      // Token expired or invalid, redirect to login
      keycloak.login();
      return;
    }

    if (response.status === 403) {
      throw new Error('Access forbidden - insufficient permissions');
    }

    if (!response.ok) {
      throw new Error(`API call failed with status ${response.status}`);
    }

    const data = await response.text();
    console.log(data)
    return data;
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

/**
 * Call the basic hello endpoint
 */
export const callHelloEndpoint = async () => {
  return callApi('/hello');
};

/**
 * Get detailed user information from API
 */
export const getUserInfo = async () => {
  return callApi('/hello/user');
};

/**
 * Call admin-only endpoint
 */
export const callAdminEndpoint = async () => {
  return callApi('/hello/admin');
};

/**
 * Call user-only endpoint
 */
export const callUserOnlyEndpoint = async () => {
  return callApi('/hello/user-only');
};

/**
 * Health check (no authentication required)
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/actuator/health`);
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default {
  callHelloEndpoint,
  getUserInfo,
  callAdminEndpoint,
  callUserOnlyEndpoint,
  healthCheck
};
