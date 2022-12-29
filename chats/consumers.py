from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from sparrow.utils import get_model
from accounts.models import User
from .models import WSClient
from channels.db import database_sync_to_async


class ChatChannel(AsyncJsonWebsocketConsumer):
    async def connect(self):

        self.user = self.scope["user"]
        # Adding User to Channel
        await self.add_user()
        await self.accept()

        self.close()

    async def disconnect(self, code):
        await self.remove_user()
        await self.disconnect(code=code)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        data=json.loads(text_data)
        to_user_mobile=data["receiver_mobile"]
        to_user_msg=data["message"]        
        to_user = get_model(User, mobile=int(to_user_mobile))
        if(not to_user["exist"]):
            return False, "The User Does Not Exist"
        
        to_user=to_user["data"]
        channels=WSClient.objects.filter(user=to_user)
        if(channels.exists()):
            to_user_channel=channels.first().channel_id
            self.channel_layer.send(to_user_channel,
                                    {"msg":to_user_msg})

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
