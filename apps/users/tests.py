import json
from unittest.mock import patch

from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .models import CustomUser
from .views import firebase_login_view


class FirebaseLoginViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post_token(self, token):
        request = self.factory.post(
            '/users/login/firebase/',
            data=json.dumps({'idToken': token}),
            content_type='application/json',
        )
        request.session = SessionStore()
        return firebase_login_view(request), request

    @patch('users.views._firebase_admin_app', return_value=object())
    @patch('firebase_admin.auth.verify_id_token')
    def test_verified_campus_google_user_is_created_and_logged_in(self, verify_token, _admin_app):
        verify_token.return_value = {
            'uid': 'firebase-user-1',
            'email': 'student@pccoepune.org',
            'email_verified': True,
            'name': 'Campus Student',
        }

        response, request = self.post_token('firebase-id-token')

        self.assertEqual(response.status_code, 200)
        user = CustomUser.objects.get(email='student@pccoepune.org')
        self.assertEqual(user.role, CustomUser.Role.STUDENT)
        self.assertEqual(user.get_full_name(), 'Campus Student')
        self.assertFalse(user.has_usable_password())
        self.assertEqual(str(request.session['_auth_user_id']), str(user.pk))

    @patch('users.views._firebase_admin_app', return_value=object())
    @patch('firebase_admin.auth.verify_id_token')
    def test_unverified_or_non_campus_email_is_rejected(self, verify_token, _admin_app):
        rejected_claims = (
            {
                'uid': 'firebase-user-unverified',
                'email': 'student@pccoepune.org',
                'email_verified': False,
            },
            {
                'uid': 'firebase-user-non-campus',
                'email': 'person@gmail.com',
                'email_verified': True,
            },
        )
        for claims in rejected_claims:
            with self.subTest(email=claims['email']):
                verify_token.return_value = claims
                response, _ = self.post_token('firebase-id-token')
                self.assertEqual(response.status_code, 403)
        self.assertFalse(CustomUser.objects.exists())

    def test_missing_token_is_rejected(self):
        request = self.factory.post(
            '/users/login/firebase/',
            data='{}',
            content_type='application/json',
        )
        request.session = SessionStore()
        response = firebase_login_view(request)

        self.assertEqual(response.status_code, 400)


class DemoLoginViewTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username='demo.student',
            password='StudentDemo123!',
            role=CustomUser.Role.STUDENT,
            first_name='Demo',
        )

    @override_settings(DEBUG=True)
    def test_demo_login_uses_only_the_seeded_account_and_creates_session(self):
        response = self.client.post(
            reverse('users:demo_login', args=['student']),
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('react_app'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.student.pk)

    @override_settings(DEBUG=False)
    def test_demo_login_is_disabled_outside_development(self):
        response = self.client.post(reverse('users:demo_login', args=['student']))

        self.assertEqual(response.status_code, 404)
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(DEBUG=True)
    def test_demo_login_rejects_unknown_role(self):
        response = self.client.post(reverse('users:demo_login', args=['admin']))

        self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG=True)
    def test_demo_login_requires_post(self):
        response = self.client.get(reverse('users:demo_login', args=['student']))

        self.assertEqual(response.status_code, 405)
