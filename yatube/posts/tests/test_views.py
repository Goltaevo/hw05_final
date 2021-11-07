from django import forms
from django.conf import settings
from django.core.cache import cache
from django.db.models import fields
from django.test import Client, TestCase
from posts.models import Group, Post, User

PAGES = [1, 2]
SLUG_GROUP_ONE: str = 'sdwan'
SLUG_GROUP_TWO: str = 'nfvo'
USERNAME: str = 'adminadmin'
USERNAME_TWO: str = 'leo'
HOME_PAGE: str = '/'
CREATE_POST_PAGE: str = '/create/'
GROUP_ONE_LIST_PAGE: str = f'/group/{SLUG_GROUP_ONE}/'
GROUP_TWO_LIST_PAGE: str = f'/group/{SLUG_GROUP_TWO}/'
PROFILE_PAGE: str = f'/profile/{USERNAME}/'
CUSTOM_404_ERROR_PAGE: str = '/WTF/'
FOLLOW_PAGE: str = '/follow/'
PROFILE_FOLLOW_PAGE: str = f'/profile/{USERNAME_TWO}/follow/'
PROFILE_UNFOLLOW_PAGE: str = f'/profile/{USERNAME_TWO}/unfollow/'


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='adminadmin')
        cls.user_two = User.objects.create(username='leo')
        cls.user_three = User.objects.create(username='jsmith')
        cls.group_one = Group.objects.create(
            title='SD-WAN',
            slug=SLUG_GROUP_ONE,
            description='Группа по обсуждению новой концепции сетей WAN'
        )
        cls.group_two = Group.objects.create(
            title='NFVO',
            slug=SLUG_GROUP_TWO,
            description='Группа по выбору ресурсного оркестратора'
        )
        bulk_posts_list_group_one = []
        for i in range(15):
            bulk_posts_list_group_one.append(Post(
                text=f'sdwan тест для автотестов номер {i}',
                author=cls.user,
                group=cls.group_one)
            )
        cls.bulk_posts_group_one = Post.objects.bulk_create(
            bulk_posts_list_group_one
        )
        bulk_posts_list_group_two = []
        for i in range(13):
            bulk_posts_list_group_two.append(Post(
                text=f'nfvo тест для автотестов номер {i}',
                author=cls.user,
                group=cls.group_two)
            )
        cls.bulk_posts_group_two = Post.objects.bulk_create(
            bulk_posts_list_group_two
        )

    def setUp(self):
        self.POST_ID_GROUP_ONE = len(PostsPagesTest.bulk_posts_group_one)
        self.TOTAL_NUMBER_OF_POSTS = Post.objects.count()
        self.LAST_POST_GROUP_ONE = Post.objects.get(id=self.POST_ID_GROUP_ONE)
        self.POST_PAGE = f'/posts/{self.POST_ID_GROUP_ONE}/'
        self.EDIT_POST_PAGE = f'/posts/{self.POST_ID_GROUP_ONE}/edit/'
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTest.user)
        self.authorized_client_user_two = Client()
        self.authorized_client_user_two.force_login(PostsPagesTest.user_two)
        self.authorized_client_user_three = Client()
        self.authorized_client_user_three.force_login(
            PostsPagesTest.user_three
        )
        self.urls = [
            HOME_PAGE,
            GROUP_ONE_LIST_PAGE,
            PROFILE_PAGE,
        ]

    def test_first_pages_contains_ten_posts(self):
        """Проверяем, что 1-ы страницы списка urls
        содержат по 10 постов.
        """
        for url in self.urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_PER_PAGE
                )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            HOME_PAGE: 'posts/index.html',
            CREATE_POST_PAGE: 'posts/create_post.html',
            GROUP_ONE_LIST_PAGE: 'posts/group_list.html',
            PROFILE_PAGE: 'posts/profile.html',
            self.POST_PAGE: 'posts/post_detail.html',
            self.EDIT_POST_PAGE: 'posts/create_post.html',
            CUSTOM_404_ERROR_PAGE: 'core/404.html'
        }
        for url, template in templates_pages_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_third_home_page_contains_five_posts(self):
        """3-я страница домашней страницы posts:index
        должна содержать только 8 постов.
        """
        response = self.authorized_client.get(HOME_PAGE + '?page=3')
        self.assertEqual(len(response.context['page_obj']), 8)

    def test_first_group_page_show_correct_posts(self):
        """1-я страница группы posts:group_list
        содержит список постов этой группы.
        """
        response = self.authorized_client.get(GROUP_ONE_LIST_PAGE)
        for post in response.context['page_obj']:
            with self.subTest(post=post):
                self.assertEqual(
                    post.group.slug,
                    SLUG_GROUP_ONE
                )

    def test_second_group_page_contains_five_posts(self):
        """2-я страница группы posts:group_list
        содержит только 5 постов.
        """
        response = self.authorized_client.get(GROUP_ONE_LIST_PAGE + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_page_show_correct_posts(self):
        """Профиль автора posts:profile
        содержит список постов этого автора.
        """
        response = self.authorized_client.get(PROFILE_PAGE)
        for post in response.context['page_obj']:
            with self.subTest(post=post):
                self.assertEqual(post.author.username, USERNAME)

    def test_post_detail_page_show_correct_post(self):
        """Страница поста показывает пост
        c корректными id, текстом и группой.
        """
        response = self.authorized_client.get(
            f'/posts/{len(PostsPagesTest.bulk_posts_group_one)}/'
        )
        self.assertEqual(
            response.context['post'].id, self.POST_ID_GROUP_ONE
        )
        self.assertEqual(
            response.context['post'].text,
            self.LAST_POST_GROUP_ONE.text
        )
        self.assertEqual(
            response.context['post'].group.title,
            self.LAST_POST_GROUP_ONE.group.title
        )

    def test_create_edit_post_pages_show_correct_context(self):
        """Формы создания и редактирования поста c id=10
        сформированы с правильным контекстом.
        """
        pages = [
            '/create/',
            f'/posts/{len(PostsPagesTest.bulk_posts_group_one)}/edit/',
        ]
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for url in pages:
            response = self.authorized_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_edit_post_pages_show_correct_post(self):
        """Форма редактирования поста
        отображает данные именно запрошенного поста.
        """
        response = self.authorized_client.get(self.EDIT_POST_PAGE)
        self.assertEqual(
            response.context.get('form').instance.text,
            self.LAST_POST_GROUP_ONE.text
        )
        self.assertEqual(
            response.context.get('form').instance.group.title,
            self.LAST_POST_GROUP_ONE.group.title
        )

    def test_post_exist_on_pages(self):
        """Созданный пост присутствует на домашней странице,
        в профайле пользователя 'adminadmin'
        и на странице выбранной группы 'SD-WAN'.
        Пользователь 'adminadmin' создал всего 28 постов в 2х группах.
        """
        for url in self.urls:
            with self.subTest(url=url):
                if url == GROUP_ONE_LIST_PAGE:
                    response = self.authorized_client.get(url)
                    first_post_on_page = response.context['page_obj'][0]
                    first_post_on_page_id = first_post_on_page.id
                    self.assertEqual(
                        first_post_on_page_id,
                        self.POST_ID_GROUP_ONE
                    )
                else:
                    response = self.authorized_client.get(url)
                    first_post_on_page = response.context['page_obj'][0]
                    first_post_on_page_id = first_post_on_page.id
                    self.assertEqual(
                        first_post_on_page_id,
                        self.TOTAL_NUMBER_OF_POSTS
                    )

    def test_post_not_exist_in_wrong_group_page(self):
        """Созданный пост с групппой ONE
        отсутствует на странице группы TWO."""
        for page in PAGES:
            response = self.authorized_client.get(
                GROUP_TWO_LIST_PAGE
                + f'?page={page}'
            )
            posts_on_page = response.context['page_obj']
            for post in posts_on_page:
                with self.subTest(post=post):
                    self.assertNotEqual(post.id, self.POST_ID_GROUP_ONE)

    def test_post_image_exist_in_context(self):
        """При выводе поста с картинкой изображение
        передается в словера CONTEXT:
         - на главную страницу,
         - на траницу профайла,
         - на страницу группы,
         - отдельную страницу поста.
        """
        urls = [
            HOME_PAGE,
            GROUP_ONE_LIST_PAGE,
            PROFILE_PAGE,
            self.POST_PAGE,
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            if url == self.POST_PAGE:
                # Берем пост из контекста
                post = response.context['post']
                # Проверяем, что пост содержит поле image,
                # являющееся объектом класса ImageFieldFile
                self.assertIsInstance(post.image, fields.files.ImageFieldFile)
            else:
                # Берем первый пост на странице
                post_0 = response.context['page_obj'][0]
                # Проверяем, что пост содержит поле image,
                # являющееся объектом класса ImageFieldFile
                self.assertIsInstance(
                    post_0.image,
                    fields.files.ImageFieldFile
                )

    def test_cache_of_posts_on_home_page(self):
        """Проверяем, что посты на главной странице
        кэшируются на 20 секунд.
        """
        # Запрашиваю главную страницу
        # и фиксирую ее контент
        response = self.guest_client.get(HOME_PAGE)
        cached_first_post_on_page = response.content
        # Создаём новый пост и снова запрашиваем главную страницу
        # проверяем, остался ли контент страницы прежним из-за кэша
        Post.objects.create(
            text='Свежий пост для тестирования кэша',
            author=PostsPagesTest.user,
            group=PostsPagesTest.group_one
        )
        response = self.guest_client.get(HOME_PAGE)
        self.assertEqual(cached_first_post_on_page, response.content)
        # Чтобы не ждать 20 секунд (время протухания кэша)
        # очищаем кэш и проверям, что контент на главной странице изменился
        cache.clear()
        response = self.guest_client.get(HOME_PAGE)
        self.assertNotEqual(cached_first_post_on_page, response.content)

    def test_user_can_follow_author(self):
        """Проверяем, что авторизованный пользователь
        может подписаться на другого пользователя
        и может отписаться от другого пользователя.
        """
        # Проверяем число подписок пользователя сначала
        number_of_follows_before = PostsPagesTest.user.follower.count()
        # Подписываемся на второго пользователя
        self.authorized_client.get(PROFILE_FOLLOW_PAGE)
        # Проверяем, что число подписок изменилось
        number_of_follows_after_subsc = PostsPagesTest.user.follower.count()
        self.assertNotEqual(
            number_of_follows_before,
            number_of_follows_after_subsc,
        )
        # Отписываемся от второго пользователя
        self.authorized_client.get(PROFILE_UNFOLLOW_PAGE)
        # Проверяем число подписок пользователя после отписки
        number_of_follows_after_unsubsc = PostsPagesTest.user.follower.count()
        # Проверяем, что число подписок стало прежним
        self.assertEqual(
            number_of_follows_after_unsubsc,
            number_of_follows_before,
        )

    def test_only_follower_can_see_post_on_follow_page(self):
        """Новая запись автора появляется
        в ленте у подписанного не него пользователя
        и не появляется у неподписавшегося
        на него пользователя.
        """
        # Подписываем первого пользователя на второго
        self.authorized_client.get(PROFILE_FOLLOW_PAGE)
        # Второй пользователь создает пост
        post = Post.objects.create(
            text='Пост второго пользователя',
            author=PostsPagesTest.user_two,
            group=PostsPagesTest.group_one
        )
        # Проверяем, что у первого пользователя на странице follow
        # появился пост второго пользователя
        response = self.authorized_client.get(FOLLOW_PAGE)
        self.assertIn(post, response.context['page_obj'].object_list)
        # Проверяем, что у третьего пользователя на странице follow
        # пост второго пользователя НЕ появился
        response = self.authorized_client_user_three.get(FOLLOW_PAGE)
        self.assertNotIn(post, response.context['page_obj'].object_list)
        # Для завершения теста отписываем первого пользователя от второго
        self.authorized_client.get(PROFILE_UNFOLLOW_PAGE)
