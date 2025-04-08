import { useState } from 'react';
import Register from './Register';
import AssetSearch from './AssetSearch';
import SyncButton from './SyncButton';

interface AdminDashboardProps {
  token: string;
  onLogout: () => void;
}

const AdminDashboard = ({ token, onLogout }: AdminDashboardProps) => {
  const [activeTab, setActiveTab] = useState('assets');

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ color: '#333' }}>Admin Dashboard</h1>
        <div>
          <SyncButton token={token} />
          <button
            onClick={onLogout}
            style={{
              marginLeft: '10px',
              padding: '8px 15px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab('assets')}
          style={{
            padding: '10px 15px',
            backgroundColor: activeTab === 'assets' ? '#4CAF50' : '#ddd',
            color: activeTab === 'assets' ? 'white' : '#333',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Asset Management
        </button>
        <button
          onClick={() => setActiveTab('users')}
          style={{
            padding: '10px 15px',
            backgroundColor: activeTab === 'users' ? '#4CAF50' : '#ddd',
            color: activeTab === 'users' ? 'white' : '#333',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          User Management
        </button>
      </div>

      {activeTab === 'assets' && <AssetSearch token={token} />}
      {activeTab === 'users' && <Register token={token} onRegister={() => {}} />}
    </div>
  );
};

export default AdminDashboard;