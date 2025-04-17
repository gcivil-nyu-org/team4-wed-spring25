
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.recipient_username = self.scope["url_route"]["kwargs"]["username"]
        self.recipient = await self.get_user(self.recipient_username)
        self.sender = self.scope["user"]
        self.room_group_name = self.get_room_name(self.sender, self.recipient)

        print(
            f">>> CONNECTED to WebSocket: {self.sender} with path: {self.scope['path']}"
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logger.debug(f"[disconnect] Closing from: {self.scope['user']}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.debug(f"[receive] Message received: {text_data}")
        try:
            data = json.loads(text_data)
            message = data["message"]
            sender = self.scope["user"]

            await self.save_message(sender, self.recipient, message)
            logger.debug(f"[receive] Message saved: '{message}'")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender.username,
                },
            )

        except Exception as e:
            logger.error(f"[receive] Error processing message: {e}")

    async def chat_message(self, event):
        logger.debug(f"[chat_message] Broadcasting message: {event}")
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                }
            )
        )

    def get_room_name(self, user1, user2):
        usernames = sorted([user1.username, user2.username])
        room = "_".join(usernames)
        logger.debug(f"[get_room_name] Room name resolved: {room}")
        return room

    @database_sync_to_async
    def get_user(self, username):
        logger.debug(f"[get_user] Fetching user: {username}")
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, sender, recipient, message):
        logger.debug(f"[save_message] Saving message from {sender} to {recipient}")
        return Message.objects.create(
            sender=sender, recipient=recipient, content=message
        )
