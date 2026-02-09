import { useNavigate } from 'react-router-dom';
import { ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { Card } from '@/components/common';
import Button from '@/components/common/Button';
import { formatCurrency, formatDuration, formatDate } from '@/utils/formatters';
import { RECOMMENDATION_COLORS } from '@/utils/constants';
import { cn } from '@/utils/helpers';
import type { Flight } from '@/types';

interface FlightCardProps {
  flight: Flight;
  onSelect?: (flight: Flight) => void;
}

const FlightCard = ({ flight, onSelect }: FlightCardProps) => {
  const navigate = useNavigate();

  const handleBookClick = () => {
    if (onSelect) {
      onSelect(flight);
    } else {
      navigate(`/booking/flight/${flight.id}`);
    }
  };

  const recommendationColor = flight.goalEvaluation
    ? RECOMMENDATION_COLORS[flight.goalEvaluation.recommendation]
    : null;

  return (
    <Card hover className="p-6">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          {/* Airline and Flight Number */}
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
              {flight.airline}
            </h3>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {flight.flightNumber}
            </span>
          </div>

          {/* Route and Times */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatDate(flight.departureTime, 'HH:mm')}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{flight.origin.code}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">{flight.origin.city}</p>
            </div>

            <div className="flex flex-col items-center justify-center">
              <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                <ClockIcon className="h-4 w-4" />
                <span className="text-sm">{formatDuration(flight.duration)}</span>
              </div>
              <div className="w-full h-px bg-gray-300 dark:bg-gray-600 my-2" />
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {flight.stops === 0 ? 'Direct' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
              </p>
            </div>

            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatDate(flight.arrivalTime, 'HH:mm')}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{flight.destination.code}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">{flight.destination.city}</p>
            </div>
          </div>

          {/* Goal Evaluation */}
          {flight.goalEvaluation && recommendationColor && (
            <div className={cn('p-3 rounded-lg mb-4', recommendationColor.bg, recommendationColor.border, 'border')}>
              <div className="flex items-center justify-between">
                <span className={cn('text-sm font-medium', recommendationColor.text)}>
                  {flight.goalEvaluation.recommendation.toUpperCase()} MATCH
                </span>
                <span className={cn('text-sm', recommendationColor.text)}>
                  Utility Score: {flight.goalEvaluation.totalUtility.toFixed(2)}
                </span>
              </div>
              {!flight.goalEvaluation.budgetConstraintMet && (
                <p className="text-xs mt-1 text-red-600 dark:text-red-400">
                  Over budget by {formatCurrency(Math.abs(flight.goalEvaluation.budgetDifference))}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Price and Book */}
        <div className="ml-6 text-right">
          <p className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {formatCurrency(flight.price, flight.currency)}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{flight.class}</p>
          <Button onClick={handleBookClick}>Book Now</Button>
        </div>
      </div>
    </Card>
  );
};

export default FlightCard;
