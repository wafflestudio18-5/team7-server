from django.contrib.auth.models import User
from django.db import models

class Title(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)    
    is_official = models.BooleanField(default=True, db_index=True)