import requests
from rest_framework import status


def check_token(data):
    access_token = data.get('access_token')
    facebookid = data.get('facebookid')
    if not access_token or not facebookid:
        return False
    url = f"https://graph.facebook.com/v7.0/me?access_token={access_token}"
    response = requests.get(url)
    if response.status_code != status.HTTP_200_OK:
        return False
    response_data = response.json()
    if response_data["id"] != facebookid:
        return False
    data["username"] = facebookid
    return True


def mocked_check_token(data):
    access_token = data.get('access_token')
    facebookid = data.get('facebookid')
    if not access_token or not facebookid:
        return False
    if access_token != facebookid:
        return False
    data["username"] = facebookid
    return True
