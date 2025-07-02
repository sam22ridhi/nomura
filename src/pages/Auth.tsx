import { AlertCircle, Building, CheckCircle, Eye, EyeOff, Loader, Lock, Mail, Shield, Sparkles, User, Waves } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import type { UserRole } from '../contexts/AuthContext';
import { useAuth } from '../contexts/AuthContext';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('volunteer');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [callbackStatus, setCallbackStatus] = useState<'loading' | 'success' | 'error' | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    organizationName: '',
  });

  const { login, signup, loginWithGoogle, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || (selectedRole === 'volunteer' ? '/volunteer' : '/organizer');

  // Handle OAuth callback
  useEffect(() => {
    const handleOAuthCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      const error = urlParams.get('error');
      const errorMessage = urlParams.get('message');

      if (window.location.pathname === '/auth/callback' || token || error) {
        setCallbackStatus('loading');
        
        if (error) {
          setCallbackStatus('error');
          setError(errorMessage || 'Authentication failed');
          setTimeout(() => {
            setCallbackStatus(null);
            navigate('/auth', { replace: true });
          }, 3000);
          return;
        }

        if (token) {
          localStorage.setItem('waveai_token', token);
          setCallbackStatus('success');
          
          // Wait for user data to be loaded, then redirect
          setTimeout(() => {
            setCallbackStatus(null);
            if (user?.role === 'volunteer') {
              navigate('/volunteer', { replace: true });
            } else if (user?.role === 'organizer') {
              navigate('/organizer', { replace: true });
            } else {
              navigate('/', { replace: true });
            }
          }, 2000);
        }
      }
    };

    handleOAuthCallback();
  }, [navigate, user]);

  // Show callback status screen
  if (callbackStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-ocean-50 to-wave-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 text-center max-w-md w-full">
          <div className="mb-6">
            {callbackStatus === 'loading' && (
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <Loader className="h-8 w-8 text-blue-600 dark:text-blue-400 animate-spin" />
              </div>
            )}
            
            {callbackStatus === 'success' && (
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
            )}
            
            {callbackStatus === 'error' && (
              <div className="w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="h-8 w-8 text-red-600 dark:text-red-400" />
              </div>
            )}
          </div>

          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            {callbackStatus === 'loading' && 'Authenticating...'}
            {callbackStatus === 'success' && 'Welcome to WaveAI!'}
            {callbackStatus === 'error' && 'Authentication Failed'}
          </h2>

          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {callbackStatus === 'loading' && 'Please wait while we verify your credentials'}
            {callbackStatus === 'success' && 'Redirecting to your dashboard...'}
            {callbackStatus === 'error' && error}
          </p>

          {callbackStatus === 'error' && (
            <button
              onClick={() => navigate('/auth')}
              className="bg-ocean-500 hover:bg-ocean-600 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (isLogin) {
        const success = await login(formData.email, formData.password);
        if (success) {
          navigate(from, { replace: true });
        } else {
          setError('Invalid email or password');
        }
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setIsLoading(false);
          return;
        }

        const success = await signup({
          name: formData.name,
          email: formData.email,
          role: selectedRole,
          organizationName: selectedRole === 'organizer' ? formData.organizationName : undefined,
          avatar: selectedRole === 'volunteer' ? '👤' : '🏢',
          password: formData.password,
        });

        if (success) {
          navigate(selectedRole === 'volunteer' ? '/volunteer' : '/organizer', { replace: true });
        } else {
          setError('User already exists with this email');
        }
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    setIsLoading(true);
    loginWithGoogle();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-ocean-50 via-wave-50 to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%2314b8a6%22%20fill-opacity%3D%220.03%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%224%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
      
      <div className="relative w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-3">
            <div className="relative">
              <Waves className="h-12 w-12 text-ocean-500 animate-wave" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-wave-400 to-ocean-400 rounded-full animate-pulse"></div>
            </div>
            <span className="text-3xl font-bold bg-gradient-to-r from-ocean-600 to-wave-600 bg-clip-text text-transparent">
              WaveAI
            </span>
          </Link>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {isLogin ? 'Welcome back!' : 'Join the movement'}
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/20 p-8">
          {/* Toggle */}
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-xl p-1 mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                isLogin
                  ? 'bg-white dark:bg-gray-600 text-ocean-600 dark:text-ocean-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                !isLogin
                  ? 'bg-white dark:bg-gray-600 text-ocean-600 dark:text-ocean-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Google OAuth Button */}
          <button
            onClick={handleGoogleLogin}
            disabled={isLoading}
            className="w-full mb-6 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl py-3 px-4 flex items-center justify-center space-x-3 hover:bg-gray-50 dark:hover:bg-gray-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mr-2"></div>
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            )}
            <span className="text-gray-700 dark:text-gray-300 font-medium">
              {isLoading ? 'Connecting...' : 'Continue with Google'}
            </span>
          </button>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">Or continue with email</span>
            </div>
          </div>

          {/* Role Selection (Sign Up Only) */}
          {!isLogin && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                I want to join as:
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedRole('volunteer')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedRole === 'volunteer'
                      ? 'border-ocean-500 bg-ocean-50 dark:bg-ocean-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                  }`}
                >
                  <Sparkles className={`h-6 w-6 mx-auto mb-2 ${
                    selectedRole === 'volunteer' ? 'text-ocean-500' : 'text-gray-400'
                  }`} />
                  <div className="text-sm font-medium text-gray-900 dark:text-white">Volunteer</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Join cleanups</div>
                </button>
                
                <button
                  type="button"
                  onClick={() => setSelectedRole('organizer')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedRole === 'organizer'
                      ? 'border-ocean-500 bg-ocean-50 dark:bg-ocean-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                  }`}
                >
                  <Shield className={`h-6 w-6 mx-auto mb-2 ${
                    selectedRole === 'organizer' ? 'text-ocean-500' : 'text-gray-400'
                  }`} />
                  <div className="text-sm font-medium text-gray-900 dark:text-white">Organizer</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Create events</div>
                </button>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-ocean-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                    placeholder="Enter your full name"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-ocean-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            {!isLogin && selectedRole === 'organizer' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Organization Name
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    name="organizationName"
                    required
                    value={formData.organizationName}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-ocean-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                    placeholder="Enter organization name"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-12 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-ocean-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    required
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-ocean-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                    placeholder="Confirm your password"
                  />
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-ocean-500 to-wave-500 hover:from-ocean-600 hover:to-wave-600 disabled:from-gray-400 disabled:to-gray-500 text-white py-3 rounded-xl font-semibold transition-all transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  {isLogin ? 'Signing In...' : 'Creating Account...'}
                </div>
              ) : (
                isLogin ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          {/* Demo Credentials */}
          {isLogin && (
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
              <p className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Test your backend:</p>
              <div className="text-xs text-blue-600 dark:text-blue-300 space-y-1">
                <div>✅ Create any account to test signup flow</div>
                <div>✅ Use Google OAuth for seamless login</div>
                <div>✅ Backend running on localhost:8000</div>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="mt-6 text-center">
            <Link
              to="/"
              className="text-sm text-ocean-600 dark:text-ocean-400 hover:text-ocean-700 dark:hover:text-ocean-300 transition-colors"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}