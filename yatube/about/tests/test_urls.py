from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls = [
            '/about/author/',
            '/about/tech/',
        ]

    def test_about_pages_are_available(self):
        """Проверяем, что страницы из списка urls
        доступны любому пользователя.
        """
        for url in self.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
