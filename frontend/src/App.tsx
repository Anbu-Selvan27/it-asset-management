import { useState } from 'react';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';

const App = () => {
  const [token, setToken] = useState('');
  const [role, setRole] = useState('');

  const handleLogin = (newToken: string, newRole: string) => {
    setToken(newToken);
    setRole(newRole);
  };

  const handleLogout = () => {
    setToken('');
    setRole('');
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {!token ? (
        <Login onLogin={handleLogin} />
      ) : role === 'admin' ? (
        <AdminDashboard token={token} onLogout={handleLogout} />
      ) : (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <h2>Welcome User</h2>
          <button
            onClick={handleLogout}
            style={{
              padding: '10px 20px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '20px'
            }}
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
};

export default App;