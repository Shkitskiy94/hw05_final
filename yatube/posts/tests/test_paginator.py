from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(0, 13):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый текст',
            )
        cls.paginate_dict = {
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
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_first_page_views(self):
        """views - На первой странице должно быть 10 постов"""
        for address, temp in self.paginate_dict.items():
            with self.subTest(temp=temp):
                danger_message = f'На странице {temp} не 10 постов'
                response = (self.authorized_client.get(address))
                self.assertEqual(len(response.context['page_obj']),
                                 10, danger_message)

    def test_second_page_views(self):
        """Views - На второй странице должно быть 3 поста"""
        for address, temp in self.paginate_dict.items():
            with self.subTest(temp=temp):
                danger_message = f'На странице {temp} не 3 постa'
                response = (self.authorized_client.get(address + '?page=2'))
                self.assertEqual(len(response.context['page_obj']),
                                 3, danger_message)
