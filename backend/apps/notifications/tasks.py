"""
Celery tasks for notification operations.
"""
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification(self, user_id, notification_type, title, message, data=None, channels=None):
    """
    Send a notification to a user through specified channels.

    Args:
        user_id: ID of the user to notify
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        data: Optional additional data (dict)
        channels: List of channels to use ['database', 'email', 'push', 'websocket']
                 Defaults to all enabled channels
    """
    try:
        from .models import Notification
        from apps.users.models import User

        logger.info(f"Sending notification to user {user_id}: {notification_type}")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {'status': 'error', 'message': 'User not found'}

        # Default to all channels if not specified
        if channels is None:
            channels = ['database', 'email', 'push', 'websocket']

        results = {}

        # Database notification (always create)
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )
        results['database'] = 'success'
        logger.debug(f"Database notification created: {notification.id}")

        # Email notification
        if 'email' in channels and user.email and user.email_notifications_enabled:
            try:
                context = {
                    'user': user,
                    'title': title,
                    'message': message,
                    'notification': notification,
                    'site_name': settings.SITE_NAME,
                    'site_url': settings.SITE_URL,
                }

                html_message = render_to_string('emails/notification.html', context)

                send_mail(
                    subject=title,
                    message=message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
                results['email'] = 'success'
                logger.debug(f"Email notification sent to {user.email}")

            except Exception as e:
                logger.error(f"Error sending email notification: {str(e)}")
                results['email'] = f'error: {str(e)}'

        # Push notification
        if 'push' in channels and user.push_notifications_enabled:
            try:
                # Send push notification via FCM or similar service
                from .utils import send_push_notification

                push_result = send_push_notification(
                    user=user,
                    title=title,
                    body=message,
                    data=data
                )
                results['push'] = 'success' if push_result else 'failed'
                logger.debug(f"Push notification sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending push notification: {str(e)}")
                results['push'] = f'error: {str(e)}'

        # WebSocket notification (real-time)
        if 'websocket' in channels:
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync

                channel_layer = get_channel_layer()
                group_name = f'user_{user_id}'

                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'notification_message',
                        'notification': {
                            'id': str(notification.id),
                            'type': notification_type,
                            'title': title,
                            'message': message,
                            'data': data or {},
                            'created_at': notification.created_at.isoformat(),
                        }
                    }
                )
                results['websocket'] = 'success'
                logger.debug(f"WebSocket notification sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {str(e)}")
                results['websocket'] = f'error: {str(e)}'

        logger.info(f"Notification sent to user {user_id}. Results: {results}")

        return {
            'status': 'success',
            'notification_id': str(notification.id),
            'channels': results
        }

    except Exception as exc:
        logger.error(f"Error in send_notification task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def send_bulk_notifications(self, user_ids, notification_type, title, message, data=None, channels=None):
    """
    Send notifications to multiple users.

    Args:
        user_ids: List of user IDs to notify
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        data: Optional additional data (dict)
        channels: List of channels to use
    """
    try:
        from .models import Notification
        from apps.users.models import User

        logger.info(f"Sending bulk notifications to {len(user_ids)} users")

        # Verify users exist
        users = User.objects.filter(id__in=user_ids, is_active=True)

        if not users.exists():
            logger.warning("No active users found for bulk notification")
            return {
                'status': 'warning',
                'message': 'No active users found'
            }

        sent_count = 0
        failed_count = 0
        results = []

        # Send to each user
        for user in users:
            try:
                result = send_notification.delay(
                    user_id=user.id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    data=data,
                    channels=channels
                )
                sent_count += 1
                results.append({
                    'user_id': user.id,
                    'status': 'queued',
                    'task_id': result.id
                })

            except Exception as e:
                logger.error(f"Error queuing notification for user {user.id}: {str(e)}")
                failed_count += 1
                results.append({
                    'user_id': user.id,
                    'status': 'failed',
                    'error': str(e)
                })

        logger.info(f"Bulk notification completed. Sent: {sent_count}, Failed: {failed_count}")

        return {
            'status': 'success',
            'total_users': len(user_ids),
            'sent': sent_count,
            'failed': failed_count,
            'results': results
        }

    except Exception as exc:
        logger.error(f"Error in send_bulk_notifications task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def cleanup_old_notifications(self, days=30):
    """
    Clean up old read notifications.

    Args:
        days: Delete read notifications older than this many days
    """
    try:
        from .models import Notification
        from datetime import timedelta

        logger.info(f"Cleaning up notifications older than {days} days")

        cutoff_date = timezone.now() - timedelta(days=days)

        # Delete old read notifications
        deleted_count, _ = Notification.objects.filter(
            is_read=True,
            created_at__lt=cutoff_date
        ).delete()

        logger.info(f"Deleted {deleted_count} old notifications")

        return {
            'status': 'success',
            'deleted_count': deleted_count
        }

    except Exception as exc:
        logger.error(f"Error in cleanup_old_notifications task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def send_daily_digest(self, user_id):
    """
    Send daily digest email with unread notifications.

    Args:
        user_id: ID of the user
    """
    try:
        from .models import Notification
        from apps.users.models import User
        from datetime import timedelta

        logger.info(f"Sending daily digest to user {user_id}")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {'status': 'error', 'message': 'User not found'}

        # Check if user has enabled digest emails
        if not user.digest_emails_enabled:
            logger.info(f"User {user_id} has digest emails disabled")
            return {'status': 'skipped', 'message': 'Digest emails disabled'}

        # Get unread notifications from last 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            created_at__gte=yesterday
        ).order_by('-created_at')

        if not notifications.exists():
            logger.info(f"No unread notifications for user {user_id}")
            return {'status': 'skipped', 'message': 'No unread notifications'}

        # Group notifications by type
        grouped_notifications = {}
        for notification in notifications:
            if notification.notification_type not in grouped_notifications:
                grouped_notifications[notification.notification_type] = []
            grouped_notifications[notification.notification_type].append(notification)

        # Prepare email
        context = {
            'user': user,
            'notifications': notifications,
            'grouped_notifications': grouped_notifications,
            'total_count': notifications.count(),
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }

        html_message = render_to_string('emails/daily_digest.html', context)

        send_mail(
            subject=f'Your Daily Digest - {notifications.count()} new notifications',
            message=f'You have {notifications.count()} unread notifications.',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

        logger.info(f"Daily digest sent to user {user_id}")

        return {
            'status': 'success',
            'user_id': user_id,
            'notification_count': notifications.count()
        }

    except Exception as exc:
        logger.error(f"Error in send_daily_digest task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def mark_notifications_as_read(self, user_id, notification_ids=None):
    """
    Mark notifications as read for a user.

    Args:
        user_id: ID of the user
        notification_ids: Optional list of specific notification IDs. If None, marks all as read.
    """
    try:
        from .models import Notification

        logger.info(f"Marking notifications as read for user {user_id}")

        queryset = Notification.objects.filter(user_id=user_id, is_read=False)

        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)

        updated_count = queryset.update(
            is_read=True,
            read_at=timezone.now()
        )

        logger.info(f"Marked {updated_count} notifications as read for user {user_id}")

        return {
            'status': 'success',
            'updated_count': updated_count
        }

    except Exception as exc:
        logger.error(f"Error in mark_notifications_as_read task: {str(exc)}")
        raise self.retry(exc=exc)
