import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [user, setUser] = useState({
    username: '',
    role: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    const username = localStorage.getItem('username') || '';
    const role = localStorage.getItem('role') || '';
    
    if (!username || !role) {
      navigate('/login');
      return;
    }
    
    setUser({ username, role });
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px',
        borderBottom: '1px solid #eee',
        paddingBottom: '20px'
      }}>
        <h1 style={{ color: '#333' }}>Dashboard</h1>
        <button
          onClick={handleLogout}
          style={{
            padding: '8px 16px',
            backgroundColor: '#d32f2f',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </div>
      
      <div style={{
        backgroundColor: '#ffffff',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)'
      }}>
        <h2 style={{ color: '#555', marginBottom: '15px' }}>Welcome, {user.username}!</h2>
        <p style={{ color: '#666' }}>Role: {user.role}</p>
        
        {user.role === 'admin' && (
          <div style={{ marginTop: '20px' }}>
            <h3 style={{ color: '#555', marginBottom: '10px' }}>Admin Panel</h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '15px'
            }}>
              <div style={{
                padding: '15px',
                backgroundColor: '#e3f2fd',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                Manage Users
              </div>
              <div style={{
                padding: '15px',
                backgroundColor: '#e3f2fd',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                View Assets
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;