from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.decorators import required_params
class NotificationView(viewsets.GenericViewSet,
                       viewsets.mixins.ListModelMixin,):
    serializer_class = NotificationSerializer
    permission_class = (IsAuthenticated,)
    fields = ('unread',)

    def get_queryset(self):
        return self.request.user.notification.all()

    @action(methods = ['GET'],detail = False,url_path='unread-count')
    def unread_count(self,request,*args,**kwargs):
        count = self.get_queryset().filter(unread = True).count()
        return Response({
            'unread_count':count
        },status = status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='update-count')
    def mark_as_all_read(self, request, *args, **kwargs):
        count = self.get_queryset().update(unread=False)
        return Response({
            'update_count': count
        }, status=status.HTTP_200_OK)

    @required_params(method = 'POST',params = 'unread')
    def update(self,request,*args,**kwargs):
        serializer = NotificationSerializerForUpdate(
            instance = self.get_object(),
            data = request.data,
        )

        if not serializer.is_valid():
            return Response({
                'message':'Please check input',
                'errors': serializer.errors,
            },status = status.HTTP_400_BAD_REQUEST)

        notification = serializer.save()

        #create userprofile object
        user.profile

        return Response(
            NotificationSerializer(notification.data),
            status = status.HTTP_200_OK,)
