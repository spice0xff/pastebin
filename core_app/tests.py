import datetime
from datetime import timezone

from django.test import TestCase, Client


class RegistrationTests(TestCase):
    def test_registration_success(self):
        from django.contrib.auth.models import User

        self.client = Client()
        self.client.post('/registration', {'username': 'test_user', 'password': 'test_user'})

        self.assertEqual(len(User.objects.all()), 1)

    def test_registration_user_already_exist(self):
        from django.contrib.auth.models import User

        self.client = Client()
        self.client.post('/registration', {'username': 'test_user', 'password': 'test_user'})

        self.assertEqual(len(User.objects.all()), 1)


class LoginTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        User.objects.create_user('test_user', 'test_user@localhost', 'test_user')

    def test_login_success(self):
        self.client = Client()
        self.client.post('/login', {'username': 'test_user', 'password': 'test_user'})

        response = self.client.get('/my_paste_list')
        self.assertEqual(response.status_code, 200)

    def test_login_fail(self):
        self.client = Client()
        self.client.post('/login', {'username': 'test_user', 'password': 'bad_password'})

        response = self.client.post('/my_paste_list')
        self.assertEqual(response.status_code, 302)


class PasteTests(TestCase):
    def test_access_time_not_out(self):
        from .models import Paste
        paste = Paste(
            text='test_text',
            access_time=datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=1)
        )
        paste.save()

        response = self.client.post('/paste/{}'.format(paste.hash))
        self.assertEqual(response.status_code, 200)

    def test_access_time_out(self):
        from .models import Paste
        paste = Paste(
            text='test_text',
            access_time=datetime.datetime.now(timezone.utc) - datetime.timedelta(minutes=1)
        )
        paste.save()

        paste_list = Paste.objects.all()
        print('paste_list: {}'.format(paste_list, ))
        paste = Paste.objects.get(id=1)
        print('paste.text: {}'.format(paste.text, ))

        response = self.client.post('/paste/{}'.format(paste.hash))
        self.assertEqual(response.status_code, 302)

    def test_access_to_private_success(self):
        from django.contrib.auth.models import User
        owner = User.objects.create_user('owner', 'owner@localhost', 'owner')

        from .models import Paste
        paste = Paste(
            text='test_text',
            access_time=datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=1),
            private=True,
            owner=owner,
        )
        paste.save()

        self.client.post('/login', {'username': 'owner', 'password': 'owner'})
        response = self.client.post('/paste/{}'.format(paste.hash))
        self.assertEqual(response.status_code, 200)

    def test_access_to_private_fail(self):
        from django.contrib.auth.models import User
        owner = User.objects.create_user('owner', 'owner@localhost', 'owner')

        from .models import Paste
        paste = Paste(
            text='test_text',
            access_time=datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=1),
            private=True,
            owner=owner,
        )
        paste.save()

        response = self.client.post('/paste/{}'.format(paste.hash))
        self.assertEqual(response.status_code, 302)
