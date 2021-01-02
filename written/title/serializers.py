from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from title.models import Title
from posting.models import Posting
from posting.serializers import PostingRetrieveSerializer
from written.error_codes import *

class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    postings = serializers.SerializerMethodField()
    is_official = serializers.BooleanField(default=False)
    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'is_official',
            'postings',
        )
    def validate(self, data):
        name = data.get('name')
        if name is None or name == '':
            raise TitleNameIsEmptyException()
        method = self.context['request'].method
        if method == 'POST':
            if Title.objects.filter(name=name):
                raise TitleNameIsDuplicateException()
        return data

    def get_postings(self, title):
        postings = title.postings.all()
        return PostingRetrieveSerializer(postings, many=True).data

class TitleUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    postings = serializers.SerializerMethodField()
    is_official = serializers.BooleanField()
    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'is_official',
            'postings',
        )

    def get_postings(self, title):
        postings = title.postings.all()
        return PostingRetrieveSerializer(postings, many=True).data