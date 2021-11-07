# posts/tests/test_urls.py
from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import Group, Post, User

SLUG: str = 'sdwan'
USERNAME_1: str = 'adminadmin'
USERNAME_2: str = 'anotheradmin'
HOME_PAGE: str = '/'
CREATE_POST_PAGE: str = '/create/'
GROUP_LIST_PAGE: str = f'/group/{SLUG}/'
PROFILE_PAGE: str = f'/profile/{USERNAME_1}/'
GUEST_USER_REDIRECT_FROM_CREATE_POST_PAGE: str = '/auth/login/?next=/create/'


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME_1)
        cls.another_user = User.objects.create(username=USERNAME_2)
        cls.group = Group.objects.create(
            title='SD-WAN',
            slug=SLUG,
            description='Группа по обсуждению новой концепции сетей WAN'
        )
        cls.post = Post.objects.create(
            text='Давай напишем еще один тест',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.POST_ID = PostsPagesTest.post.id
        self.GUEST_USER_REDIRECT_FROM_EDIT_POST_PAGE: str = (
            f'/auth/login/?next=/posts/{self.POST_ID}/edit/'
        )
        self.POST_PAGE = f'/posts/{self.POST_ID}/'
        self.EDIT_POST_PAGE = f'/posts/{self.POST_ID}/edit/'
        self.guest_client = Client()
        self.authorized_author_client = Client()
        self.authorized_another_client = Client()
        self.authorized_author_client.force_login(PostsPagesTest.user)
        self.authorized_another_client.force_login(PostsPagesTest.another_user)

        self.any_user_urls = [
            HOME_PAGE,
            GROUP_LIST_PAGE,
            PROFILE_PAGE,
            self.POST_PAGE,
        ]
        self.authorized_user_urls = [
            self.EDIT_POST_PAGE,
            CREATE_POST_PAGE,
        ]
        self.guest_user_redirect_urls = {
            self.EDIT_POST_PAGE: self.GUEST_USER_REDIRECT_FROM_EDIT_POST_PAGE,
            CREATE_POST_PAGE: GUEST_USER_REDIRECT_FROM_CREATE_POST_PAGE,
        }

    def test_urls_exists_at_desired_location(self):
        """Проверяем, что страницы из списка any_user_urls
        доступны любому пользователя.
        """
        for url in self.any_user_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_create_post_url_availale_for_correct_user(self):
        """Страница /posts/<post_id>/edit/ доступна только автору поста.
        Страница /create/ доступна только авторизованному пользователю.
        """
        for url in self.authorized_user_urls:
            with self.subTest(url=url):
                if url == self.EDIT_POST_PAGE:
                    response = self.authorized_author_client.get(url)
                else:
                    response = self.authorized_another_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url(self):
        """Несуществующая Страница /unexisting_page/
        доступна всем с кодом 404.
        """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_post_url_redirect_non_author(self):
        """Страница /posts/<post_id>/edit/ перенаправляет
        не автора поста на страницу поста.
        """
        response = self.authorized_another_client.get(
            self.EDIT_POST_PAGE, follow=True)
        self.assertRedirects(response, self.POST_PAGE)

    def test_edit_create_post_urls_redirect_anonymous(self):
        """Страница /posts/<post_id>/edit/ перенаправляет
        анонимного пользователя на страницу авторизации.
        Страница /create/ перенаправляет
        анонимного пользователя на страницу авторизации.
        """
        for url, redirect_url in self.guest_user_redirect_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            HOME_PAGE: 'posts/index.html',
            GROUP_LIST_PAGE: 'posts/group_list.html',
            PROFILE_PAGE: 'posts/profile.html',
            self.POST_PAGE: 'posts/post_detail.html',
            self.EDIT_POST_PAGE: 'posts/create_post.html',
            CREATE_POST_PAGE: 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_author_client.get(url)
                self.assertTemplateUsed(response, template)
