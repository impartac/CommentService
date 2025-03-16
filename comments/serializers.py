from rest_framework import serializers
from .models import Post, Comment, Like, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'author', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    like_ids = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'likes', 'like_ids']

    def get_likes(self, obj):
        return obj.likes

    def get_like_ids(self, obj):
        return obj.like_ids

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'post']