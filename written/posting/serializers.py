from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from posting import Posting
from title import Title

class PostingSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    alignment = serializers.ChoiceField(Posting.ALIGNMENT)
    is_public = serializers.BooleanField(default=False)
    
    class Meta:
        model = Posting
        fields = (
            'id',
            'title',
            'writer',
            'content',
            'alignment',
            'is_public',
        )
    
    def get_writer(self, posting):
        return posting.writer

    def get_title(self, posting):
        return posting.title