"""
WebSocket consumers for real-time notifications.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Handles connection, authentication, and message broadcasting.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        """
        # Get user from scope (set by authentication middleware)
        self.user = self.scope.get('user')

        # Reject anonymous users
        if not self.user or isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            logger.warning("WebSocket connection rejected: User not authenticated")
            await self.close(code=4001)
            return

        # Create unique group name for this user
        self.group_name = f'user_{self.user.id}'

        # Add this connection to the user's group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        logger.info(f"WebSocket connected: User {self.user.id}, Channel {self.channel_name}")

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification service',
            'user_id': str(self.user.id)
        }))

        # Send unread notification count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if hasattr(self, 'group_name'):
            # Remove this connection from the user's group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

            logger.info(f"WebSocket disconnected: User {self.user.id if self.user else 'Unknown'}, Code {close_code}")

    async def receive(self, text_data):
        """
        Handle incoming messages from WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            logger.debug(f"WebSocket message received from user {self.user.id}: {message_type}")

            # Route message based on type
            if message_type == 'mark_read':
                await self.handle_mark_read(data)

            elif message_type == 'mark_all_read':
                await self.handle_mark_all_read()

            elif message_type == 'get_notifications':
                await self.handle_get_notifications(data)

            elif message_type == 'ping':
                # Respond to keep-alive ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def notification_message(self, event):
        """
        Handler for notification messages sent to the group.
        This is called when a notification is broadcast to the user's group.
        """
        notification = event.get('notification', {})

        logger.debug(f"Broadcasting notification to user {self.user.id}: {notification.get('id')}")

        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification
        }))

    async def notification_update(self, event):
        """
        Handler for notification update messages (e.g., read status changed).
        """
        await self.send(text_data=json.dumps({
            'type': 'notification_update',
            'notification_id': event.get('notification_id'),
            'updates': event.get('updates', {})
        }))

    async def handle_mark_read(self, data):
        """
        Handle marking a notification as read.
        """
        notification_id = data.get('notification_id')

        if not notification_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'notification_id is required'
            }))
            return

        try:
            success = await self.mark_notification_read(notification_id)

            if success:
                await self.send(text_data=json.dumps({
                    'type': 'marked_read',
                    'notification_id': notification_id
                }))

                # Update unread count
                unread_count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': unread_count
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Failed to mark notification as read'
                }))

        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_mark_all_read(self):
        """
        Handle marking all notifications as read.
        """
        try:
            count = await self.mark_all_notifications_read()

            await self.send(text_data=json.dumps({
                'type': 'marked_all_read',
                'count': count
            }))

            # Update unread count to 0
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': 0
            }))

        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_get_notifications(self, data):
        """
        Handle fetching notifications.
        """
        limit = data.get('limit', 20)
        offset = data.get('offset', 0)
        unread_only = data.get('unread_only', False)

        try:
            notifications = await self.get_notifications(limit, offset, unread_only)

            await self.send(text_data=json.dumps({
                'type': 'notifications',
                'notifications': notifications,
                'limit': limit,
                'offset': offset
            }))

        except Exception as e:
            logger.error(f"Error fetching notifications: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    @database_sync_to_async
    def get_unread_count(self):
        """
        Get count of unread notifications for the user.
        """
        from .models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """
        Mark a notification as read.
        """
        from .models import Notification
        from django.utils import timezone

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {self.user.id}")
            return False

    @database_sync_to_async
    def mark_all_notifications_read(self):
        """
        Mark all notifications as read for the user.
        """
        from .models import Notification
        from django.utils import timezone

        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )

    @database_sync_to_async
    def get_notifications(self, limit, offset, unread_only):
        """
        Fetch notifications for the user.
        """
        from .models import Notification

        queryset = Notification.objects.filter(user=self.user)

        if unread_only:
            queryset = queryset.filter(is_read=False)

        notifications = queryset.order_by('-created_at')[offset:offset + limit]

        return [
            {
                'id': str(n.id),
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'data': n.data,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'read_at': n.read_at.isoformat() if n.read_at else None,
            }
            for n in notifications
        ]


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat with AI agent.
    """

    async def connect(self):
        """
        Handle WebSocket connection for chat.
        """
        self.user = self.scope.get('user')

        if not self.user or isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            logger.warning("Chat WebSocket connection rejected: User not authenticated")
            await self.close(code=4001)
            return

        # Get or create conversation ID from URL parameters
        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')

        if self.conversation_id:
            # Join existing conversation
            self.room_group_name = f'chat_{self.conversation_id}'
        else:
            # Create new conversation
            conversation = await self.create_conversation()
            self.conversation_id = str(conversation.id)
            self.room_group_name = f'chat_{self.conversation_id}'

        # Add to conversation group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        logger.info(f"Chat WebSocket connected: User {self.user.id}, Conversation {self.conversation_id}")

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'conversation_id': self.conversation_id
        }))

    async def disconnect(self, close_code):
        """
        Handle chat WebSocket disconnection.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            logger.info(f"Chat WebSocket disconnected: Conversation {self.conversation_id}, Code {close_code}")

    async def receive(self, text_data):
        """
        Handle incoming chat messages.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                message = data.get('message')

                if not message:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Message content is required'
                    }))
                    return

                # Process message with AI agent
                await self.process_chat_message(message)

            elif message_type == 'typing':
                # Broadcast typing indicator to other participants
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_typing',
                        'user_id': str(self.user.id)
                    }
                )

            else:
                logger.warning(f"Unknown chat message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def process_chat_message(self, message):
        """
        Process chat message with AI agent.
        """
        # Save user message
        user_msg = await self.save_message(message, 'user')

        # Send acknowledgment
        await self.send(text_data=json.dumps({
            'type': 'message_sent',
            'message': {
                'id': str(user_msg.id),
                'content': message,
                'sender': 'user',
                'timestamp': user_msg.created_at.isoformat()
            }
        }))

        # Process with AI agent (async)
        from apps.agents.tasks import run_agent_task_async

        run_agent_task_async.delay(
            task_type='chat',
            user_id=self.user.id,
            params={
                'conversation_id': self.conversation_id,
                'message': message
            }
        )

        # Send typing indicator
        await self.send(text_data=json.dumps({
            'type': 'agent_typing'
        }))

    async def chat_message(self, event):
        """
        Handler for chat messages sent to the group.
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def user_typing(self, event):
        """
        Handler for typing indicator.
        """
        # Don't send typing indicator back to the sender
        if event.get('user_id') != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id']
            }))

    @database_sync_to_async
    def create_conversation(self):
        """
        Create a new conversation.
        """
        from apps.agents.models import AgentConversation

        return AgentConversation.objects.create(
            user=self.user,
            status='active'
        )

    @database_sync_to_async
    def save_message(self, content, sender_type):
        """
        Save a chat message to the database.
        """
        from apps.agents.models import AgentConversation, AgentMessage

        conversation = AgentConversation.objects.get(id=self.conversation_id)

        return AgentMessage.objects.create(
            conversation=conversation,
            content=content,
            sender_type=sender_type,
            user=self.user if sender_type == 'user' else None
        )
