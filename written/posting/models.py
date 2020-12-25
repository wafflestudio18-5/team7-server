from django.contrib.auth.models import User
from django.db import models
from title import Title
class Posting(models.Model):
    LEFT = 'LEFT'
    CENTER = 'CENTER'
    ALIGNMENT = [
        (LEFT, LEFT),
        (CENTER, CENTER),
    ]
    title = models.ForeignKey(Title, related_name="posting_title")
    writer = models.ForeignKey(User, related_name="posting_writer")
    content = models.TextField()
    alignment = models.CharField(choices=ALIGNMENT, default=LEFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
