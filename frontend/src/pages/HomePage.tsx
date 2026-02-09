import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MagnifyingGlassIcon, CalendarIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import { Card } from '@/components/common';
import { ROUTES } from '@/utils/constants';

const HomePage = () => {
  const navigate = useNavigate();
  const [searchType, setSearchType] = useState<'flight' | 'hotel'>('flight');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [passengers, setPassengers] = useState(1);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(ROUTES.SEARCH, {
      state: {
        searchType,
        origin,
        destination,
        departureDate,
        passengers,
      },
    });
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-primary-600 to-primary-800 dark:from-primary-700 dark:to-primary-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4">
              Your AI-Powered Travel Companion
            </h1>
            <p className="text-xl opacity-90">
              Smart flight and hotel bookings with goal-based optimization
            </p>
          </div>

          {/* Search Form */}
          <Card className="max-w-4xl mx-auto">
            <div className="flex space-x-4 mb-6">
              <button
                onClick={() => setSearchType('flight')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                  searchType === 'flight'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                Flights
              </button>
              <button
                onClick={() => setSearchType('hotel')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                  searchType === 'hotel'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                Hotels
              </button>
            </div>

            <form onSubmit={handleSearch} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {searchType === 'flight' && (
                  <Input
                    label="From"
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    placeholder="City or airport"
                    leftIcon={<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                )}
                <Input
                  label="To"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  placeholder="City or destination"
                  leftIcon={<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />}
                  required
                />
                <Input
                  label={searchType === 'flight' ? 'Departure Date' : 'Check-in Date'}
                  type="date"
                  value={departureDate}
                  onChange={(e) => setDepartureDate(e.target.value)}
                  leftIcon={<CalendarIcon className="h-5 w-5 text-gray-400" />}
                  required
                />
                <Input
                  label={searchType === 'flight' ? 'Passengers' : 'Guests'}
                  type="number"
                  value={passengers}
                  onChange={(e) => setPassengers(parseInt(e.target.value))}
                  min="1"
                  leftIcon={<UserGroupIcon className="h-5 w-5 text-gray-400" />}
                  required
                />
              </div>

              <Button type="submit" className="w-full" size="lg">
                Search {searchType === 'flight' ? 'Flights' : 'Hotels'}
              </Button>
            </form>
          </Card>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
          Why Choose AI Travel Agent?
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="text-center">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <MagnifyingGlassIcon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Smart Search
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              AI-powered search with goal-based optimization finds the best deals for your needs
            </p>
          </Card>

          <Card className="text-center">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <CalendarIcon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Trip Planning
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Organize your entire trip with our intuitive itinerary builder
            </p>
          </Card>

          <Card className="text-center">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <UserGroupIcon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              24/7 Support
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              AI assistant available anytime to help with your travel needs
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
