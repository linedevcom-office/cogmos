# Generated by Django 4.0.4 on 2022-05-09 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_connpasspopularevent_dailyyoutubesubscriber_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='url',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]