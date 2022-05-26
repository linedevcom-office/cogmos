# Generated by Django 4.0.4 on 2022-05-18 05:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_leader_id_connpass_alter_leader_id_qiita_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZennMember',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]
