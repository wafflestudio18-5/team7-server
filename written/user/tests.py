from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
from unittest.mock import patch
from user.token import mocked_check_token
from user.models import UserProfile
from title.models import Title


@patch("user.views.check_token", mocked_check_token)
class PostUserTestCase(TestCase):
    client = Client()

    def setUp(self):
        pass

    def test_invalid_token(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "136748680361026",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], 10001)
        self.assertEqual(data["message"], "Invalid facebook token")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1423",
                "access_token": "14232",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], 10001)
        self.assertEqual(data["message"], "Invalid facebook token")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

    def test_invalid_nickname(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "1367486803610262",
                "nickname": "",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], 10002)
        self.assertEqual(data["message"], "Nickname duplicate")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "1367486803610262",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], 10002)
        self.assertEqual(data["message"], "Nickname duplicate")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

    def test_post(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "1367486803610262",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        data = response.json()
        id = data["user"]["id"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
        userprofile_count = UserProfile.objects.count()
        self.assertEqual(userprofile_count, 1)
        user = User.objects.get(id=id)
        profile = user.userprofile
        self.assertEqual(profile.facebook_id, "1367486803610262")


class GetUserTestCase(TestCase):
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

        Title.objects.create(name="1", is_official=True)

        for i in range(20):
            response = self.client.post(
                '/postings/',
                json.dumps({
                    "title": "1",
                    "content": f"{i}",
                    "alignment": "LEFT",
                    "is_public": False
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token_1
            )
        for i in range(20):
            response = self.client.post(
                '/postings/',
                json.dumps({
                    "title": "1",
                    "content": f"{i}",
                    "alignment": "LEFT",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token_1
            )
            posting_id = response.json()['id']
            response = self.client.put(
                f'/postings/{posting_id}/',
                json.dumps({
                    "is_public": True
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token_1
            )
            data = response.json()
            self.assertEqual(data["is_public"], True)


    def test_get_user_me(self):
        response = self.client.get(
            '/users/me/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_1
        )
        data = response.json()
        self.assertEqual(data["count_public_postings"], 20)
        self.assertEqual(data["count_all_postings"], 40)

    def test_get_user_id(self):
        response = self.client.get(
            f'/users/{self.id_1}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_2
        )
        data = response.json()
        self.assertEqual(data["subscribing"], False)
        self.assertEqual(data["count_public_postings"], 20)

        response = self.client.post(
            f'/users/{self.id_1}/subscribe/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_2
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            f'/users/{self.id_1}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token_2
        )
        data = response.json()
        self.assertEqual(data["subscribing"], True)
        self.assertEqual(data["count_public_postings"], 20)

class PutUserMeTestCase(TestCase):
    client = Client()
    token = ""

    @patch("user.views.check_token", mocked_check_token)
    def setUp(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "1367486803610262",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.token = "Token " + data["access_token"]

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_put_users_me(self):
        response = self.client.put(
            '/users/me/',
            json.dumps({
                "description": "blah blah"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(data['description'], 'blah blah')

        response = self.client.put(
            '/users/me/',
            json.dumps({
                "nickname": "asdf"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(data['nickname'], 'asdf')

        response = self.client.put(
            '/users/me/',
            json.dumps({
                "nickname": "seunghan",
                "description": "pop stars",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(data['nickname'], 'seunghan')
        self.assertEqual(data['description'], 'pop stars')


class GetUserPostingsTestCase(TestCase):
    client = Client()
    token = ""

    @patch("user.views.check_token", mocked_check_token)
    def setUp(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1",
                "access_token": "1",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        data = response.json()
        self.token = "Token " + data["access_token"]
        self.id = data["user"]["id"]

        Title.objects.create(name="1", is_official=True)
        Title.objects.create(name="2", is_official=True)
        Title.objects.create(name="3", is_official=True)

        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "1",
                "content": "1",
                "alignment": "LEFT",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        posting_id = response.json()['id']
        response = self.client.put(
            f'/postings/{posting_id}/',
            json.dumps({
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "2",
                "content": "1",
                "alignment": "CENTER",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        posting_id = response.json()['id']
        response = self.client.put(
            f'/postings/{posting_id}/',
            json.dumps({
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "2",
                "content": "2",
                "alignment": "CENTER",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        posting_id = response.json()['id']
        response = self.client.put(
            f'/postings/{posting_id}/',
            json.dumps({
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "2",
                "content": "2",
                "alignment": "CENTER",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        posting_id = response.json()['id']
        response = self.client.put(
            f'/postings/{posting_id}/',
            json.dumps({
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "3",
                "content": "1",
                "alignment": "CENTER",
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        posting_id = response.json()['id']
        response = self.client.put(
            f'/postings/{posting_id}/',
            json.dumps({
                "is_public": True
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        response = self.client.post(
            '/postings/',
            json.dumps({
                "title": "3",
                "content": "2",
                "alignment": "CENTER",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )

    def test_get_user_posting(self):
        page_size = 2
        response = self.client.get(
            f'/users/{self.id}/postings/?page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["has_next"], True)


        cursor = data["cursor"]
        page_size = 2
        response = self.client.get(
            f'/users/{self.id}/postings/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["has_next"], True)

        cursor = data["cursor"]
        page_size = 2
        response = self.client.get(
            f'/users/{self.id}/postings/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["has_next"], False)


class GetUsersSubscribedTestCase(TestCase):
    client = Client()
    token = []
    id = []

    @patch("user.views.check_token", mocked_check_token)
    def setUp(self):
        for i in range(20):  # create user 0 ~ 19
            response = self.client.post(
                '/users/',
                json.dumps({
                    "facebookid": f"{i}",
                    "access_token": f"{i}",
                    "nickname": f"{i}",
                }),
                content_type='application/json'
            )
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.token.append("Token " + data["access_token"])
            self.id.append(data["user"]["id"])

        for i in range(1, 20):  # user 0 subscribe users 1 ~ 19
            response = self.client.post(
                f'/users/{self.id[i]}/subscribe/',
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token[0]
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_subscribe(self):
        page_size = 5
        response = self.client.get(
            f'/users/subscribed/?page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["writers"]), page_size)
        self.assertEqual(data["has_next"], True)
        cursor = data["cursor"]

        response = self.client.get(
            f'/users/subscribed/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["writers"]), page_size)
        self.assertEqual(data["has_next"], True)
        cursor = data["cursor"]

        response = self.client.get(
            f'/users/subscribed/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["writers"]), page_size)
        self.assertEqual(data["has_next"], True)
        cursor = data["cursor"]

        response = self.client.get(
            f'/users/subscribed/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["writers"]), 4)
        self.assertEqual(data["has_next"], False)
        self.assertEqual(data["cursor"], None)


class GetUsersSubscriberTestCase(TestCase):
    client = Client()
    token = []
    id = []

    @patch("user.views.check_token", mocked_check_token)
    def setUp(self):
        for i in range(20):  # create user 0 ~ 19
            response = self.client.post(
                '/users/',
                json.dumps({
                    "facebookid": f"{i}",
                    "access_token": f"{i}",
                    "nickname": f"{i}",
                }),
                content_type='application/json'
            )
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.token.append("Token " + data["access_token"])
            self.id.append(data["user"]["id"])

        for i in range(1, 20):  # user 1~19 subscribe user 0
            response = self.client.post(
                f'/users/{self.id[0]}/subscribe/',
                content_type='application/json',
                HTTP_AUTHORIZATION=self.token[i]
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_subscriber(self):
        page_size = 5
        response = self.client.get(
            f'/users/subscriber/?page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["subscribers"]), page_size)
        self.assertEqual(data["has_next"], True)
        cursor = data["cursor"]

        response = self.client.get(
            f'/users/subscriber/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["subscribers"]), page_size)
        self.assertEqual(data["has_next"], True)
        cursor = data["cursor"]

        response = self.client.get(
            f'/users/subscriber/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["subscribers"]), page_size)
        self.assertEqual(data["has_next"], True)
        cursor = data["cursor"]

        response = self.client.get(
            f'/users/subscriber/?cursor={cursor}&page_size={page_size}',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token[0]
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["subscribers"]), 4)
        self.assertEqual(data["has_next"], False)
        self.assertEqual(data["cursor"], None)
