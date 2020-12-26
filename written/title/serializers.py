from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from title.models import Title
from posting.models import Posting

class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    postings = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'postings',
        )
    
    def get_postings(self, title):
        return title.postings.all()
