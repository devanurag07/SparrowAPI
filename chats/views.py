from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import ConversationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Conversation,Message,Status
from sparrow.utils import resp_fail,resp_success
from django.db.models import Q
from django.shortcuts import get_object_or_404
from sparrow.utils import required_data
from .serializers import MessageSerializer,StatusSerializer
from accounts.models import User
from rest_framework.decorators import action
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
        data=ConversationSerializer(conversations,many=True,context={
            "request":request}).data
        return Response(resp_success("Conversations Fetched Successfully",{
          "data":data  
        }))
        
    def retrieve(self, request,pk=None, *args, **kwargs):
        if(not pk):
            return Response(resp_fail("Conversation ID Required.."))

        conv=self.get_queryset().filter(pk=pk)
        if(not conv.exists()):
            return Response(resp_fail("Conversation Does Not Exist..."))
        conv=conv.first()
        
        class ConvSerializer(serializers.ModelSerializer):
            messages=MessageSerializer(many=True)
            
            class Meta:
                model=Conversation
                fields="__all__"
        
        conv_data=ConvSerializer(conv,many=False,context={
            "request":request}).data
        return Response(resp_success("Conversation Fetched Successfully.",conv_data))
            
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
    permission_classes=[IsAuthenticated]
    serializer_class=MessageSerializer
    
    def get_queryset(self):
        queryset=Message.objects.filter(sender=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    def create(self, request, *args, **kwargs):
        data=request.data
        success,req_data=required_data(data,["mobile","message"])
        if(not success):
            return Response(resp_fail("[Mobile , Message] Required.."))
        
        
        mobile,message=req_data
        user=request.user
        receivers=User.objects.filter(mobile=mobile)
        if(receivers.exists()):
            reciever=receivers.first()
        else:
            return Response(resp_fail("Reciever Doesn't Exist"))
        
        mobile,message=req_data
        conv=Conversation.objects.filter(Q(user1=user,user2=reciever)| Q(user1=user,user2=user))
        if(conv.exists()):
            created=False
            conv=conv.first()
        else:
            created=True
            conv=Conversation.objects.create(user1=user,user2=reciever)
            
            
        message=Message(conversation=conv,sender=user,reciever=reciever,message=message)
        message.save()
        
        return Response(resp_success("Msg Sent...",{
            "data":MessageSerializer(message,many=False).data,
            "created":created
        }))

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

class StatusAPI(ModelViewSet):
    serializer_class=StatusSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return Status.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        request.data["user"]=request.user.id
        status_form=StatusSerializer(data=request.data)
        if(status_form.is_valid()):
            status=status_form.save()
            return Response(resp_success("Status Uploaded Successfully",{
                "data":status_form.data
            }))
        else:
            return Response(resp_fail("Failed To Upload Status",{
                "errors":status_form.errors
            }))
        
        