from django.db import models
from accounts.models import User

# Create your models here.


class Conversation(models.Model):
    user1=models.ForeignKey(User,on_delete=models.CASCADE,related_name="convs1")
    user2=models.ForeignKey(User,on_delete=models.CASCADE,related_name="convs2")
    isArchived=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
class Message(models.Model):
    conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name="messages")
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name="sent_messages")
    reciever=models.ForeignKey(User,on_delete=models.CASCADE,related_name="received_messages")
    message=models.TextField()
    isStarred=models.BooleanField(default=False)

    
    STATUS_CHOICES=[
        (0,"SENT"),
        (1,"DELIVERED"),
        (2,"SEEN"),
    ]
    
    status=models.IntegerField(choices=STATUS_CHOICES,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    
    
class Document(models.Model):
    message=models.ForeignKey(Message,on_delete=models.CASCADE,related_name="documents")
    document=models.FileField(upload_to="media/documents/")
    created_at=models.DateTimeField(auto_now_add=True)
    
    
class Image(models.Model):
    message=models.ForeignKey(Message,on_delete=models.CASCADE)
    document=models.ImageField(upload_to="media/images/")
    created_at=models.DateTimeField(auto_now_add=True)
    
    

class Status(models.Model):
    media=models.FileField(upload_to="media/status/")
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="status_all")
    views=models.ManyToManyField(User,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    

# class GroupChat(models.Model):
#     group_name=models.CharField(max_length=255)
#     users=models.ManyToManyField(User)
#     admins=models.ManyToManyField(User)
#     created_by=models.ForeignKey(User,on_delete=models.CASCADE)
    

#WebSockets --Models
class WSClient(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    channel_name=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    
class SignallingWSClient(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    channel_name=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    
    