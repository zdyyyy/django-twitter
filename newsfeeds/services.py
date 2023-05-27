from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls,tweet):
        #先把要请求的instance new好
        newsfeeds = [NewsFeed(user = follower,tweet = tweet) for follower in FriendshipService.get_followers(tweet.user)]
        #自己发帖自己看到
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