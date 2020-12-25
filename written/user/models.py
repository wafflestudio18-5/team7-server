from django.db import models
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth

class UserProfile(models.Model):
    social = models.OneToOneField(UserSocialAuth, on_delete=models.CASCADE)
    user = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=100, blank=True, default="")
    first_posted_at = models.TimeField()
