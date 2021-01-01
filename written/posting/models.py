from django.contrib.auth.models import User
from django.db import models
from title.models import Title
class Posting(models.Model):
    LEFT = 'LEFT'
    CENTER = 'CENTER'
    ALIGNMENT_CHOICES = [
        (LEFT, LEFT),
        (CENTER, CENTER),
    ]
    ALIGNMENTS = (LEFT, CENTER)

    title = models.ForeignKey(Title, related_name="postings", on_delete=models.CASCADE)
    writer = models.ForeignKey(User, related_name="postings", on_delete=models.CASCADE, null=True)
    content = models.TextField()
    alignment = models.CharField(choices=ALIGNMENT_CHOICES, default=LEFT, max_length=7)
    is_public = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
