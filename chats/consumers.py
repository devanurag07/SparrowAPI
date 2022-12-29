from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from sparrow.utils import get_model
from accounts.models import User
from .models import WSClient
from channels.db import database_sync_to_async
from .models import Conversation,Message,Status
from django.db.models import Q
from chats.serializers import MessageSerializer


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
        
        message=self.save_msg({
            "to_user":to_user,
            "message":to_user_msg
        })

        message_data=MessageSerializer(message,many=False).data
        self.send(message_data)

        channels=WSClient.objects.filter(user=to_user)
        if(channels.exists()):
            reciever_channel_name=channels.first().channel_id
            self.channel_layer.send(reciever_channel_name,message_data)

        else:
            pass
    @database_sync_to_async
    def save_msg(self,data):
        reciever=data["to_user"]
        user=self.scope["user"]
        message=data["message"]
        Message.objects.filter()

        conv=Conversation.objects.filter(Q(user1=user,user2=reciever)| Q(user1=reciever,user2=user))
        if(conv.exists()):
            conv=conv.first()
        else:
            conv=Conversation.objects.create(user1=user,user2=reciever)
        
        message=Message(conversation=conv,sender=user,reciever=reciever,message=message)
        message.save()
        return message

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
