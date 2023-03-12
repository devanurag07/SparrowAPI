# Generated by Django 4.1.4 on 2023-02-21 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_historicaluser_profile_pic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluser',
            name='profile_pic',
            field=models.TextField(default='profilepics/default.jpg', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(default='profilepics/default.jpg', upload_to='profilepics'),
        ),
    ]