# Generated by Django 4.1.4 on 2022-12-28 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_historicalotptempdata_mobile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluser',
            name='bio',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(default='At Sparrow'),
            preserve_default=False,
        ),
    ]
