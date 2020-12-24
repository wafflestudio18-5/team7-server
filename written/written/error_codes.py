# 10000 : Users
from rest_framework.response import Response

invalidFacebookToken = {
    "errorcode": "10001",
    "message": "Invalid facebook token"
}
nicknameDuplicate = {
    "errorcode": "10002",
    "message": "Nickname duplicate"
}
userDoesNotExist = {
    "errorcode": "10003",
    "message": "User does not exist"
}
userNotAuthorized = {
    "errorcode": "10004",
    "message": "User is not authorized"
}

# 20000 Postings
titleDoesNotExist = {
    "errorcode": "20002",
    "message": "Title does not exist"
}
postingDoesNotExist = {
    "errorcode": "20003",
    "message": "Posting does not exist"
}
contentIsEmpty = {
    "errorcode": "20004",
    "message": "Content is empty"
}
titlenameIsEmpty = {
    "errorcode": "20005",
    "message": "Title name is empty"
}

# 30000 Subscriptions
alreadySubscribed = {
    "errorcode": "30001",
    "message": "User is already subscribed",
}

alreadyUnsubscribed = {
    "errorcode": "30002",
    "message": "User is not subscribed",
}

# 40000 Scraps
alreadyScrapped = {
    "errorcode": "40001",
    "message": "Posting is already scrapped",
}

alreadyUnscrapped = {
    "errorcode": "40002",
    "message": "Posting is not scrapped",
}
