from django.contrib.auth.models import User
from django.db import models

from posting.models import Posting


class Scrap(models.Model):
    user = models.ForeignKey(User, related_name='scrap', on_delete=models.CASCADE)
    posting = models.ForeignKey(Posting, related_name='scrap', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'posting'], name='unique_scrap')
        ]
