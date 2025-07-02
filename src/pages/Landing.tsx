import { ArrowRight, Shield, Sparkles, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Landing() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-24">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            <span className="block">WaveAI</span>
            <span className="block bg-gradient-to-r from-ocean-600 to-wave-600 bg-clip-text text-transparent">
              Empowering Communities
            </span>
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-4xl mx-auto">
            AI-driven innovation for a cleaner, greener tomorrow. Join thousands of volunteers making a real difference in beach conservation.
          </p>
          
          {user ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Link
                to={user.role === 'volunteer' ? '/volunteer' : '/organizer'}
                className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-ocean-500 to-wave-500 text-white font-semibold rounded-full hover:from-ocean-600 hover:to-wave-600 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Go to Dashboard
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </div>
          ) : (
            <>
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                <Link
                  to="/auth"
                  className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-ocean-500 to-wave-500 text-white font-semibold rounded-full hover:from-ocean-600 hover:to-wave-600 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  Get Started
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </div>

              {/* Role Selection Preview */}
              <div className="max-w-2xl mx-auto mb-16">
                <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">Choose your path to environmental impact:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 border border-white/20 dark:border-gray-700/20 hover:scale-105 transition-all duration-200">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Sparkles className="h-8 w-8 text-white" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Join as Volunteer</h3>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">
                        Participate in cleanups, earn points, unlock achievements, and make a direct impact
                      </p>
                    </div>
                  </div>
                  
                  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 border border-white/20 dark:border-gray-700/20 hover:scale-105 transition-all duration-200">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Shield className="h-8 w-8 text-white" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Become Organizer</h3>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">
                        Create events, manage volunteers, track impact, and lead community initiatives
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Stats Counter */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-ocean-600 dark:text-ocean-400 mb-2">247+</div>
              <div className="text-gray-600 dark:text-gray-300">Beaches Cleaned</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-wave-600 dark:text-wave-400 mb-2">12.8K kg</div>
              <div className="text-gray-600 dark:text-gray-300">Waste Collected</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-green-600 dark:text-green-400 mb-2">5.6K+</div>
              <div className="text-gray-600 dark:text-gray-300">Active Volunteers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-purple-600 dark:text-purple-400 mb-2">1.8K kg</div>
              <div className="text-gray-600 dark:text-gray-300">CO₂ Saved</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-ocean-500 to-wave-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-8">
            Ready to Make Waves?
          </h2>
          <p className="text-xl text-ocean-100 mb-12 max-w-3xl mx-auto">
            Join our community of environmental champions and start making a difference today.
          </p>
          {!user && (
            <Link
              to="/auth"
              className="inline-flex items-center px-8 py-4 bg-white text-ocean-600 font-semibold rounded-full hover:bg-gray-100 transform hover:scale-105 transition-all duration-200 shadow-lg"
            >
              <Users className="mr-2 h-5 w-5" />
              Join the Movement
            </Link>
          )}
        </div>
      </section>
    </div>
  );
}