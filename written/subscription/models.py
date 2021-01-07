from django.contrib.auth.models import User
from django.db import models


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriber_subscription', on_delete=models.CASCADE)
    writer = models.ForeignKey(User, related_name='writer_subscription', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'writer'], name='unique_subscription')
        ]
