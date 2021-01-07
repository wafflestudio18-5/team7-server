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
from posting.models import Posting

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
        last_title = Title.objects.last()
        self.assertEqual(data['titles'][0]['id'], last_title.id)

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

        response = self.client.get(
            '/titles/?order=oldest',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['titles']), TitleViewSet.TITLES_PAGE_SIZE_DEFAULT)
        first_title = Title.objects.first()
        self.assertEqual(data['titles'][0]['id'], first_title.id)

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


class GetTitleTodayTestCase(TestCase):
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

    def test_valid_titles_today(self):
        response = self.client.get(
            '/titles/today/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        last_title = Title.objects.last()
        self.assertEqual(data['id'], last_title.id)

    def test_invalid_titles_today(self):
        response = self.client.get(
            '/titles/yesterday/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        
class GetTitlePostingsTestCase(TestCase):
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

        for i in range (50):
            postingcontent = "This is content " + str(i)
            response = self.client.post(
                '/postings/',
                json.dumps({
                    "title": "title1",
                    "content": postingcontent,
                    "alignment": "LEFT",
                    "is_public": True   
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_title_postings(self):
        title1_id = Title.objects.get(name='title1').id
        
        response = self.client.get(
            f'/titles/{title1_id}/postings/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['has_next'], True)

        last_posting_id = Posting.objects.last().id
        self.assertEqual(data['postings'][0]['id'], last_posting_id)
        self.assertLess(data['cursor'], last_posting_id)
        cursor = data['cursor']

        response = self.client.get(
            f'/titles/{title1_id}/postings/?cursor={cursor}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['has_next'], True)

        last_posting_id = Posting.objects.last().id
        self.assertNotEqual(data['postings'][0]['id'], last_posting_id)
        self.assertLess(data['cursor'], cursor)

    def test_invalid_title_postings(self):
        title1_id = Title.objects.last().id
        title1_id += 1

        response = self.client.get(
            f'/titles/{title1_id}/postings/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['errorcode'], 20002)