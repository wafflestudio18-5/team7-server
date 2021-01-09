from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
from unittest.mock import patch
from user.token import mocked_check_token
from user.models import UserProfile
from title.models import Title
from posting.models import Posting

class PostPostingTestCase(TestCase):
    client = Client()

    @patch("user.views.check_token", mocked_check_token)
    def setUp(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1",
                "access_token": "1",
                "nickname": "1",
            }),
            content_type='application/json'
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.token_1 = "Token " + data["access_token"]
        self.id_1 = data["user"]["id"]

        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "2",
                "access_token": "2",
                "nickname": "2",
            }),
            content_type='application/json'
        )
        data = response.json()
        self.token_2 = "Token " + data["access_token"]

    def test_valid_post_postings(self):
        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "title1",
                "content": "This is content of posting1",
                "alignment": "LEFT",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['title'], 'title1')
        self.assertEqual(data['content'], 'This is content of posting1')
        self.assertEqual(data['alignment'], 'LEFT')
        
        for i in range(20):
            response = self.client.post(
                '/postings/',
                json.dumps({
                    "title": "title1",
                    "content": "This is content of posting1",
                    "alignment": "LEFT",
                    "is_public": True
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token_1
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(pk=self.id_1)
        self.assertIsNotNone(user.userprofile.first_posted_at)


    def test_invalid_post_postings_empty_content(self):
        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "title1",
                "content": "",
                "alignment": "LEFT",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GetPostingTestCase(TestCase):
    client = Client()

    @patch("user.views.check_token", mocked_check_token)
    def setUp(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1",
                "access_token": "1",
                "nickname": "1",
            }),
            content_type='application/json'
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.token_1 = "Token " + data["access_token"]
        self.id_1 = data["user"]["id"]

        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "title1",
                "content": "This is content of posting1",
                "alignment": "LEFT",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_valid_get_postings(self):
        last_posting_id = Posting.objects.last().id
        response = self.client.get(
            f'/postings/{last_posting_id}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['title'], 'title1')
        self.assertEqual(data['writer']['nickname'], '1')

    def test_invalid_get_postings(self):
        last_posting_id = Posting.objects.last().id
        response = self.client.get(
            f'/postings/{last_posting_id+1}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['errorcode'], 20003)

class PutPostingTest(TestCase):
    client = Client()

    @patch("user.views.check_token", mocked_check_token)
    def setUp(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1",
                "access_token": "1",
                "nickname": "1",
            }),
            content_type='application/json'
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.token_1 = "Token " + data["access_token"]
        self.id_1 = data["user"]["id"]

        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "title1",
                "content": "This is content of posting1",
                "alignment": "LEFT",
                "is_public": False
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_put_postings(self):
        last_posting_id = Posting.objects.last().id
        response = self.client.get(
            f'/postings/{last_posting_id}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['title'], 'title1')
        self.assertEqual(data['writer']['nickname'], '1')
        self.assertEqual(data['content'], 'This is content of posting1')

        response = self.client.put(
            f'/postings/{last_posting_id}/',
            json.dumps({
                "content": "Changed content",
                "alignment": "LEFT",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['title'], 'title1')
        self.assertEqual(data['writer']['nickname'], '1')
        self.assertEqual(data['content'], 'Changed content')
        self.assertEqual(data['is_public'], True)

    def test_invalid_put_postings(self):
        last_posting_id = Posting.objects.last().id
        response = self.client.get(
            f'/postings/{last_posting_id}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['title'], 'title1')
        self.assertEqual(data['writer']['nickname'], '1')
        self.assertEqual(data['content'], 'This is content of posting1')

        response = self.client.put(
            f'/postings/{last_posting_id}/',
            json.dumps({
                "content": "Changed content",
                "alignment": "LEFT",
                "is_public": 'asdf'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(
            f'/postings/{last_posting_id}/',
            json.dumps({
                "content": "Changed content",
                "alignment": "INVALID",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)