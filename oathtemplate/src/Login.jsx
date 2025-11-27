import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './Login.css';

const Login = () => {
  const { authenticated, login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (authenticated) {
      navigate('/secure');
    }
  }, [authenticated, navigate]);

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Welcome</h1>
        <p>Please login to access the secure page</p>
        <button className="login-button" onClick={login}>
          Login with Keycloak
        </button>
      </div>
    </div>
  );
};

export default Login;
