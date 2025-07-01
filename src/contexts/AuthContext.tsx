import React, { createContext, useContext, useEffect, useState } from 'react';

export type UserRole = 'volunteer' | 'organizer';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  points?: number;
  level?: string;
  badges?: number;
  organizationName?: string;
  eventsOrganized?: number;
  totalVolunteers?: number;
  joinedAt: string;
  isVerified?: boolean;
  authProvider?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  loginWithGoogle: () => void;
  signup: (userData: Omit<User, 'id' | 'joinedAt'> & { password?: string }) => Promise<boolean>;
  logout: () => Promise<void>;
  isLoading: boolean;
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = 'http://localhost:8000/api';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Handle OAuth callback
  useEffect(() => {
    const handleOAuthCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      
      if (token && window.location.pathname === '/auth/callback') {
        localStorage.setItem('waveai_token', token);
        await getCurrentUser();
        // Redirect to appropriate dashboard
        if (user?.role === 'volunteer') {
          window.location.href = '/volunteer';
        } else {
          window.location.href = '/organizer';
        }
      }
    };

    handleOAuthCallback();
  }, [user]);

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('waveai_token');
    if (token) {
      await getCurrentUser();
    }
    setIsLoading(false);
  };

  const getCurrentUser = async () => {
    try {
      const token = localStorage.getItem('waveai_token');
      if (!token) return;

      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        localStorage.removeItem('waveai_token');
      }
    } catch (error) {
      console.error('Error getting current user:', error);
      localStorage.removeItem('waveai_token');
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('waveai_token', data.access_token);
        setUser(data.user);
        setIsLoading(false);
        return true;
      } else {
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setIsLoading(false);
      return false;
    }
  };

  const loginWithGoogle = () => {
    // Redirect to Google OAuth
    window.location.href = `${API_URL}/auth/google`;
  };

  const signup = async (userData: Omit<User, 'id' | 'joinedAt'> & { password?: string }): Promise<boolean> => {
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: userData.name,
          email: userData.email,
          role: userData.role,
          organizationName: userData.organizationName,
          password: userData.password || 'temp-password', // For hackathon simplicity
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('waveai_token', data.access_token);
        setUser(data.user);
        setIsLoading(false);
        return true;
      } else {
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Signup error:', error);
      setIsLoading(false);
      return false;
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('waveai_token');
      if (token) {
        // Call logout endpoint to invalidate session
        await fetch(`${API_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('waveai_token');
    }
  };

  const updateUser = (updates: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...updates };
      setUser(updatedUser);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      loginWithGoogle, 
      signup, 
      logout, 
      isLoading, 
      updateUser 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}