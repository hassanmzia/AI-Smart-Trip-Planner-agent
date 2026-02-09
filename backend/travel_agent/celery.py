"""
Celery configuration for AI Travel Agent project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_agent.settings')

app = Celery('travel_agent')

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    # Check for price drops every hour
    'check-price-alerts': {
        'task': 'apps.flights.tasks.check_price_alerts',
        'schedule': crontab(minute=0),  # Every hour
    },
    # Update flight status every 30 minutes
    'update-flight-status': {
        'task': 'apps.flights.tasks.update_flight_status',
        'schedule': crontab(minute='*/30'),
    },
    # Send booking reminders 24 hours before departure
    'send-booking-reminders': {
        'task': 'apps.bookings.tasks.send_booking_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    # Clean up expired sessions
    'cleanup-expired-sessions': {
        'task': 'apps.users.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    # Update weather data
    'update-weather-data': {
        'task': 'apps.itineraries.tasks.update_weather_data',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
