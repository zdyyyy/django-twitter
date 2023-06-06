from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls,tweet):
        #create a new request instance first
        newsfeeds = [NewsFeed(user = follower,tweet = tweet) for follower in FriendshipService.get_followers(tweet.user)]
        #can see the tweet created by self
        newsfeeds.append(NewsFeed(user = tweet.user,tweet = tweet))
        NewsFeed.objects.bulk_create(newsfeeds)

        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

    @classmethod
    def get_cached_newsfeeds(cls,user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key,queryset)

    @classmethod
    def push_newsfeed_to_cache(cls,newsfeed):
        queryset = NewsFeed.objects.filter(user_id = newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id = newsfeed.user_id)
        RedisHelper.push_object(key,newsfeed,queryset)

    @classmethod
    def create(cls, **kwargs):
        newsfeed = NewsFeed.objects.create(**kwargs)
        return newsfeed

    @classmethod
    def batch_create(cls,batch_params):
        newsfeeds = [NewsFeed(**params) for params in batch_params]
        NewsFeed.objects.bulk_create(newsfeeds)
        for newsfeed in newsfeeds:
            NewsFeedService.push_newsfeed_to_cache(newsfeed)
        return newsfeeds