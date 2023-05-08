from accounts.api.serializers import UserSerializer
from rest_framework import serializers
from tweets.models import Tweet
class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer() #if we do not have such serializer, the user in the fields would be returned as int type

    class Meta:
        model = Tweet
        fields = ('id','user','created_at','content')


class TweetCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6,max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)   #avoid using others' id to tweet

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user,content=content)
        return tweet