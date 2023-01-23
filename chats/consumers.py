from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
import json
from sparrow.utils import get_model
from accounts.models import User
from .models import WSClient,SignallingWSClient
from channels.db import database_sync_to_async
from .models import Message, Status
from django.db.models import Q
from chats.serializers import MessageSerializer
from asgiref.sync import sync_to_async
from .websocket_constants import SDP_RECEIVE, CHAT_RECEIVE
from .middleware import get_user,get_user_sync


from channels.middleware import BaseMiddleware
from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken
from django.conf import settings
from asgiref.sync import async_to_sync
class ChatChannel(AsyncJsonWebsocketConsumer):

    async def connect(self):

        scope=self.scope
        headers = {key.decode("ascii"): value.decode("ascii")
                   for key, value in scope['headers']}
        token = headers.get("token", "adioda")

        try:
            UntypedToken(token)
        except Exception as e:
            raise InvalidToken("Invalid Token")

        decoded = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        scope["user"] = await get_user(validated_token=decoded)

        self.user = scope["user"]
        # Adding User to Channel
        await self.clean_user()
        await self.add_user()
        await self.accept()

    async def disconnect(self, code):
        print("Disconnecting")
        await self.clean_user()

    async def receive(self, text_data='', bytes_data=None, **kwargs):
        data = json.loads(text_data)
        receiver_mobile = data["receiver_mobile"]
        event_type = data["event_type"]
        receiver_channel_name = await self.get_channel(receiver_mobile)

        if (receiver_channel_name):
            print(receiver_channel_name)
            await self.channel_layer.send(receiver_channel_name, {
                "type": event_type,
                "payload": text_data
            })

            if (event_type == SDP_RECEIVE):
                await self.send(json.dumps({"status": "online"}))
        else:
            print("Hey")
            if (event_type == SDP_RECEIVE):
                await self.send(json.dumps({"status": "offline"}))

    async def chat_receive(self, text_data):
        data = text_data['payload']
        data = json.loads(data)
        data["event_type"] = CHAT_RECEIVE
        await self.send(json.dumps(data))

    async def sdp_receive(self, text_data):
        data = text_data["payload"]
        data = json.loads(data)
        data["event_type"] = SDP_RECEIVE
        await self.send(json.dumps(data))

    @database_sync_to_async
    def get_channel(self, mobile):
        channels = WSClient.objects.filter(user__mobile=int(mobile))
        if (channels.exists()):
            channel_name = channels.last().channel_name
            return channel_name
        else:
            return None

    @database_sync_to_async
    def get_user_channel(self, to_user_id):
        to_user = get_model(User, id=int(to_user_id))
        if (not to_user["exist"]):
            return False, "The User Does Not Exist"

        to_user = to_user['data']
        active_to_user = WSClient.objects.filter(user__id=int(to_user_id))
        return active_to_user.channel_name, active_to_user.user

    @database_sync_to_async
    def add_user(self):
        self.clean_user()
        WSClient.objects.create(user=self.user, channel_name=self.channel_name)

    @database_sync_to_async
    def clean_user(self):
        print("Cleaned")
        WSClient.objects.filter(user=self.user).delete()




# Signalling Constants

OFFER="rtc.offer"
ANSWER="rtc.answer"
CANDIDATE="rtc.candidate"

class Signalling(WebsocketConsumer):
    def connect(self):
    
        scope=self.scope
        headers = {key.decode("ascii"): value.decode("ascii")
                   for key, value in scope['headers']}
        token = headers.get("token", "adioda")

        try:
            UntypedToken(token)
        except Exception as e:
            raise InvalidToken("Invalid Token")

        decoded = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        scope["user"] = get_user_sync(validated_token=decoded)

        self.user = scope["user"]

        self.clean_user()
        self.add_user()
        self.accept()

        self.send(json.dumps({
            "type":"info",
            "msg":"Signalling COnnected"

        }))        
    def disconnect(self, code):
        print("Disconnecting")
        self.clean_user()


    async def authenticate(self,data):

        scope=self.scope
        token = data['token']

        try:
            UntypedToken(token)
        except Exception as e:
            raise InvalidToken("Invalid Token")

        decoded = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = get_user(validated_token=decoded)
        self.user=user

        print("HEy there")
        self.clean_user()
        self.add_user()
        print("Authenticated")



    def receive(self, text_data='', bytes_data=None, **kwargs):
        import pdb
        data = json.loads(text_data)
        event_type = data["type"]
        print("Sending ")
        print("Event Type :"+str(event_type))   
        

        if(event_type=="authenticate"):
            # await self.send(json.dumps(data))
            self.channel_layer.send(self.channel_name,data)
            return

        data['mobile']=self.user.mobile;
        receiver_mobile = data["receiver"]
        receiver_channel_name = self.get_channel(receiver_mobile)

        if (receiver_channel_name):
            print(f"Sending To {receiver_mobile}")
            print(f"CHANNEL_NAME : {receiver_channel_name}")

            async_to_sync(self.channel_layer.send)(receiver_channel_name,data)

            if (event_type == OFFER):
                self.send(json.dumps({"status": "online","type":"status"}))
            return
        else:
            if (event_type == OFFER):
                self.send(json.dumps({"status": "offline","type":"status"}))




    def rtc_offer(self, text_data):
        print("Offer Getting")
        mobile=text_data['receiver']
        print(f"Calling - {mobile}")
        self.send(json.dumps(text_data))

    def rtc_answer(self, text_data):
        self.send(json.dumps(text_data))

    def rtc_candidate(self, text_data):
        self.send(json.dumps(text_data))

    def rtc_hangup(self, text_data):
        self.send(json.dumps(text_data))

    def rtc_reject(self, text_data):
        self.send(json.dumps(text_data))
    
    def get_channel(self, mobile):
        try:    
            channels = SignallingWSClient.objects.filter(user__mobile=int(mobile))
            print(f"{channels.count()} Channels with mobile no {mobile}")

        except Exception as e:
            import pdb
            pdb.set_trace()
            
        if (channels.exists()):
            channel_name = channels.first().channel_name
            return channel_name
        else:
            return None

    
    def add_user(self):
        print("Createad Channel "+str(self.channel_name))
        SignallingWSClient.objects.create(user=self.user, channel_name=self.channel_name)
        print("User Added with mobile -- ",str(self.user.mobile))


        

    def clean_user(self):
        print(SignallingWSClient.objects.filter(user=self.user).delete())

