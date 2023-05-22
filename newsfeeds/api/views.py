from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.paginations import EndlessPagination

# Create your views here.
class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination
    def get_queryset(self):
        return NewsFeed.objects.filter(user = self.request.user)

    def list(self,request):
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = NewsFeedSerializer(queryset,
                                        context = {'request':request},
                                        many = True)
        return self.get_paginated_response(serializer.data)


