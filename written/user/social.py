from urllib.request import urlopen

from django.core.files.base import ContentFile
from social.utils import slugify

USER_FIELDS = ['nickname']


def create_user(strategy, details, user=None, *args, **kwargs):
    print(details)
    print(kwargs)
    if user:
        return {'is_new': False}

    fields = {'nickname': details.get('username')}

    if not fields:
        return

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }


def update_avatar(backend, response, uid, user, *args, **kwargs):
    if backend.name == 'facebook':
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        avatar = urlopen(url)
        user.avatar.save(slugify(user.email + " social") + '.jpg', ContentFile(avatar.read()))
        user.save()
