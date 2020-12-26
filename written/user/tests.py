from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from user.models import UserProfile


class PostUserTestCase(TestCase):
    client = Client()

    def setUp(self):
        pass

    def test_invalid_token(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "EAAEZAH2ttWo4BACPWqzJUxIyU1nrfyzv8JiZB7a3HJrDnqWDLRWofodYTN46rRS8PBZB4VxS469JPFTI3lNSXNJkGqA86QeKuZAuyygEfYNaostYWZA39Y8N0lKMrUMj2KKWJe01NbTGjxZB7cllZBg37FEfZBs20kBKDo5P5ozBgAZDZD",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], "10001")
        self.assertEqual(data["message"], "Invalid facebook token")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1423",
                "access_token": "EAAEZAH2ttWo4BACPWqzJUxIyU1nrfyzv8JiZB7a3HJrDnqWDLRWofodYTN46rRS8PBZB4VxS469JPFTI3lNSXNJkGqA86QeKuZAuyygEfYNaostYWZA39Y8N0lKMrUMj2KKWJe01NbTGjxZB7cllZBg37FEfZBs20kBKDo5P5ozBgAZDZD",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], "10001")
        self.assertEqual(data["message"], "Invalid facebook token")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

    def test_invalid_nickname(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "EAAEZAH2ttWo4BACPWqzJUxIyU2nrfyzv8JiZB7a3HJrDnqWDLRWofodYTN46rRS8PBZB4VxS469JPFTI3lNSXNJkGqA86QeKuZAuyygEfYNaostYWZA39Y8N0lKMrUMj2KKWJe01NbTGjxZB7cllZBg37FEfZBs20kBKDo5P5ozBgAZDZD",
                "nickname": "",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], "10002")
        self.assertEqual(data["message"], "Nickname duplicate")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "EAAEZAH2ttWo4BACPWqzJUxIyU2nrfyzv8JiZB7a3HJrDnqWDLRWofodYTN46rRS8PBZB4VxS469JPFTI3lNSXNJkGqA86QeKuZAuyygEfYNaostYWZA39Y8N0lKMrUMj2KKWJe01NbTGjxZB7cllZBg37FEfZBs20kBKDo5P5ozBgAZDZD",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["errorcode"], "10002")
        self.assertEqual(data["message"], "Nickname duplicate")

        user_count = User.objects.count()
        self.assertEqual(user_count, 0)

    def test_post(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "EAAEZAH2ttWo4BACPWqzJUxIyU2nrfyzv8JiZB7a3HJrDnqWDLRWofodYTN46rRS8PBZB4VxS469JPFTI3lNSXNJkGqA86QeKuZAuyygEfYNaostYWZA39Y8N0lKMrUMj2KKWJe01NbTGjxZB7cllZBg37FEfZBs20kBKDo5P5ozBgAZDZD",
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


class PutUserMeTestCase(TestCase):
    client = Client()
    token = ""

    def setUp(self):
        response = self.client.post(
            '/users/',
            json.dumps({
                "facebookid": "1367486803610262",
                "access_token": "EAAEZAH2ttWo4BACPWqzJUxIyU2nrfyzv8JiZB7a3HJrDnqWDLRWofodYTN46rRS8PBZB4VxS469JPFTI3lNSXNJkGqA86QeKuZAuyygEfYNaostYWZA39Y8N0lKMrUMj2KKWJe01NbTGjxZB7cllZBg37FEfZBs20kBKDo5P5ozBgAZDZD",
                "nickname": "seunghan",
            }),
            content_type='application/json'
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.token = data["access_token"]

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
