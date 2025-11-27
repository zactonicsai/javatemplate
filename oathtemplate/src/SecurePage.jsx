import { useState } from 'react';
import { useAuth } from './AuthContext';
import './SecurePage.css';
import InactivityTimer from './InactivityTimer';
import { callHelloEndpoint, getUserInfo, callAdminEndpoint} from './apiService';


const SecurePage = () => {
  const { userInfo, logout, getUserRoles } = useAuth();
  const roles = getUserRoles();
    const [apiResponse, setApiResponse] = useState(null);
    const [apiLoading, setApiLoading] = useState(false);
    const [apiError, setApiError] = useState(null);

    const handleApiCall = async (apiFunction, buttonName) => {
    setApiLoading(true);
    setApiError(null);
    setApiResponse(null);
    
    try {
      const data = await apiFunction();
      setApiResponse(data);
    } catch (error) {
      setApiError(`${buttonName} failed: ${error.message}`);
    } finally {
      setApiLoading(false);
    }
  };

  return (
    <div className="secure-container">
      <div className="secure-card">
        <h1>Hello, {userInfo?.preferred_username || userInfo?.name || 'User'}! 👋</h1>
        
        <div className="info-section">
          <h2>Your Information</h2>
          <InactivityTimer/>
          {userInfo?.email && (
            <p><strong>Email:</strong> {userInfo.email}</p>
          )}
          {userInfo?.name && (
            <p><strong>Name:</strong> {userInfo.name}</p>
          )}
        </div>

        <div className="roles-section">
          <h2>Your Roles</h2>
          {roles.length > 0 ? (
            <div className="roles-list">
              {roles.map((role, index) => (
                <span key={index} className="role-badge">
                  {role}
                </span>
              ))}
            </div>
          ) : (
            <p>No roles assigned</p>
          )}
        </div>
           <div className="api-section">
          <h2>Test API Calls</h2>
          <p className="api-description">
            Try calling the Spring Boot API endpoints
          </p>
          
          <div className="api-buttons">
            <button 
              className="api-button"
              onClick={() => handleApiCall(callHelloEndpoint, 'Hello Endpoint')}
              disabled={apiLoading}
            >
              Call Hello API
            </button>
            
            <button 
              className="api-button"
              onClick={() => handleApiCall(getUserInfo, 'User Info Endpoint')}
              disabled={apiLoading}
            >
              Get User Info
            </button>
            
            <button 
              className="api-button"
              onClick={() => handleApiCall(callAdminEndpoint, 'Admin Endpoint')}
              disabled={apiLoading}
            >
              Call Admin API
            </button>
          </div>

          {apiLoading && (
            <div className="api-loading">Loading...</div>
          )}

          {apiError && (
            <div className="api-error">
              ❌ {apiError}
            </div>
          )}

          {apiResponse && (
            <div className="api-response">
              <h3>API Response:</h3>
              <pre>{apiResponse}</pre>
            </div>
          )}
        </div>

        <div className="session-info">
          <p className="info-text">
            ⏱️ Your session will expire after 5 minutes of inactivity
          </p>
        </div>

        <button className="logout-button" onClick={logout}>
          Logout
        </button>
      </div>
    </div>
  );
};

export default SecurePage;
