from accounts.models import UserProfile
from django.contrib.auth.models import User
from rest_framework import serializers,exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username")


class UserSerializerWithProfile(UserSerializer):
    nickname = serializers.CharField(source = 'profile.nickname')
    avatar = serializers.SerializerMethodField()

    def get_avatar(self,obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    class Meta:
        model = User
        fields = ('id','username','nickname','avatar_url')


class UserSerializerForTweet(UserSerializerWithProfile):
    pass


class UserSerializerForComment(UserSerializerWithProfile):
    pass


class UserSerializerForFriendship(UserSerializerWithProfile):
    pass


class UserSerializerForLike(UserSerializerWithProfile):
    pass


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20,min_length=6)
    password = serializers.CharField(max_length=20,min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username','email','password')

    def validate(self,data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'The username has already been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'The email adress has already been occupied.'
            })
        return data

    def create(self,validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username = username,
            email = email,
            password = password,
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname','avatar')

