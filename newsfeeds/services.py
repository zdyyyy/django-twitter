from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService

class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls,tweet):
        #先把要请求的instance new好
        newsfeeds = [NewsFeed(user = follower,tweet = tweet) for follower in FriendshipService.get_followers(tweet.user)]
        #自己发帖自己看到
        newsfeeds.append(NewsFeed(user = tweet.user,tweet = tweet))
        NewsFeed.objects.bulk_create(newsfeeds)


