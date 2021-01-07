from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from title.models import Title
from posting.models import Posting
from posting.serializers import PostingRetrieveSerializer
from written.error_codes import *
from django.utils import timezone

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


class TitleSmallSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    is_official = serializers.BooleanField(default=False)
    count_public_postings = serializers.SerializerMethodField()
    count_all_postings = serializers.SerializerMethodField()
    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'is_official',
            'count_public_postings',
            'count_all_postings',
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

    def get_count_public_postings(self, title):
        if type(title) == dict:
            title = Title.objects.get(pk=title['id'])            
        return title.postings.filter(is_public=True).count()

    def get_count_all_postings(self, title):
        if type(title) == dict:
            title = Title.objects.get(pk=title['id'])
        return title.postings.count()

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