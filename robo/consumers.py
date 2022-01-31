import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AttemptConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'attempt'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        print('receive')
        text_data_json = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'nimadr',
                'data': text_data_json
            }
        )

    # Receive message from room group
    async def attempt_message(self, event):
        print('attempt_message')
        # Send message to WebSocket
        print(json.dumps({'event': event}))
        await self.send(text_data=json.dumps({
            'event': event
        }))
