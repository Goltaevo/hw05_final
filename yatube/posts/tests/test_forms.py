import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

SLUG: str = 'sdwan'
USERNAME: str = 'adminadmin'
CREATE_POST_PAGE: str = reverse('posts:post_create')
PROFILE_PAGE: str = f'/profile/{USERNAME}/'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
IMAGE_FOR_NEW_POST = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='SD-WAN',
            slug=SLUG,
            description='Группа по обсуждению новой концепции сетей WAN'
        )
        bulk_posts_list = []
        for i in range(15):
            bulk_posts_list.append(Post(
                text=f'sdwan тест для автотестов номер {i}',
                author=cls.user,
                group=cls.group,)
            )
        cls.bulk_posts = Post.objects.bulk_create(bulk_posts_list)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.POST_ID = len(PostCreateFormTest.bulk_posts)
        self.POST_PAGE: str = f'/posts/{self.POST_ID}/'
        self.EDIT_POST_PAGE: str = f'/posts/{self.POST_ID}/edit/'
        self.COMMENT_POST_PAGE: str = f'/posts/{self.POST_ID}/comment/'
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTest.user)

    def test_create_post_form(self):
        """Новый пост с картинкой создается успешно на странице /create/
        и пользователь перенаправляется
        на страницу своего профайла.
        """
        posts_count_before_new_post = Post.objects.count()
        uploaded_image = SimpleUploadedFile(
            name='test.jpg',
            content=IMAGE_FOR_NEW_POST,
            content_type='image/jpg'
        )
        form = {
            'text': 'дополнительный sdwan тест для автотестов',
            'group.title': 'SD-WAN',
            'image': uploaded_image,
        }
        response = self.authorized_client.post(
            CREATE_POST_PAGE,
            data=form,
            follow=True
        )
        posts_count_after_new_post = Post.objects.count()
        self.assertRedirects(response, PROFILE_PAGE)
        # Проверяем, что число записей в БД увеличилось на единицу
        self.assertEqual(
            posts_count_after_new_post,
            posts_count_before_new_post + 1
        )
        # Проверяем, что в БД создалась запись с заданными текстом и картинкой
        self.assertTrue(
            Post.objects.filter(
                text='дополнительный sdwan тест для автотестов',
                image='posts/test.jpg',
            ).exists()
        )

    def test_edit_post_form(self):
        """При отправке формы отредактированного поста
        на странице /posts/<post_id>/edit/ происходит изменение поста
        с указанным post_id в БД. Кол-во постов не изменяется.
        Пользователь при этом перенаправляется на страницу /posts/<post_id>/.
        """
        posts_count_before_edit = Post.objects.count()
        text_post_before_edit = Post.objects.get(id=self.POST_ID).text
        form_data_for_new_post = {
            'text': 'изменили текст поста',
            'group.title': 'SD-WAN',
        }
        response = self.authorized_client.post(
            self.EDIT_POST_PAGE,
            form_data_for_new_post,
            follow=True
        )
        self.assertRedirects(
            response,
            self.POST_PAGE
        )
        # После отправки формы с отредактированным текстом
        # повторно запрашиваем пост из БД
        text_post_after_edit = Post.objects.get(id=self.POST_ID).text
        # Проверяем, что текст отредактированного поста
        # действительно был изменен и сохранён в БД
        self.assertNotEqual(text_post_before_edit, text_post_after_edit)
        # Проверяем, что изменённый текст поста соответствуют тому,
        # который внесли при редактировании в форме
        self.assertEqual(text_post_after_edit, form_data_for_new_post['text'])
        # Проверяем, что число постов в БД после
        # редактирования поста не изменилось
        posts_count_after_edit = Post.objects.count()
        self.assertEqual(posts_count_after_edit, posts_count_before_edit)

    def test_comment_post_form_only_authorized_user(self):
        """Комментировать пост может только авторизованный пользователь.
        После отправки комментария пользователь
        перенаправляется на обратно на страницу поста.
        После успешной отправки комментария, он
        появляется на странице поста.
        """
        # Добавляем комментарий к посту
        form = {
            'text': 'комментарий для автотестов',
        }
        response = self.authorized_client.post(
            self.COMMENT_POST_PAGE,
            data=form,
            follow=True
        )
        # Перезапрашиваем страницу поста
        response = self.authorized_client.get(self.POST_PAGE)
        # Проверяем, что комменатрий присутствует на странице поста
        self.assertTrue(
            response.context['comments'].filter(
                text='комментарий для автотестов'
            ).exists()
        )
