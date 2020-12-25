from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from user.models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(required=True)

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

    def validate(self, data):
        return data

    def update(self, user, data):
        if data.get('description'):
            profile = user.userprofile
            profile.description = data.get('description')
            profile.save()
        return