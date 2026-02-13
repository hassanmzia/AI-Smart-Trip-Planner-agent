import { useState } from 'react';
import { Button } from '@/components/common';
import api from '@/services/api';
import { API_ENDPOINTS } from '@/utils/constants';
import toast from 'react-hot-toast';

interface TripFeedbackModalProps {
  itineraryId: number;
  destination: string;
  onClose: () => void;
  onSubmitted: () => void;
}

const RATING_LABELS = ['', 'Poor', 'Fair', 'Good', 'Great', 'Excellent'];

const TAG_OPTIONS = [
  'great_location', 'loved_culture', 'amazing_food', 'beautiful_nature',
  'friendly_locals', 'good_value', 'too_expensive', 'poor_transport',
  'loved_nightlife', 'great_adventure', 'relaxing', 'crowded',
  'clean_accommodation', 'historical', 'romantic', 'family_friendly',
];

const StarRating = ({
  value,
  onChange,
  label,
}: {
  value: number;
  onChange: (v: number) => void;
  label: string;
}) => (
  <div className="flex items-center justify-between">
    <span className="text-sm text-gray-700 dark:text-gray-300 w-36">{label}</span>
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          className={`text-2xl transition-colors ${
            star <= value
              ? 'text-yellow-400'
              : 'text-gray-300 dark:text-gray-600 hover:text-yellow-200'
          }`}
        >
          {star <= value ? '\u2605' : '\u2606'}
        </button>
      ))}
    </div>
    <span className="text-xs text-gray-500 w-16 text-right">
      {value > 0 ? RATING_LABELS[value] : ''}
    </span>
  </div>
);

export const TripFeedbackModal = ({
  itineraryId,
  destination,
  onClose,
  onSubmitted,
}: TripFeedbackModalProps) => {
  const [submitting, setSubmitting] = useState(false);
  const [overallRating, setOverallRating] = useState(0);
  const [flightRating, setFlightRating] = useState(0);
  const [hotelRating, setHotelRating] = useState(0);
  const [activitiesRating, setActivitiesRating] = useState(0);
  const [foodRating, setFoodRating] = useState(0);
  const [valueRating, setValueRating] = useState(0);
  const [lovedMost, setLovedMost] = useState('');
  const [wouldChange, setWouldChange] = useState('');
  const [additionalComments, setAdditionalComments] = useState('');
  const [wouldVisitAgain, setWouldVisitAgain] = useState<boolean | null>(null);
  const [wouldRecommend, setWouldRecommend] = useState<boolean | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleSubmit = async () => {
    if (overallRating === 0) {
      toast.error('Please provide an overall rating');
      return;
    }
    setSubmitting(true);
    try {
      await api.post(`${API_ENDPOINTS.ITINERARY.LIST}/${itineraryId}/feedback/`, {
        overall_rating: overallRating,
        flight_rating: flightRating || undefined,
        hotel_rating: hotelRating || undefined,
        activities_rating: activitiesRating || undefined,
        food_rating: foodRating || undefined,
        value_for_money_rating: valueRating || undefined,
        loved_most: lovedMost,
        would_change: wouldChange,
        additional_comments: additionalComments,
        would_visit_again: wouldVisitAgain,
        would_recommend: wouldRecommend,
        tags: selectedTags,
      });
      toast.success('Thank you for your feedback!');
      onSubmitted();
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              How was your trip to {destination}?
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl"
            >
              &times;
            </button>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            Your feedback helps our AI plan better trips for you in the future.
          </p>

          {/* Overall Rating */}
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Overall Experience *</p>
            <StarRating value={overallRating} onChange={setOverallRating} label="" />
          </div>

          {/* Category Ratings */}
          <div className="mb-6 space-y-3">
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Rate by category (optional)</p>
            <StarRating value={flightRating} onChange={setFlightRating} label="Flights" />
            <StarRating value={hotelRating} onChange={setHotelRating} label="Accommodation" />
            <StarRating value={activitiesRating} onChange={setActivitiesRating} label="Activities" />
            <StarRating value={foodRating} onChange={setFoodRating} label="Food & Dining" />
            <StarRating value={valueRating} onChange={setValueRating} label="Value for Money" />
          </div>

          {/* Text Feedback */}
          <div className="mb-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                What did you love most?
              </label>
              <textarea
                value={lovedMost}
                onChange={(e) => setLovedMost(e.target.value)}
                rows={2}
                placeholder="The food was incredible, the hotel had a perfect location..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                What would you change?
              </label>
              <textarea
                value={wouldChange}
                onChange={(e) => setWouldChange(e.target.value)}
                rows={2}
                placeholder="The flight layover was too long, wish we had more beach time..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Any other comments?
              </label>
              <textarea
                value={additionalComments}
                onChange={(e) => setAdditionalComments(e.target.value)}
                rows={2}
                placeholder="Overall thoughts, suggestions for improvement..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Tags */}
          <div className="mb-6">
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Quick tags (select all that apply)
            </p>
            <div className="flex flex-wrap gap-2">
              {TAG_OPTIONS.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    selectedTags.includes(tag)
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {tag.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Boolean Questions */}
          <div className="mb-6 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">Would you visit again?</span>
              <div className="flex gap-2">
                {[true, false].map((val) => (
                  <button
                    key={String(val)}
                    type="button"
                    onClick={() => setWouldVisitAgain(val)}
                    className={`px-4 py-1 rounded-full text-xs font-medium transition-colors ${
                      wouldVisitAgain === val
                        ? val ? 'bg-green-600 text-white' : 'bg-red-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {val ? 'Yes' : 'No'}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">Would you recommend to a friend?</span>
              <div className="flex gap-2">
                {[true, false].map((val) => (
                  <button
                    key={String(val)}
                    type="button"
                    onClick={() => setWouldRecommend(val)}
                    className={`px-4 py-1 rounded-full text-xs font-medium transition-colors ${
                      wouldRecommend === val
                        ? val ? 'bg-green-600 text-white' : 'bg-red-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {val ? 'Yes' : 'No'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <Button variant="secondary" onClick={onClose}>
              Skip for now
            </Button>
            <Button onClick={handleSubmit} isLoading={submitting} disabled={submitting || overallRating === 0}>
              Submit Feedback
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripFeedbackModal;
