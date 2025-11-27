import Keycloak from 'keycloak-js';

// Keycloak configuration
// Replace these values with your Keycloak server details
const keycloak = new Keycloak({
  url: 'http://localhost:9191',  // Your Keycloak server URL
  realm: 'demo-realm',            // Your Keycloak realm name
  clientId: 'demo-client',     // Your Keycloak client ID
});

export default keycloak;
