import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import AuthForm from '../components/AuthForm';

const Login = () => {
  const [error, setError] = useState<string | undefined>();
  const navigate = useNavigate();

  const handleLogin = async (username: string, password: string) => {
    try {
      const response = await login(username, password);
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('role', response.role);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid username or password');
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      <AuthForm isLogin={true} onSubmit={handleLogin} error={error} />
    </div>
  );
};

export default Login;