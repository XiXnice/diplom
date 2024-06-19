from rest_framework import serializers

from app.models import User, KnowledgeBase, Forum, MessageForum, MessagePatterns
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


class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = ('id', 'theme', 'date_time_creation', 'condition', 'user_id')


class MessageForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageForum
        fields = ('id', 'text', 'date_time_creation', 'user_id', 'forum_id')


class MessagePatternsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagePatterns
        fields = ('id', 'text', 'path_file', 'date_time_creation', 'user_id', 'patterns_id')


class PatternsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ('id', 'theme', 'path_file', 'date_time_creation', 'user_id')