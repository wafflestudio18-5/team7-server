from django.db import models
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facebook_id = models.CharField(max_length=20, unique=True, default="")
    nickname = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=100, blank=True, default="")
    first_posted_at = models.TimeField(null=True, default=None)

