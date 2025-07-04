from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты проверяют корректность открытия и доступа к страницам."""

    @classmethod
    def setUpTestData(cls):
        """Создаём пользователей и заметку."""
        cls.author = User.objects.create(username="Лев Толстой")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель простой")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title="Заголовок",
            text="Текст",
            author=cls.author,
        )

    def test_pages_availability(self):
        """Проверяем доступность страниц для анонимного пользователя"""
        get_urls = (
            "notes:home",
            "users:login",
            "users:signup",
        )

        for name in get_urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                ), f"Страница {name} недоступна"

        post_urls = ("users:logout",)
        for name in post_urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.post(url)
                (
                    self.assertEqual(response.status_code, HTTPStatus.OK),
                    f"Страница {name} недоступна",
                )

    def test_authenticated_user_pages(self):
        """
        Проверяем доступность страниц
        для аутентифицированного пользователя
        """
        urls = (
            "notes:list",
            "notes:success",
            "notes:add",
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.reader_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                ), f"Страница {name} недоступна"

    def test_availability_for_comment_edit_and_delete(self):
        """
        Проверяем доступность страниц для редактирования
        и удаления комментария автором и читателем заметок
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in ("notes:edit", "notes:delete", "notes:detail"):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status),
                    f"Страница {name} недоступна"

    def test_redirect_for_anonymous_client(self):
        """Проверяем редирект анонимного пользователя на страницу логина"""
        login_url = reverse("users:login")

        urls = (
            ("notes:list", None),
            ("notes:add", None),
            ("notes:success", None),
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url), (
                    f"Анонимный пользователь не перенаправлен"
                    f" на страницу логина со страницы {name}"
                )
