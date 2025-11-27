import { createContext, useContext, useEffect, useState, useRef } from 'react';
import keycloak from './keycloak';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);
  const timeoutRef = useRef(null);

  // 5 minutes in milliseconds
  const INACTIVITY_TIMEOUT = 5 * 60 * 1000;

  const resetInactivityTimer = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (authenticated) {
      timeoutRef.current = setTimeout(() => {
        logout();
        alert('Session expired due to inactivity');
      }, INACTIVITY_TIMEOUT);
    }
  };

  const initHasRun = useRef(false);

  useEffect(() => {

    if (initHasRun.current) {
            return; // Initialization has already run, exit the effect
        }
        
        // Set the flag *before* starting the async operation
        initHasRun.current = true;

    const initKeycloak = async () => {
      try {
        const auth = await keycloak.init({
          onLoad: 'check-sso',
          checkLoginIframe: false,
          pkceMethod: 'S256'
        });

        setAuthenticated(auth);

        if (auth) {
          const userInfo = await keycloak.loadUserInfo();
          setUserInfo(userInfo);
          resetInactivityTimer();
        }
      } catch (error) {
        console.error('Keycloak initialization error:', error);
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initKeycloak();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!authenticated) return;

    // Track user activity
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    
    events.forEach(event => {
      document.addEventListener(event, resetInactivityTimer);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, resetInactivityTimer);
      });
    };
  }, [authenticated]);

  const login = () => {
    keycloak.login();
  };

  const logout = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    keycloak.logout();
  };

  const getUserRoles = () => {
    if (!keycloak.tokenParsed) return [];
    
    // Get realm roles
    const realmRoles = keycloak.tokenParsed.realm_access?.roles || [];
    
    // Get client roles
    const clientRoles = keycloak.tokenParsed.resource_access?.[keycloak.clientId]?.roles || [];
    
    return [...realmRoles, ...clientRoles];
  };

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        loading,
        userInfo,
        login,
        logout,
        getUserRoles,
        keycloak
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
