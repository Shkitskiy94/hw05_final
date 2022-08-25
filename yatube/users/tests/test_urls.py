from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class ContactURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаем юзера"""
        cls.user = User.objects.create_user(
            username='auth',
            email='test@yandex.ru',
            password='test_pass'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.quest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(ContactURLTests.user)

    def test_login(self):
        """Cтраница '/auth/login/' доступна любому пользователю."""
        response = self.quest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup(self):
        """Cтраница '/auth/signup/' доступна любому пользователю."""
        response = self.quest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset(self):
        """Cтраница '/auth/password_reset/' доступна любому пользователю."""
        response = self.quest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done(self):
        """Cтраница '/auth/password_reset/done/'
        доступна любому пользователю."""
        response = self.quest_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change(self):
        """
        Cтраница '/auth/password_change/'
        доступна авторизованному пользователю.
        """
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done(self):
        """
        Cтраница '/auth/password_change/done/'
        доступна авторизованному пользователю.
        """
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset(self):
        """
        Cтраница '/auth/reset/<uidb64>/<token>/'
        доступна авторизованному пользователю.
        """
        response = self.authorized_client.get('/auth/reset/<uidb64>/<token>/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_complete(self):
        """
        Cтраница '/auth/password_reset/complete/'
        доступна авторизованному пользователю.
        """
        response = self.authorized_client.get('/auth/password_reset/complete/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout(self):
        """Cтраница '/auth/logout/' доступна любому пользователю."""
        response = self.quest_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting(self):
        """Несуществующая страница выдаёт код 404"""
        response = self.quest_client.get('/auth/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/password_reset/complete/':
            'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
