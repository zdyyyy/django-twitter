from django.shortcuts import render
from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetCreateSerializer,
    TweetSerializerWithComments)
from tweets.models import Tweet
from utils.decorators import required_params
# Create your views here.
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action in ['list','retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self,request,*args,**kwargs):
        serializer = TweetCreateSerializer(   #for creating tweet
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
        return Response(TweetSerializer(tweet).data,status = 201)

    @required_params(params=['user_id'])
    def list(self, request, *args,**kwargs):
        tweets = Tweet.objects.filter(
            user_id = request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets,many = True)  #list of dict #for showing
        return Response({'tweets': serializer.data})

    def retrieve(self,request,*args,**kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)