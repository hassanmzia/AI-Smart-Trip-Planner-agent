import { useNavigate } from 'react-router-dom';
import { StarIcon, MapPinIcon } from '@heroicons/react/24/solid';
import { Card } from '@/components/common';
import Button from '@/components/common/Button';
import { formatCurrency, formatDistance } from '@/utils/formatters';
import { RECOMMENDATION_COLORS } from '@/utils/constants';
import { cn } from '@/utils/helpers';
import type { Hotel } from '@/types';

interface HotelCardProps {
  hotel: Hotel;
  onSelect?: (hotel: Hotel) => void;
}

const HotelCard = ({ hotel, onSelect }: HotelCardProps) => {
  const navigate = useNavigate();

  const handleBookClick = () => {
    if (onSelect) {
      onSelect(hotel);
    } else {
      navigate(`/booking/hotel/${hotel.id}`);
    }
  };

  const recommendationColor = hotel.utilityScore
    ? RECOMMENDATION_COLORS[hotel.utilityScore.recommendation]
    : null;

  return (
    <Card hover className="p-0 overflow-hidden">
      <div className="flex">
        {/* Image */}
        <div className="w-64 h-48 flex-shrink-0">
          {hotel.images && hotel.images.length > 0 ? (
            <img
              src={hotel.images[0]}
              alt={hotel.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
              <span className="text-gray-400">No image</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 p-6">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              {/* Name and Stars */}
              <h3 className="font-semibold text-xl text-gray-900 dark:text-white mb-2">
                {hotel.name}
              </h3>
              <div className="flex items-center space-x-2 mb-2">
                <div className="flex">
                  {[...Array(hotel.stars)].map((_, i) => (
                    <StarIcon key={i} className="h-4 w-4 text-yellow-400" />
                  ))}
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {hotel.rating.toFixed(1)} rating
                </span>
              </div>

              {/* Location */}
              <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-400 mb-4">
                <MapPinIcon className="h-4 w-4" />
                <span className="text-sm">{hotel.address}, {hotel.city}</span>
                <span className="text-sm">• {formatDistance(hotel.distanceFromCenter)} from center</span>
              </div>

              {/* Amenities */}
              <div className="flex flex-wrap gap-2 mb-4">
                {hotel.amenities.slice(0, 4).map((amenity) => (
                  <span
                    key={amenity}
                    className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                  >
                    {amenity}
                  </span>
                ))}
                {hotel.amenities.length > 4 && (
                  <span className="px-2 py-1 text-xs text-gray-500 dark:text-gray-400">
                    +{hotel.amenities.length - 4} more
                  </span>
                )}
              </div>

              {/* Utility Score */}
              {hotel.utilityScore && recommendationColor && (
                <div className={cn('p-2 rounded-lg inline-block', recommendationColor.bg, recommendationColor.border, 'border')}>
                  <span className={cn('text-xs font-medium', recommendationColor.text)}>
                    {hotel.utilityScore.recommendation.toUpperCase()} • Score: {hotel.utilityScore.totalScore.toFixed(2)}
                  </span>
                </div>
              )}
            </div>

            {/* Price and Book */}
            <div className="ml-6 text-right">
              <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                {formatCurrency(hotel.pricePerNight, hotel.currency)}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">per night</p>
              <Button onClick={handleBookClick}>Book Now</Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default HotelCard;
