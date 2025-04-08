import { useState } from 'react';
import { getAssets } from '../api';
import AssetReassign from './AssetReassign';
import { Asset } from '../types';

interface AssetSearchProps {
  token: string;
}

const AssetSearch = ({ token }: AssetSearchProps) => {
  const [assetTag, setAssetTag] = useState('');
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    try {
      const data = await getAssets(assetTag, token);
      setAssets(data);
      setError('');
    } catch (err) {
      setError('Failed to fetch assets');
      setAssets([]);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input
          type="text"
          value={assetTag}
          onChange={(e) => setAssetTag(e.target.value)}
          placeholder="Enter asset tag"
          style={{
            flex: '1',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ddd'
          }}
        />
        <button
          onClick={handleSearch}
          style={{
            padding: '8px 15px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Search
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {assets.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h3>Search Results</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f2f2f2' }}>
                  <th style={{ padding: '10px', border: '1px solid #ddd' }}>Asset Tag</th>
                  <th style={{ padding: '10px', border: '1px solid #ddd' }}>User</th>
                  <th style={{ padding: '10px', border: '1px solid #ddd' }}>Department</th>
                  <th style={{ padding: '10px', border: '1px solid #ddd' }}>Location</th>
                  <th style={{ padding: '10px', border: '1px solid #ddd' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset) => (
                  <tr key={asset.asset_tag} style={{ borderBottom: '1px solid #ddd' }}>
                    <td style={{ padding: '10px' }}>{asset.asset_tag}</td>
                    <td style={{ padding: '10px' }}>{asset.user_name || 'N/A'}</td>
                    <td style={{ padding: '10px' }}>{asset.department || 'N/A'}</td>
                    <td style={{ padding: '10px' }}>{asset.location || 'N/A'}</td>
                    <td style={{ padding: '10px' }}>
                      <button
                        onClick={() => setSelectedAsset(asset)}
                        style={{
                          padding: '5px 10px',
                          backgroundColor: '#FF9800',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        Reassign
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {selectedAsset && (
        <AssetReassign
          asset={selectedAsset}
          token={token}
          onClose={() => setSelectedAsset(null)}
          onReassigned={() => handleSearch()}
        />
      )}
    </div>
  );
};

export default AssetSearch;