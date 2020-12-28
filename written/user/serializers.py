from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from user.models import UserProfile
import requests
from rest_framework import status
from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    first_posted_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'nickname',
            'description',
            'first_posted_at',
        )

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        return user

    def update(self, user, data):
        if data.get('description'):
            profile = user.userprofile
            profile.description = data.get('description')
            profile.save()
        if data.get('nickname'):
            if UserProfile.objects.filter(nickname=data.get('nickname')).count() != 0:
                raise serializers.ValidationError("Nickname duplicate")
            profile = user.userprofile
            profile.nickname = data.get('nickname')
            profile.save()
        return

    def get_nickname(self, user):
        return user.userprofile.nickname

    def get_description(self, user):
        return user.userprofile.description

    def get_first_posted_at(self, user):
        return user.userprofile.first_posted_at