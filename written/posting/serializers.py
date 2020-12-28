from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from posting.models import Posting
from title.models import Title

class PostingSerializer(serializers.ModelSerializer):
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

    def validate(self):
        if (title is None) or (writer is None) or (content is None):
            raise TitleDoesNotExistException
        # TODO... is any other conditions?
        return True

    def get_writer(self, posting):
        return posting.writer
        # after merge into facebook login/logout, replace it with below
        # return SmallUserSerializer(posting.writer, context=self.context).data

    def get_title(self, posting):
        return posting.title.name
        