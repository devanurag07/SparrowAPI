from rest_framework.serializers import ModelSerializer
from .models import Conversation,Message,Status
from accounts.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault


class MessageSerializer(ModelSerializer):
    class Meta:
        model=Message
        fields="__all__"
        
        
class ConversationSerializer(ModelSerializer):
    user1=UserSerializer(many=False,read_only=True)
    user2=UserSerializer(many=False,read_only=True)
    conv_name=serializers.SerializerMethodField(read_only=True)
    last_message=serializers.SerializerMethodField(read_only=True)
    
    def get_conv_name(self,instance):
        current_user=self.context["request"].user
        print(current_user)
        if(current_user==instance.user1):
            return instance.user2.first_name+ ' '+ instance.user2.last_name
        else:
            return instance.user1.first_name+ ' '+instance.user1.last_name
    
    def get_last_message(self,instance):
        messages=instance.messages.all()
        return MessageSerializer(messages.order_by("-created_at").first()).data
        
    class Meta:
        model=Conversation
        fields="__all__"
        

class StatusSerializer(ModelSerializer):
    class Meta:
        model=Status
        fields="__all__"