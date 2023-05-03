# from django.test import TestCase
from rest_framework.test import APIClient
# from django.contrib.auth.models import User
from testing.testcases import TestCase

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # self.user = self.createUser(
        self.user = self.create_user(
            username='admin',
            email='admin@jiuzhang.com',
            password="correct password",
        )
    # def createUser(self,username,email,password):
    #     return User.objects.create_user(username,email,password)

    def test_login(self):

        #should be POST
        response = self.client.get(LOGIN_URL,{
            'username': self.user.username,
            'password':'correct password',
        })
        self.assertEqual(response.status_code, 405)

        #POST, but wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        #Verify not log yet
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],False)

        #correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'],None)
        self.assertEqual(response.data['user']['email'],'admin@jiuzhang.com')

        #verify user has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],True)

    def test_logout(self):

        #login
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        #verify user already logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],True)

        #should be POST
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        #success after POST
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        #verify user logged out
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }

        #test GET fail
        response = self.client.get(SIGNUP_URL,data)
        self.assertEqual(response.status_code, 405)

        #test wrong email address
        response = self.client.post(SIGNUP_URL,{
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        #test short password
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        #test long username
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is toooooooo loooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        #register successfully
        response = self.client.post(SIGNUP_URL,data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'],'someone')

        #verify user has already logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)



