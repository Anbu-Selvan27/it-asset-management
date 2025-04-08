import { useState } from 'react';
import { syncData } from '../api';

interface SyncButtonProps {
  token: string;
}

const SyncButton = ({ token }: SyncButtonProps) => {
  const [isSyncing, setIsSyncing] = useState(false);
  const [message, setMessage] = useState('');

  const handleSync = async () => {
    setIsSyncing(true);
    setMessage('');
    try {
      const result = await syncData(token);
      setMessage(result.message || 'Sync completed successfully');
    } catch (err) {
      setMessage('Sync failed');
    } finally {
      setIsSyncing(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <button
        onClick={handleSync}
        disabled={isSyncing}
        style={{
          padding: '8px 15px',
          backgroundColor: '#2196F3',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          opacity: isSyncing ? 0.7 : 1
        }}
      >
        {isSyncing ? 'Syncing...' : 'Sync Data'}
      </button>
      {message && <span style={{ color: message.includes('failed') ? 'red' : 'green' }}>{message}</span>}
    </div>
  );
};

export default SyncButton;