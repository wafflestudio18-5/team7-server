# Generated by Django 3.1 on 2021-01-01 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posting', '0002_posting_is_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posting',
            name='writer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='postings', to=settings.AUTH_USER_MODEL),
        ),
    ]
