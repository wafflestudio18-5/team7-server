# Generated by Django 3.1 on 2020-12-26 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='facebook_id',
            field=models.CharField(default='', max_length=20, unique=True),
        ),
    ]
