import { Award, MapPin, Trophy, Users } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function OrganizerDashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome, {user?.name}!</h1>
        <p className="text-green-100 text-lg">
          {user?.organizationName ? `${user.organizationName} • ` : ''}Ready to organize impactful events
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
              <MapPin className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Events Created</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{user?.eventsOrganized || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Volunteers</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">{user?.totalVolunteers || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <Award className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Impact Score</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">--</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <Trophy className="h-6 w-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Rating</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {user?.isVerified ? '✅ Verified' : 'Pending'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Organizer Quick Start</h2>
        <div className="space-y-4">
          <div className="flex items-center p-4 bg-green-50 dark:bg-green-900 rounded-lg">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold mr-4">
              1
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Set up your organization profile</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Add details about your organization and mission</p>
            </div>
          </div>
          
          <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold mr-4">
              2
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Create your first event</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Plan and organize a beach cleanup event</p>
            </div>
          </div>
          
          <div className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold mr-4">
              3
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Engage volunteers</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Build your community and track impact</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}