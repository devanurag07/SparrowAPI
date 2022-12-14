from rest_framework.serializers import ModelSerializer
from .models import Conversation,Message
from accounts.serializers import UserSerializer

class ConversationSerializer(ModelSerializer):
    user1=UserSerializer(many=False,read_only=True)
    user2=UserSerializer(many=False,read_only=True)
    
    class Meta:
        model=Conversation
        fields="__all__"
        
class MessageSerializer(ModelSerializer):
    class Meta:
        model=Message
        fields="__all__"
        