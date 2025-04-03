import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Register } from '../api/auth';
import AuthForm from '../components/AuthForm';

const Register = () => {
  const [error, setError] = useState<string | undefined>();
  const navigate = useNavigate();

  const handleRegister = async (username: string, password: string) => {
    try {
      await register(username, password);
      navigate('/login');
    } catch (err) {
      setError('Registration failed. Username may already exist.');
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
      <AuthForm isLogin={false} onSubmit={handleRegister} error={error} />
    </div>
  );
};

export default Register;