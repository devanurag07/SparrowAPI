# Generated by Django 4.1.4 on 2023-04-08 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0014_remove_message_reciever_message_recievers'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupchat',
            name='group_profile',
            field=models.ImageField(default='profilepics/default-group.jpg', upload_to='profilepics'),
        ),
    ]