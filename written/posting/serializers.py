from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from posting.models import Posting
from title.models import Title
from written.error_codes import *
from user.serializers import SmallUserSerializer
from django.utils import timezone

class PostingSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    writer = serializers.SerializerMethodField(allow_null=True)
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    alignment = serializers.ChoiceField(Posting.ALIGNMENTS)
    # is_public = serializers.SerializerMethodField()
    
    class Meta:
        model = Posting
        fields = (
            'id',
            'title',
            'writer',
            'content',
            'alignment',
            # 'is_public',
            'created_at',
        )

    def validate(self, data):
        if data.get('title') is None: 
            raise TitleDoesNotExistException
        if data.get('content') is None:
            raise ContentIsEmptyException
        data_copy = data
        try:
            title = Title.objects.get(name=data['title'])
        except Title.DoesNotExist:
            title = Title.objects.create(name=data.get('title'), 
                    created_at=timezone.now(), updated_at=timezone.now(), is_official=False)
        data_copy['title'] = Title.objects.get(name=data['title'])
        return data_copy

    def create(self, validated_data):
        posting = super(PostingSerializer, self).create(validated_data)
        return posting

    def get_writer(self, posting):
        writer = posting.writer
        return SmallUserSerializer(writer, context=self.context).data

    def get_title(self, posting):
        return posting.title.name

class PostingRetrieveSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    alignment = serializers.ChoiceField(Posting.ALIGNMENTS)
    is_public = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField()

    class Meta:
        model = Posting
        fields = (
            'id',
            'title',
            'writer',
            'content',
            'alignment',
            'is_public',
            'created_at',
        )

    def get_writer(self, posting):
        writer = posting.writer
        return SmallUserSerializer(writer, context=self.context).data

    def get_title(self, posting):
        return posting.title.name

class PostingDictSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    alignment = serializers.ChoiceField(Posting.ALIGNMENTS)
    is_public = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField()

    class Meta:
        model = Posting
        fields = (
            'id',
            'title',
            'writer',
            'content',
            'alignment',
            'is_public',
            'created_at',
        )

    def get_writer(self, posting):
        if type(posting) == dict:
            try:
                writer = User.objects.get(pk=posting['writer_id'])
            except User.DoesNotExist:
                return None
        return SmallUserSerializer(writer, context=self.context).data
    
    def get_title(self, posting):
        if type(posting) == dict:
            try:
                title = Title.objects.get(pk=posting['title_id'])
            except Title.DoesNotExist:
                return None
        return title.name
    
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
        writer = posting.writer
        return SmallUserSerializer(writer, context=self.context).data

    def get_title(self, posting):
        return posting.title.name
