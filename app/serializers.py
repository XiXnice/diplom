from rest_framework import serializers

from app.models import User, KnowledgeBase, Forum
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'last_name', 'first_name', 'patronymic', 'email', 'password')
        read_only_fields = ('id',)


class KnowledgeBaseArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ('id', 'theme', 'text', 'date_time_creation', 'user_id')


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key', 'user_id')


class ForumSerializer(serializers.Serializer):
    class Meta:
        model = Forum
        fields = ('id', 'theme', 'date_time_creation', 'condition', 'user_id')