# news/tests/test_routes.py
from http import HTTPStatus

from django.urls import reverse

import pytest

from pytest_django.asserts import assertRedirects


# class TestRoutes(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(title='Заголовок', text='Текст')
#         # Создаём двух пользователей с разными именами:
#         cls.author = User.objects.create(username='Лев Толстой')
#         cls.reader = User.objects.create(username='Читатель простой')
#         # От имени одного пользователя создаём комментарий к новости:
#         cls.comment = Comment.objects.create(
#             news=cls.news,
#             author=cls.author,
#             text='Текст комментария'
#         )

# def test_pages_availability(self):
#     urls = (
#         ('news:home', None),
#         ('news:detail', (self.news.id,)),
#         ('users:login', None),
#         ('users:logout', None),
#         ('users:signup', None),
#     )
#     for name, args in urls:
#         with self.subTest(name=name):
#             url = reverse(name, args=args)
#             response = self.client.get(url)
#             self.assertEqual(response.status_code, HTTPStatus.OK)
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('id_for_args')),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
    )
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name,
                                               args):
    url = reverse(name, args=args)

    # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# def test_availability_for_comment_edit_and_delete(self):
#     users_statuses = (
#         (self.author, HTTPStatus.OK),
#         (self.reader, HTTPStatus.NOT_FOUND),
#     )
#     for user, status in users_statuses:
#         # Логиним пользователя в клиенте:
#         self.client.force_login(user)
#         # Для каждой пары "пользователь - ожидаемый ответ"
#         # перебираем имена тестируемых страниц:
#         for name in ('news:edit', 'news:delete'):
#             with self.subTest(user=user, name=name):
#                 url = reverse(name, args=(self.comment.id,))
#                 response = self.client.get(url)
#                 self.assertEqual(response.status_code, status)

@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
            (
                    pytest.lazy_fixture('not_author_client'),
                    HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
            ('news:edit', pytest.lazy_fixture('id_post_for_args')),
            ('news:delete', pytest.lazy_fixture('id_post_for_args')),
    )
)
def test_pages_availability_for_different_users(parametrized_client,
                                                expected_status, name,
                                                args, db):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# def test_redirect_for_anonymous_client(self):
#     # Сохраняем адрес страницы логина:
#     login_url = reverse('users:login')
#     # В цикле перебираем имена страниц, с которых ожидаем редирект:
#     for name in ('news:edit', 'news:delete'):
#         with self.subTest(name=name):
#             # Получаем адрес страницы редактирования или удаления комментария:
#             url = reverse(name, args=(self.comment.id,))
#             # Получаем ожидаемый адрес страницы логина,
#             # на который будет перенаправлен пользователь.
#             # Учитываем, что в адресе будет параметр next, в котором передаётся
#             # адрес страницы, с которой пользователь был переадресован.
#             redirect_url = f'{login_url}?next={url}'
#             response = self.client.get(url)
#             # Проверяем, что редирект приведёт именно на указанную ссылку.
#             self.assertRedirects(response, redirect_url)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
            ('news:edit', pytest.lazy_fixture('id_post_for_args')),
            ('news:delete', pytest.lazy_fixture('id_post_for_args')),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args, db):
    login_url = reverse('users:login')
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
