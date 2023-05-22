from django.contrib.auth.models import User
from friendships.api.paginations import FriendshipPagination
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    pagination_class = FriendshipPagination

    @action(methods = ['GET'],detail=True,permission_classes = [AllowAny])
    def followers(self,request,pk):
        #GET /api/friendships/{}/followers
        friendships = Friendship.objects.filter(to_user_id = pk).order_by('-created_at')
        #serilizer is responsible for parsing
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page,context={'request':request},many = True)
        return self.get_paginated_response(serializer.data)
    @action(methods=['GET'], detail=True, permission_classes = [AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page,context={'request':request},many = True)
        return self.get_paginated_response(serializer.data)
    @action(methods=['POST'], detail=True, permission_classes = [IsAuthenticated])
    def follow(self,request,pk):
        if Friendship.objects.filter(from_user=request.user,to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True
            },status = status.HTTP_201_CREATED)

        #current user follows the follower whose id is pk
        serializer = FriendshipSerializerForCreate(data = {
            'from_user_id':request.user.id,
            'to_user_id': pk,
        })

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            },status = status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'success': True},status = status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes = [IsAuthenticated])
    def unfollow(self, request, pk):
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself'
            },status = status.HTTP_400_BAD_REQUEST)
        deleted, _ = Friendship.objects.filter(
            from_user = request.user.id,
            to_user = pk,
        ).delete()
        return Response({'success': True,'deleted':deleted})