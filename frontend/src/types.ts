export interface User {
    username: string;
    role: string;
  }
  
  export interface AuthResponse {
    access_token: string;
    token_type: string;
    role: string;
  }