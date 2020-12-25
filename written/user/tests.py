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
        print(data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
