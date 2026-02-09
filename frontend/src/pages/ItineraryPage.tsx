import { useRequireAuth } from '@/hooks/useAuth';
import { Card } from '@/components/common';

const ItineraryPage = () => {
  useRequireAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        My Itineraries
      </h1>

      <Card>
        <p className="text-center text-gray-600 dark:text-gray-400 py-12">
          Your trip itineraries will appear here
        </p>
      </Card>
    </div>
  );
};

export default ItineraryPage;
