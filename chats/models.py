from django.db import models
from accounts.models import User

# Create your models here.


class Conversation(models.Model):
    user1=models.ForeignKey(User,on_delete=models.CASCADE,related_name="convs")
    user2=models.ForeignKey(User,on_delete=models.CASCADE,related_name="convs")
    created_at=models.DateTimeField(auto_now_add=True)
    
class Message(models.Model):
    conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name="messages")
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name="sent_messages")
    reciever=models.ForeignKey(User,on_delete=models.CASCADE,related_name="received_messages")
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    
class Document(models.Model):
    message=models.ForeignKey(Message,on_delete=models.CASCADE,related_name="documents")
    document=models.FileField(upload_to="media/documents/")
    created_at=models.DateTimeField(auto_now_add=True)
    
    
class Image(models.Model):
    message=models.ForeignKey(Message,on_delete=models.CASCADE)
    document=models.ImageField(upload_to="media/images/")
    created_at=models.DateTimeField(auto_now_add=True)
    