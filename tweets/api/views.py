from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from tweets.services import TweetService
from utils.decorators import required_params
from utils.paginations import EndlessPagination
# Create your views here.
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action in ['list','retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self,request,*args,**kwargs):
        serializer = TweetSerializerForCreate(   #for creating tweet
            data = request.data,
            context = {'request':request}  #extra info
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message':"Please check input",
                'errors':serializer.errors,
            },status = 400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        serializer = TweetSerializer(tweet,context = {'request':request})
        return Response(serializer.data,status = 201)

    @required_params(params=['user_id'])
    def list(self, request, *args,**kwargs):
        user_id = request.query_params['user_id']
        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets,request)
        if page is None:
            queryset = Tweet.objects.filter(user_id = user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request':request},
            many = True,
        )
        return Response({'tweets': serializer.data})

    def retrieve(self,request,*args,**kwargs):
        serializer = TweetSerializerForDetail(
            self.get_object(),
            context = {'request':request},
        )
        return Response(serializer.data)