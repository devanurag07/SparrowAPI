from rest_framework.serializers import ModelSerializer
from .models import Conversation,Message,Status
from accounts.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault


class MessageSerializer(ModelSerializer):
    
    status=serializers.SerializerMethodField(read_only=True)
    
    
    def get_status(self,instance):
        
        msg_status=instance.status
        status_text=''
        if(msg_status==0):
            status_text="sent"
        elif msg_status==1:
            msg_status="delivered"
        elif msg_status==2:
            status_text="seen"
            
        return status_text
    class Meta:
        model=Message
        fields="__all__"
        
        
class ConversationSerializer(ModelSerializer):
    conv_name=serializers.SerializerMethodField(read_only=True)
    last_message=serializers.SerializerMethodField(read_only=True)
    avatar=serializers.SerializerMethodField(read_only=True)
    
    def get_conv_name(self,instance):
        current_user=self.context["request"].user
        print(current_user)
        if(current_user==instance.user1):
            return instance.user2.first_name+ ' '+ instance.user2.last_name
        else:
            return instance.user1.first_name+ ' '+instance.user1.last_name
    
    def get_avatar(self,instance):
        return ''
    
    def get_last_message(self,instance):
        messages=instance.messages.all()
        last_message=messages.order_by("-created_at").first()
        msg_status=last_message.status
        msg_time=str(last_message.created_at.time())
        status_text=''
        if(msg_status==0):
            status_text="sent"
        elif msg_status==1:
            msg_status="delivered"
        elif msg_status==2:
            status_text="seen"
            
        return {
            "message":last_message.message,
            "status":status_text,
            "timestamp":msg_time
        }
        
 
    class Meta:
        model=Conversation
        fields="__all__"
        

class StatusSerializer(ModelSerializer):
    class Meta:
        model=Status
        fields="__all__"