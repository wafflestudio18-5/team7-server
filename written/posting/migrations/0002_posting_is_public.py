# Generated by Django 3.1 on 2021-01-01 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='posting',
            name='is_public',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
