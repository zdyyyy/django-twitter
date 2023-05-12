from django_filters.rest_framework import DjangoFilterBackend
from inbox.api.serializers import NotificationSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

