# Generated by Django 3.1 on 2021-01-09 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_userprofile_facebook_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='first_posted_at',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]