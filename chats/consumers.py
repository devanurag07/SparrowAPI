from channels.generic.websocket import AsyncJsonWebsocketConsumer,WebsocketConsumer
import json
from sparrow.utils import get_model
from accounts.models import User
from .models import WSClient
from channels.db import database_sync_to_async
from .models import Message,Status
from django.db.models import Q
from chats.serializers import MessageSerializer
from asgiref.sync import sync_to_async

class ChatChannel(AsyncJsonWebsocketConsumer):
    async def connect(self):

        self.user = self.scope["user"]
        # Adding User to Channel
        await self.clean_user()
        await self.add_user()
        await self.accept()

    async def disconnect(self, code):
        await self.remove_user()
        await self.disconnect(code=code)

    async def receive(self, text_data='', bytes_data=None, **kwargs):
        data=json.loads(text_data)
        receiver_mobile=data["receiver_mobile"]
        receiver_channel_name=await self.get_channel(receiver_mobile)

        if(receiver_channel_name):
            await self.channel_layer.send(receiver_channel_name,
                {
                    "type":"chat.receive",
                    "payload":text_data
                }
            )
        else:
            pass


    
    async def chat_receive(self,text_data):
        data=text_data['payload']
        await self.send(data)

    @database_sync_to_async
    def get_channel(self,mobile):
        channels=WSClient.objects.filter(user__mobile=int(mobile))
        if(channels.exists()):
            channel_name=channels.first().channel_name
            return channel_name
        else:
            return None
        

    @database_sync_to_async
    def get_user_channel(self, to_user_id):
        to_user = get_model(User, id=int(to_user_id))
        if(not to_user["exist"]):
            return False, "The User Does Not Exist"

        to_user = to_user['data']
        active_to_user = WSClient.objects.filter(user__id=int(to_user_id))
        return active_to_user.channel_name, active_to_user.user

    @database_sync_to_async
    def add_user(self):
        self.clean_user()
        WSClient.objects.create(
            user=self.user, channel_name=self.channel_name)

    @database_sync_to_async
    def remove_user(self):
        self.clean_user()

    @database_sync_to_async
    def clean_user(self):
        print("cleaned")
        print(WSClient.objects.filter(user=self.user).delete())



class TestChannel(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))

    
