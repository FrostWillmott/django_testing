# news/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # cls.note = Note.objects.create(title='Заголовок', text='Текст')
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # От имени одного пользователя создаём комментарий к новости:
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            # slug='slug',
            author=cls.author,
        )
        # print(cls.note.slug)

    def test_pages_availability(self):
        '''№1, 5 техзадания'''
        urls = (
            'notes:home',  # Техзадание 1
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages(self):
        '''№2 техзадания'''
        self.client.force_login(self.reader)
        urls = (
            'notes:list',  # Страница со списком заметок
            'notes:success',  # Страница успешного добавления заметки
            'notes:add',  # Страница добавления новой заметки
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        '''№3 техзадания'''
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete',
                         'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
                    # print(response.data)

    def test_redirect_for_anonymous_client(self):
        '''№4 техзадания'''
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')

        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        # # В цикле перебираем имена страниц, с которых ожидаем редирект:
        # for name in (
        #         'notes:edit', 'notes:delete', 'notes:add',
        #         'notes:success',
        #         'notes:list'):
        #     with self.subTest(name=name):
        #         # Получаем адрес страницы редактирования или удаления комментария:
        #         url = reverse(name, args=(self.note.slug,))
        #         # Получаем ожидаемый адрес страницы логина,
        #         # на который будет перенаправлен пользователь.
        #         # Учитываем, что в адресе будет параметр next, в котором передаётся
        #         # адрес страницы, с которой пользователь был переадресован.
        #         redirect_url = f'{login_url}?next={url}'
        #         response = self.client.get(url)
        #         # Проверяем, что редирект приведёт именно на указанную ссылку.
        #         self.assertRedirects(response, redirect_url)
        # for name in ():
        #     with self.subTest(name=name):
        #         url = reverse(name)
        #         redirect_url = f'{login_url}?next={url}'
        #         response = self.client.get(url)
        #         self.assertRedirects(response, redirect_url)
