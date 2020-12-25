from django.contrib.auth.models import User
from django.db import models
from title import Title
class Posting(models.Model):
    LEFT = 'LEFT'
    CENTER = 'CENTER'
    ALIGNMENT_CHOICES = [
        (LEFT, LEFT),
        (CENTER, CENTER),
    ]
    ALIGNMENTS = (LEFT, CENTER)

    title = models.ForeignKey(Title, related_name="postings")
    writer = models.ForeignKey(User, related_name="postings")
    content = models.TextField()
    alignment = models.CharField(choices=ALIGNMENT_CHOICES, default=LEFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
