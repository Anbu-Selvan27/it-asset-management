const API_BASE = 'http://localhost:8000';

export const login = async (username: string, password: string) => {
  const response = await fetch(`${API_BASE}/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
  });
  return await response.json();
};

export const register = async (username: string, password: string, role: string, token: string) => {
    const response = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        username,
        password,
        role,
      }),
    });
    return await response.json();
  };
  
export const getAssets = async (assetTag: string, token: string) => {
  const response = await fetch(`${API_BASE}/assets/${assetTag}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return await response.json();
};

export const reassignAsset = async (assetTag: string, data: ReassignmentData, token: string) => {
  const response = await fetch(`${API_BASE}/assets/${assetTag}/reassign`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  return await response.json();
};

export const syncData = async (token: string) => {
  const response = await fetch(`${API_BASE}/sync/refresh`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return await response.json();
};