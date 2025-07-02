import { Award, MapPin, TrendingUp, Trophy } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function VolunteerDashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-ocean-500 to-wave-500 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.name}! 👋</h1>
        <p className="text-ocean-100 text-lg">Ready to make a difference today?</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-ocean-100 dark:bg-ocean-900 rounded-lg">
              <Trophy className="h-6 w-6 text-ocean-600 dark:text-ocean-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Current Level</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{user?.level || 'Newcomer'}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
              <Award className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Points</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{user?.points || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <MapPin className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Events Joined</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">0</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <TrendingUp className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Rank</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">#--</p>
            </div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Getting Started</h2>
        <div className="space-y-4">
          <div className="flex items-center p-4 bg-ocean-50 dark:bg-ocean-900 rounded-lg">
            <div className="w-8 h-8 bg-ocean-500 rounded-full flex items-center justify-center text-white font-bold mr-4">
              1
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Complete your profile</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Add your interests and location preferences</p>
            </div>
          </div>
          
          <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold mr-4">
              2
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Find your first event</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Browse upcoming beach cleanups in your area</p>
            </div>
          </div>
          
          <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold mr-4">
              3
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Start making impact</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Join events, earn points, and unlock achievements</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}