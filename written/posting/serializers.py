from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from posting.models import Posting
from title.models import Title
from written.error_codes import *

class PostingSerializer(serializers.ModelSerializer):
    # title = serializers.SerializerMethodField()
    title = serializers.CharField()
    writer = serializers.SerializerMethodField(allow_null=True)
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    alignment = serializers.ChoiceField(Posting.ALIGNMENTS)
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

    def validate(self, data):
        if data.get('title') is None: 
            raise TitleDoesNotExistException
        if data.get('content') is None:
            raise ContentIsEmptyException
        data_copy = data
        title = Title.objects.get(name=data['title'])
        data_copy['title'] = Title.objects.get(name=data['title'])
        return data_copy

    def create(self, validated_data):
        posting = super(PostingSerializer, self).create(validated_data)
        return posting

    def get_writer(self, posting):
        return posting.writer
        # after merge into facebook login/logout, replace it with below
        # return SmallUserSerializer(posting.writer, context=self.context).data

    def get_title(self, posting):
        return posting.title.name
        

class PostingRetrieveSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    alignment = serializers.ChoiceField(Posting.ALIGNMENTS)
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
        # after merge into facebook login/logout, replace it with below
        # return SmallUserSerializer(posting.writer, context=self.context).data

    def get_title(self, posting):
        return posting.title.name

class PostingUpdateSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField(allow_null=True)
    content = serializers.CharField(style={'base_template': 'textarea.html'}, allow_null=True)
    alignment = serializers.ChoiceField(Posting.ALIGNMENTS, allow_null=True)
    is_public = serializers.BooleanField(default=False, allow_null=True)
    
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
            
    #     return data

    def get_writer(self, posting):
        return posting.writer
        # after merge into facebook login/logout, replace it with below
        # return SmallUserSerializer(posting.writer, context=self.context).data

    def get_title(self, posting):
        return posting.title.name
