from django.test import TestCase
from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='adminadmin')
        cls.author_for_subscription = User.objects.create(username='leo')
        cls.group = Group.objects.create(title='Авто')
        cls.post = Post.objects.create(
            text='Давай напишем еще один тест',
            author=cls.author,
            group=cls.group
        )

    def test_str_method_print_text_field(self):
        """__str__ method print first 15 characters of text field value."""
        post = PostModelTest.post
        expected_str_method_output = post.text[:15]
        self.assertEqual(expected_str_method_output, str(post))

    def test_check_length_str_method_output_is_15_chars(self):
        """__str__ method print exactly first 15
        characters of text field value.
        """
        post = PostModelTest.post
        length_value_str_method = len(str(post))
        self.assertEqual(length_value_str_method, 15)

    def test_expected_str_method_for_follow_object(self):
        """__str__ method print usernames of user and author"""
        follow = Follow.objects.create(
            user=PostModelTest.author,
            author=PostModelTest.author_for_subscription
        )
        expected_str_method_output = (
            f'Пользователь {follow.user.username}'
            f' подписан на автора {follow.author.username}'
        )
        self.assertEqual(expected_str_method_output, str(follow))

    def test_expected_str_method_for_comment_object(self):
        """__str__ method print comment text and post id"""
        comment = Comment.objects.create(
            text='коммент к посту',
            post=PostModelTest.post,
            author=PostModelTest.author
        )
        expected_str_method_output = (
            f'Комментарий "{comment.text[:10]}"'
            f' к посту номер {comment.post.id}'
        )
        self.assertEqual(expected_str_method_output, str(comment))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='SD-WAN',
            slug='sdwan',
            description='Группа по обсуждению новой концепции сетей WAN'
        )

    def test_expected_str_method_print_title_field(self):
        """__str__ method print value of title field."""
        group = GroupModelTest.group
        expected_str_method_output = group.title
        self.assertEqual(expected_str_method_output, str(group))
