import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Tab } from '@headlessui/react';
import { MagnifyingGlassIcon, CalendarIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import { Card } from '@/components/common';
import { ROUTES } from '@/utils/constants';
import { cn } from '@/utils/helpers';

const SearchPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const initialState = location.state || {};

  const [origin, setOrigin] = useState(initialState.origin || '');
  const [destination, setDestination] = useState(initialState.destination || '');
  const [departureDate, setDepartureDate] = useState(initialState.departureDate || '');
  const [returnDate, setReturnDate] = useState('');
  const [checkInDate, setCheckInDate] = useState('');
  const [checkOutDate, setCheckOutDate] = useState('');
  const [passengers, setPassengers] = useState(initialState.passengers || 1);
  const [guests, setGuests] = useState(1);
  const [rooms, setRooms] = useState(1);
  const [selectedClass, setSelectedClass] = useState('economy');

  const handleFlightSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(ROUTES.FLIGHT_RESULTS, {
      state: {
        origin,
        destination,
        departureDate,
        returnDate,
        passengers,
        class: selectedClass,
      },
    });
  };

  const handleHotelSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(ROUTES.HOTEL_RESULTS, {
      state: {
        destination,
        checkInDate,
        checkOutDate,
        guests,
        rooms,
      },
    });
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Search Flights & Hotels
      </h1>

      <Card>
        <Tab.Group>
          <Tab.List className="flex space-x-4 mb-6">
            <Tab
              className={({ selected }) =>
                cn(
                  'flex-1 py-2 px-4 rounded-lg font-medium transition-colors',
                  selected
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                )
              }
            >
              Flights
            </Tab>
            <Tab
              className={({ selected }) =>
                cn(
                  'flex-1 py-2 px-4 rounded-lg font-medium transition-colors',
                  selected
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                )
              }
            >
              Hotels
            </Tab>
          </Tab.List>

          <Tab.Panels>
            {/* Flight Search */}
            <Tab.Panel>
              <form onSubmit={handleFlightSearch} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="From"
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    placeholder="City or airport"
                    leftIcon={<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <Input
                    label="To"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    placeholder="City or airport"
                    leftIcon={<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <Input
                    label="Departure Date"
                    type="date"
                    value={departureDate}
                    onChange={(e) => setDepartureDate(e.target.value)}
                    leftIcon={<CalendarIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <Input
                    label="Return Date (Optional)"
                    type="date"
                    value={returnDate}
                    onChange={(e) => setReturnDate(e.target.value)}
                    leftIcon={<CalendarIcon className="h-5 w-5 text-gray-400" />}
                  />
                  <Input
                    label="Passengers"
                    type="number"
                    value={passengers}
                    onChange={(e) => setPassengers(parseInt(e.target.value))}
                    min="1"
                    leftIcon={<UserGroupIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Class
                    </label>
                    <select
                      value={selectedClass}
                      onChange={(e) => setSelectedClass(e.target.value)}
                      className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="economy">Economy</option>
                      <option value="premium_economy">Premium Economy</option>
                      <option value="business">Business</option>
                      <option value="first">First Class</option>
                    </select>
                  </div>
                </div>

                <Button type="submit" className="w-full" size="lg">
                  Search Flights
                </Button>
              </form>
            </Tab.Panel>

            {/* Hotel Search */}
            <Tab.Panel>
              <form onSubmit={handleHotelSearch} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Destination"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    placeholder="City or destination"
                    leftIcon={<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <Input
                    label="Check-in Date"
                    type="date"
                    value={checkInDate}
                    onChange={(e) => setCheckInDate(e.target.value)}
                    leftIcon={<CalendarIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <Input
                    label="Check-out Date"
                    type="date"
                    value={checkOutDate}
                    onChange={(e) => setCheckOutDate(e.target.value)}
                    leftIcon={<CalendarIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <Input
                    label="Guests"
                    type="number"
                    value={guests}
                    onChange={(e) => setGuests(parseInt(e.target.value))}
                    min="1"
                    leftIcon={<UserGroupIcon className="h-5 w-5 text-gray-400" />}
                    required
                  />
                  <Input
                    label="Rooms"
                    type="number"
                    value={rooms}
                    onChange={(e) => setRooms(parseInt(e.target.value))}
                    min="1"
                    required
                  />
                </div>

                <Button type="submit" className="w-full" size="lg">
                  Search Hotels
                </Button>
              </form>
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>
      </Card>
    </div>
  );
};

export default SearchPage;
