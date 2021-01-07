from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
from unittest.mock import patch
from user.token import mocked_check_token
from user.models import UserProfile
from title.models import Title
from title.views import TitleViewSet

class PostTitleTestCase(TestCase):
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

    def test_valid_post_titles(self):
        response = self.client.post(
            '/titles/',
            json.dumps({
                "name": "title1"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['name'], 'title1')
        self.assertEqual(data['is_official'], False)
        self.assertEqual(data['postings'], [])

    def test_invalid_post_titles_name_duplicate(self):
        response = self.client.post(
            '/titles/',
            json.dumps({
                "name": "title1"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            '/titles/',
            json.dumps({
                "name": "title1"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
class GetTitleTestCase(TestCase):
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
        self.token = "Token " + data["access_token"]
        self.id = data["user"]["id"]

        for i in range (30):
            titlename = "title" + str(i)
            response = self.client.post(
                '/titles/',
                json.dumps({
                    "name": titlename
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_valid_get_titles(self):
        response = self.client.get(
            '/titles/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['titles']), TitleViewSet.TITLES_PAGE_SIZE_DEFAULT)
        cursor = data['cursor']
        has_next = data['has_next']
        self.assertEqual(has_next, True)

        response = self.client.get(
            f'/titles/?cursor={cursor}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['titles']), TitleViewSet.TITLES_PAGE_SIZE_DEFAULT)
        self.assertEqual(data['cursor'], cursor-4)
        self.assertEqual(has_next, True)

        page_size = 5
        response = self.client.get(
            f'/titles/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['titles']), 5)
        self.assertEqual(data['cursor'], cursor-5)
        
    def test_invalid_get_titles(self):
        response = self.client.get(
            f'/titles/?time=invalid',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['errorcode'], 20002)
        self.assertEqual(data['message'], 'Title does not exist')
        
        response = self.client.get(
            f'/titles/?only_official=invalid',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['errorcode'], 20002)
        self.assertEqual(data['message'], 'Title does not exist')        
        
        response = self.client.get(
            f'/titles/?order=invalid',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['errorcode'], 20002)
        self.assertEqual(data['message'], 'Title does not exist')
