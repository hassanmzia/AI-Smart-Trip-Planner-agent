import { useRequireAuth } from '@/hooks/useAuth';
import { Card } from '@/components/common';

const PaymentPage = () => {
  useRequireAuth();

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Payment
      </h1>

      <Card>
        <p className="text-center text-gray-600 dark:text-gray-400 py-12">
          Stripe payment integration will be implemented here
        </p>
      </Card>
    </div>
  );
};

export default PaymentPage;
