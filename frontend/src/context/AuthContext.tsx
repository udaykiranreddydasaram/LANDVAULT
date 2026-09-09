import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (u: string, p: string) => Promise<void>;
  logout: () => void;
  switchDemoRole: (role: UserRole) => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('landvault_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadUser() {
      if (token) {
        try {
          const u = await api.getCurrentUser();
          setUser(u);
        } catch (e) {
          console.warn('Session expired, falling back to demo default');
          loginAsVerifier();
        }
      } else {
        // Auto login as Verifier for instant hackathon demonstration!
        loginAsVerifier();
      }
      setIsLoading(false);
    }
    loadUser();
  }, [token]);

  async function loginAsVerifier() {
    try {
      const res = await api.login('verifier', 'verifierpassword123');
      localStorage.setItem('landvault_token', res.access_token);
      setToken(res.access_token);
      setUser(res.user);
    } catch (err) {
      // If db not seeded yet, seed and retry
      try {
        await api.seedUsers();
        const res = await api.login('verifier', 'verifierpassword123');
        localStorage.setItem('landvault_token', res.access_token);
        setToken(res.access_token);
        setUser(res.user);
      } catch (e) {
        console.error('Failed auto-login', e);
      }
    }
  }

  const login = async (username: string, pass: string) => {
    const res = await api.login(username, pass);
    localStorage.setItem('landvault_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem('landvault_token');
    setToken(null);
    setUser(null);
  };

  const switchDemoRole = async (targetRole: UserRole) => {
    const pass = `${targetRole}password123`;
    try {
      await login(targetRole, pass);
    } catch (err) {
      console.error('Role switch failed', err);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, switchDemoRole, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
