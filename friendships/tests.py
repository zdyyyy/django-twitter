from testing.testcases import TestCase
from friendships.models import Friendship
from rest_framework.test import APIClient

# Create your tests here.
FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWER_URL = '/api/friendships/{}/followers/'
FOLLOWING_URL = '/api/friendships/{}/followings/'

class FriendshipAPITests(TestCase):
    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # create followings and followers for dongxie
        for i in range(2):
            follower = self.create_user('dongxie_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.dongxie)
        for i in range(3):
            following = self.create_user('dongxie_following{}'.format(i))
            Friendship.objects.create(from_user=self.dongxie, to_user=following)


    def test_follow(self):
        url = FOLLOW_URL.format(self.linghu.id)

        #login to follow
        response = self.anonymous_client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, 403)

        #method = get
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)

        #cannot follow self
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)

        #successfully follow
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 201)

        #repeatly follow, keep silence
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'],True)

        # repeatedly follow, keep silence
        count = Friendship.objects.count()
        response = self.linghu_client.post(FOLLOW_URL.format(self.dongxie.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(),count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.linghu.id)

        #login to unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        #method = get
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)

        #cannot unfollow self
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)

        #successfully unfollow
        Friendship.objects.create(from_user=self.dongxie,to_user=self.linghu)
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # Under the condition of unfollow, keep silence for follow
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(),count)

    def test_followings(self):
        url = FOLLOWING_URL.format(self.dongxie.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # 确保按照时间倒序
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'dongxie_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'dongxie_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'dongxie_following0',
        )

    def test_followers(self):
        url = FOLLOWER_URL.format(self.dongxie.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # 确保按照时间倒序
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'dongxie_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'dongxie_follower0',
        )


