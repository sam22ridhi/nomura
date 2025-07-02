import { LogOut, Waves } from 'lucide-react';
import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Layout() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-ocean-50 to-wave-50 dark:from-gray-900 dark:to-gray-800">
      {/* Simple Header */}
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-ocean-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center space-x-2">
              <Waves className="h-8 w-8 text-ocean-500" />
              <span className="text-xl font-bold bg-gradient-to-r from-ocean-600 to-wave-600 bg-clip-text text-transparent">
                WaveAI
              </span>
            </Link>

            <div className="flex items-center space-x-4">
              {user ? (
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {user.name} ({user.role})
                  </span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center px-3 py-1 text-sm text-red-600 hover:text-red-800 transition-colors"
                  >
                    <LogOut className="h-4 w-4 mr-1" />
                    Logout
                  </button>
                </div>
              ) : (
                <Link
                  to="/auth"
                  className="bg-gradient-to-r from-ocean-500 to-wave-500 hover:from-ocean-600 hover:to-wave-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}