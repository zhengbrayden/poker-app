# Generated by Django 5.1.6 on 2025-03-11 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='room',
        ),
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.DeleteModel(
            name='Room',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
