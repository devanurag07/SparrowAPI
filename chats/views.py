from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import ConversationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Conversation,Message
from sparrow.utils import resp_fail,resp_success
from django.db.models import Q
from django.shortcuts import get_object_or_404
from sparrow.utils import required_data
from .serializers import MessageSerializer
from accounts.models import User

# Create your views here.
class ConversationAPI(ModelViewSet):
    serializer_class=ConversationSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        user=self.request.user
        conversation_list=Conversation.objects.filter(Q(user1=user)|Q(user2=user))
        return conversation_list        

    def create(self, request, *args, **kwargs):
        return Response(resp_fail("Methdod Not Allowed"))

    def list(self, request, *args, **kwargs):
        conversations=self.get_queryset()
        data=ConversationSerializer(conversations,many=True).data
        return Response(resp_success("Conversations Fetched Successfully",{
          "data":data  
        }))
        
    def retrieve(self, request,pk=None, *args, **kwargs):
        if(not pk):
            return Response(resp_fail("Conversation ID Required.."))

        conv=self.get_queryset().filter(pk=pk)
        if(conv.exists()):
            return Response(resp_fail("Conversation Does Not Exist..."))
        conv=conv.first()
        
        class ConvSerializer(ConversationSerializer):
            messages=MessageSerializer(many=True)
        
        conv_data=ConvSerializer(conv,many=False).data
        return Response(resp_success("Conversation Fetched Successfully.",{
            "data":conv_data
        }))
            
    def update(self, request, *args, **kwargs):
        return Response(resp_fail("Methdod Not Allowed"))
    
    def destroy(self, request,pk=None, *args, **kwargs):
        if(pk):
            queryset=self.get_queryset()
            convs=queryset.filter(pk=int(pk)) 
            if(convs.exists()):
                convs.delete()
                return Response(resp_success("Conversation Deleted"))
            
            return Response(resp_fail("Conversation Not Found..."))
        
        return Response(resp_fail("Conversation ID Required."))
    
class ChatAPI(ModelViewSet):
    permission_classe=[IsAuthenticated]
    serializer_class=MessageSerializer
    
    def get_queryset(self):
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        data=request.data
        success,req_data=required_data(data,["mobile","message"])
        if(not success):
            return Response(resp_fail("[Mobile , Message] Required.."))
        
        user=request.user
        receivers=User.objects.filter(mobile=mobile)
        if(receivers.exists()):
            reciever=receivers.first()
        else:
            return Response(resp_fail("Reciever Doesn't Exist"))
        
        mobile,message=req_data
        created,conv=Conversation.objects.get_or_create(Q(user1=user,user2=reciever)| Q(user1=user,user2=user))
        message=Message(conversation=conv,sender=user,reciever=reciever,message=message)
        message.save()
        
        return Response(resp_success("Msg Sent...",{
            "data":MessageSerializer(message,many=False).data
        }))

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)