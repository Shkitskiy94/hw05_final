import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post, Follow
from posts.forms import PostForm, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='TestUser')
        cls.another_user = User.objects.create_user(username='tiger')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded
        )
        cls.context_test = {
            reverse('posts:index'): 'Главная страница',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'Страница групп',
            reverse(
                'posts:profile',
                kwargs={'username': cls.post.author}
            ): 'Страница профиля',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): 'Страница деталей поста',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ): 'Страница создания поста',
        }
        cls.post_with_views = {
            reverse('posts:index'): 'Главная страница',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'Страница групп',
            reverse(
                'posts:profile',
                kwargs={'username': cls.post.author}
            ): 'Страница профиля',
        }
        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.post.author}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ),
            'posts/follow.html': reverse(
                'posts:follow_index'
            )
        }
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.quest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTest.post.author)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_for_guest(self):
        """URL-адрес не использует шаблон для
         не авторизованного пользователя"""
        response = self.quest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertTemplateNotUsed(response, 'posts/create_post.html')

    def test_all_views_page_show_correct_context(self):
        """Шаблоны views сформированы с правильным контекстом."""
        cache.clear()
        for address, temp in self.context_test.items():
            with self.subTest(temp=temp):
                danger_message = f'Шаблон {temp} сформирован не верно'
                response = (self.authorized_client.get(address))
                post = response.context['post']
                self.assertEqual(post.author, self.post.author, danger_message)
                self.assertEqual(post.text, self.post.text, danger_message)
                self.assertEqual(post.group, self.post.group, danger_message)
                self.assertEqual(post.image, self.post.image, danger_message)

    def test_post_with_group_index_show_correct_context(self):
        """Пост с группой есть на главной странице."""
        post_2 = Post.objects.create(
            author=self.user,
            text='Тестовый точно текст?',
            group=self.group,
            pub_date='2022-08-14 00:00:00',
        )
        for address, temp in self.post_with_views.items():
            with self.subTest(temp=temp):
                danger_message = f'Пост {temp} не найден на странице'
                response = (self.authorized_client.get(address))
                post = response.context['page_obj'][0]
                self.assertEqual(post.pk, post_2.pk, danger_message)

    def test_authorized_client_can_comment(self):
        """Авторизованный пользователь может комментировать посты."""
        comments_initial = Comment.objects.count()
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data={'text': 'Комментарий для поста 2'}
        )
        comments_finally = Comment.objects.count()
        comments_text = Comment.objects.all()[0].text
        self.assertEqual(comments_initial + 1, comments_finally)
        self.assertEqual('Комментарий для поста 2', comments_text)

    def test_guest_client_cant_comment(self):
        """Неавторизованный пользователь не может комментировать посты."""
        comments_initial = Comment.objects.count()
        self.quest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data={'text': 'Комментарий для поста 1'}
        )
        comments_finally = Comment.objects.count()
        self.assertNotEqual(comments_initial + 1, comments_finally)

    def test_comment_in_page_detail(self):
        """После успешной отправки комментарий появляется на странице поста."""
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data={'text': 'Комментарий для поста 2'}
        )
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        comments_text = response.context['comments'][0].text
        self.assertEqual('Комментарий для поста 2', comments_text)

    def test_cache_home_page(self):
        """Проверка работы кеша главной страницы."""
        cache.clear()
        post_del_cache = Post.objects.create(
            text='Текст для проверки',
            author=self.user,
        )

        def response():
            return self.quest_client.get(reverse('posts:index'))

        response_primary = response().content
        post_del_cache.delete()
        response_secondary = response().content
        self.assertEqual(response_primary, response_secondary)
        cache.clear()
        response_cache_clear = response().content
        self.assertNotEqual(response_secondary, response_cache_clear)

    def test_create_follow_authorized(self):
        """Тест создания подписок авторизованным пользователем."""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.another_user.username}
                    )
        )
        self.assertTrue(Follow.objects.filter(author=self.another_user,
                                              user=self.user))

    def test_create_follow_non_authorized(self):
        """Тест создания подписок неавторизованным пользователем."""
        self.quest_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.another_user.username}
                    )
        )
        self.assertFalse(Follow.objects.filter(author=self.another_user,
                                               user=self.user))

    def test_create_follow_author(self):
        """Тест автор подписки не может подписаться сам на себя."""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}
                    )
        )
        self.assertFalse(Follow.objects.filter(author=self.user,
                                               user=self.user))

    def test_delete_follow_authorized(self):
        """Тест удаления подписок авторизованным пользователем."""
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.another_user.username}
                    )
        )
        self.assertFalse(Follow.objects.filter(author=self.another_user,
                                               user=self.user))

    def test_new_post(self):
        """Тест новой записи пользователя появляется в ленте подписавшихся."""
        me = User.objects.create(username='me')
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': me.username}
                    )
        )
        new_post = Post.objects.create(author=me, text='Test 1')
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(new_post, response.context['page_obj'][0])
        response = self.another_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)
