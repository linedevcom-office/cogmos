# Generated by Django 4.0.4 on 2022-05-11 00:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_rename_roleatseminar_roleatevent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='roleatevent',
            old_name='name',
            new_name='title',
        ),
    ]
