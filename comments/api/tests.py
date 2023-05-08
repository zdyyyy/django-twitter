from testing.testcases import TestCase
from rest_framework.test import APIClient
from comments.models import Comment
from django.utils import timezone

COMMENT_URL = '/api/comments/'

class CommentApiTest(TestCase):

    def setUp(self):

        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        self.tweet = self.create_tweet(self.linghu)

    def test_create(self):
        # Anonymous client cannot post tweet
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # Should have parameters
        response = self.linghu_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # Only tweet id
        response = self.linghu_client.post(COMMENT_URL,{'tweet_id':self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # Only content
        response = self.linghu_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # Content is too long
        response = self.linghu_client.post(COMMENT_URL, {'tweet_id': self.tweet.id,'content': '1'*141})
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'],True)

        # Content and tweet id
        response = self.linghu_client.post(COMMENT_URL, {'tweet_id': self.tweet.id, 'content': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_update(self):
        comment = self.create_comment(self.linghu,self.tweet,'origin')
        another_tweet = self.create_tweet(self.dongxie)
        url = '{}{}/'.format(COMMENT_URL,comment.id)

        #anonymous user cannot update
        response = self.anonymous_client.put(url,{'content':'new'})
        self.assertEqual(response.status_code, 403)

        # Not self cannot update
        response = self.dongxie_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEquals(comment.content,'new')

        # Cannot delete anything except for content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.linghu_client.put(url,{
            'content':'new',
            'user_id': self.dongxie.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code,200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.linghu)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)












