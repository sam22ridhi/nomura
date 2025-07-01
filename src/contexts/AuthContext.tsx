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
  joinedAt: Date;
  isVerified?: boolean;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (userData: Omit<User, 'id' | 'joinedAt'> & { password: string }) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock users for demonstration
const mockUsers: (User & { password: string })[] = [
  {
    id: '1',
    name: 'Ritika Iyer',
    email: 'ritika@example.com',
    password: 'password123',
    role: 'volunteer',
    avatar: '👩‍🚀',
    points: 1247,
    level: 'Eco Warrior',
    badges: 4,
    joinedAt: new Date('2023-06-15'),
  },
  {
    id: '2',
    name: 'Samridhi Raj Sinha',
    email: 'sam@example.com',
    password: 'password123',
    role: 'organizer',
    avatar: '👨‍🌾',
    organizationName: 'Marine Conservation Society',
    eventsOrganized: 15,
    totalVolunteers: 247,
    joinedAt: new Date('2023-03-10'),
    isVerified: true,
  },
];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored user session
    const storedUser = localStorage.getItem('waveai_user');
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('waveai_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const foundUser = mockUsers.find(u => u.email === email && u.password === password);
    
    if (foundUser) {
      const { password: _, ...userWithoutPassword } = foundUser;
      setUser(userWithoutPassword);
      localStorage.setItem('waveai_user', JSON.stringify(userWithoutPassword));
      setIsLoading(false);
      return true;
    }
    
    setIsLoading(false);
    return false;
  };

  const signup = async (userData: Omit<User, 'id' | 'joinedAt'> & { password: string }): Promise<boolean> => {
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Check if user already exists
    const existingUser = mockUsers.find(u => u.email === userData.email);
    if (existingUser) {
      setIsLoading(false);
      return false;
    }
    
    const newUser: User = {
      id: Date.now().toString(),
      name: userData.name,
      email: userData.email,
      role: userData.role,
      avatar: userData.avatar,
      points: userData.role === 'volunteer' ? 0 : undefined,
      level: userData.role === 'volunteer' ? 'Newcomer' : undefined,
      badges: userData.role === 'volunteer' ? 0 : undefined,
      organizationName: userData.organizationName,
      eventsOrganized: userData.role === 'organizer' ? 0 : undefined,
      totalVolunteers: userData.role === 'organizer' ? 0 : undefined,
      joinedAt: new Date(),
      isVerified: false,
    };
    
    // Add to mock users (in real app, this would be an API call)
    mockUsers.push({ ...newUser, password: userData.password });
    
    setUser(newUser);
    localStorage.setItem('waveai_user', JSON.stringify(newUser));
    setIsLoading(false);
    return true;
  };

  const updateUser = (updates: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...updates };
      setUser(updatedUser);
      localStorage.setItem('waveai_user', JSON.stringify(updatedUser));
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('waveai_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, isLoading, updateUser }}>
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