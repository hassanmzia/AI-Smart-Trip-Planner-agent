import { useQuery } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { searchHotels } from '@/services/hotelService';
import HotelCard from '@/components/hotel/HotelCard';
import Loading from '@/components/common/Loading';
import { QUERY_KEYS } from '@/utils/constants';
import type { HotelSearchParams } from '@/types';

const HotelResultsPage = () => {
  const location = useLocation();
  const searchParams = location.state as HotelSearchParams;

  const { data, isLoading, error } = useQuery({
    queryKey: [...QUERY_KEYS.HOTELS, searchParams],
    queryFn: () => searchHotels(searchParams),
    enabled: !!searchParams,
  });

  if (!searchParams) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-center text-gray-600 dark:text-gray-400">
          No search parameters found. Please start a new search.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Loading size="lg" text="Searching for hotels..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-center text-red-600 dark:text-red-400">
          Error loading hotels. Please try again.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Hotel Results
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {searchParams.destination} • {data?.total || 0} hotels found
        </p>
      </div>

      {/* Hotels List */}
      <div className="space-y-4">
        {data?.items && data.items.length > 0 ? (
          data.items.map((hotel) => <HotelCard key={hotel.id} hotel={hotel} />)
        ) : (
          <p className="text-center text-gray-600 dark:text-gray-400 py-12">
            No hotels found for your search criteria.
          </p>
        )}
      </div>
    </div>
  );
};

export default HotelResultsPage;
