import { useRequireAdmin } from '@/hooks/useAuth';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common';

const AdminDashboardPage = () => {
  useRequireAdmin();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Admin Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-primary-600 dark:text-primary-400">
              0
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-primary-600 dark:text-primary-400">
              0
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-primary-600 dark:text-primary-400">
              $0
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
