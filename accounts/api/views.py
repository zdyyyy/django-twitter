from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
    UserSerializerWithProfile,
    UserProfileSerializerForUpdate
)
from accounts.models import UserProfile
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth import(
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from utils.permissions import IsObjectOwner

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializerWithProfile
    permissions_classes = (permissions.IsAdminUser,)

class AccountViewSet(viewsets.ViewSet):
    permissions_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['POST'],detail=False)
    def signup(self,request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success':False,
                'message':"Please check input",
                'errors':serializer.errors,
            },status = 400)

        user = serializer.save()

        #Create UserProfile Object
        user.profile

        django_login(request,user)
        return Response({
            'success':True,
            'user':UserSerializer(user).data,
        },status = 201)
    @action(methods=['POST'],detail=False)
    def login(self,request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            },status = 400)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # queryset = User.objects.filter(username = username)
        # print(queryset.query())

        if not User.objects.filter(username = username).exists():
            return Response({
                "success": False,
                "message": "username does not exist",
            }, status=400)

        user = django_authenticate(username=username,password=password)
        if not user or user.is_anonymous:
            return Response({
                "success":False,
                "message":"username and password does not match",
            },status = 400)

        django_login(request,user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['GET'],detail=False)
    def login_status(self,request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'],detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success':True})

class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permissions_classes = (IsObjectOwner,)
    serializer_class = UserProfileSerializerForUpdate
