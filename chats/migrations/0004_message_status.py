# Generated by Django 4.1.4 on 2022-12-17 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0003_alter_status_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='status',
            field=models.IntegerField(choices=[(0, 'SENT'), (1, 'DELIVERED'), (2, 'SEEN')], default=0),
        ),
    ]
