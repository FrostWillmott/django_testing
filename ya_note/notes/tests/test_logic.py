from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotesCreation(TestCase):
    """Тесты проверяют создание заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создаём пользователя, автора заметки и заметку."""
        cls.user = User.objects.create(username="Мимо Крокодил")
        cls.author = User.objects.create(username="Лев Толстой")
        cls.note = Note.objects.create(
            title="Заголовок",
            text="Текст",
            slug="slug",
            author=cls.author,
        )
        cls.note_add_url = reverse("notes:add")
        cls.anonym_user_redir_url = (
            f'{reverse("users:login")}?next={cls.note_add_url}'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            "title": "Новая заметка",
            "text": "Новый текст",
            "slug": "newslug",
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяем, что анонимный пользователь не может создать заметку."""
        note_count_before = Note.objects.count()
        response = self.client.post(self.note_add_url, data=self.form_data)
        (
            self.assertRedirects(response, self.anonym_user_redir_url),
            "Анонимный пользователь не перенаправляться на страницу логина",
        )

        note_count = Note.objects.count()
        self.assertEqual(note_count, note_count_before), "Заметка создана"

    def test_authenticated_user_can_create_note(self):
        """
        Проверяем, что аутентифицированный пользователь
        может создать заметку.
        """
        note_count_before = Note.objects.count()
        response = self.auth_client.post(
            self.note_add_url, data=self.form_data
        )
        self.assertRedirects(
            response, reverse("notes:success")
        ), "Страница успешного выполнения операции не открыта"
        note_count = Note.objects.count()
        self.assertEqual(note_count, (note_count_before + 1)), (
            "Заметка" " не создана"
        )
        new_note = Note.objects.latest("id")
        self.assertEqual(new_note.author, self.user)
        self.assertEqual(
            new_note.title, self.form_data["title"]
        ), "Заголовок новой заметки не совпадает с формой"
        self.assertEqual(
            new_note.text, self.form_data["text"]
        ), "Текст новой заметки не совпадает с формой"
        self.assertEqual(
            new_note.slug, self.form_data["slug"]
        ), "Slug новой заметки не совпадает с формой"

    def test_cannot_create_note_with_duplicate_slug(self):
        """Проверяем, что нельзя создать заметку с дублирующимся slug."""
        note_count_before = Note.objects.count()
        self.form_data["slug"] = self.note.slug
        response = self.auth_client.post(
            self.note_add_url, data=self.form_data
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK
        ), "Запрос не вернул код 200"
        note_count = Note.objects.count()
        self.assertEqual(note_count, note_count_before), "Заметка создана"
        self.assertFormError(
            response, "form", "slug", "slug" + WARNING
        ), "Сообщение об ошибке не соответствует ожидаемому"

    def test_slug_is_generated_if_not_provided(self):
        """Проверяем, что slug генерируется, если не указан в форме."""
        self.form_data.pop("slug")
        response = self.auth_client.post(
            self.note_add_url, data=self.form_data
        )
        self.assertEqual(
            response.status_code, HTTPStatus.FOUND
        ), "Запрос не вернул код 302"
        note = Note.objects.latest("id")
        self.assertEqual(
            note.slug, slugify(self.form_data["title"])
        ), "Slug не сгенерирован"


class TestNoteEditDelete(TestCase):
    """Тесты проверяют редактирование и удаление заметок."""

    NOTE_TEXT = "Текст заметки"
    NEW_NOTE_TEXT = "Обновлённая заметка"
    NOTE_TITLE = "Новый заголовок"
    NEW_NOTE_TITLE = "Обновлённый заголовок"
    NOTE_SLUG = "slug"
    NEW_NOTE_SLUG = "new-slug"

    @classmethod
    def setUpTestData(cls):
        """Создаём автора, читателя, заметку и форму."""
        cls.author = User.objects.create(username="Автор заметки")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.NOTE_SLUG,
        )
        cls.success_url = reverse("notes:success")
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))
        cls.form_data = {
            "title": cls.NEW_NOTE_TITLE,
            "text": cls.NEW_NOTE_TEXT,
            "slug": cls.NEW_NOTE_SLUG,
        }

    def test_author_can_edit_own_note(self):
        """Проверяем, что автор может отредактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(
            response, self.success_url
        ), "Страница успешного выполнения операции не открыта"
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text, self.form_data["text"]
        ), "Текст заметки не обновлён"
        self.assertEqual(
            self.note.title, self.form_data["title"]
        ), "Заголовок заметки не обновлён"
        self.assertEqual(
            self.note.slug, self.form_data["slug"]
        ), "Slug заметки не обновлён"

    def test_author_can_delete_own_note(self):
        """Проверяем, что автор может удалить свою заметку."""
        note_count_before = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(
            response, self.success_url
        ), "Страница успешного выполнения операции не открыта"
        self.assertEqual(
            Note.objects.count(), note_count_before - 1
        ), "Заметка не удалена"

    def test_reader_cannot_edit_others_note(self):
        """Проверяем, что читатель не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND
        ), "Страница не вернула код 404"
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text, self.NOTE_TEXT
        ), "Текст заметки изменён"
        self.assertEqual(
            self.note.title, self.NOTE_TITLE
        ), "Заголовок заметки изменён"
        self.assertEqual(
            self.note.slug, self.NOTE_SLUG
        ), "Slug заметки изменён"

    def test_reader_cannot_delete_others_note(self):
        """Проверяем, что читатель не может удалить чужую заметку."""
        note_count_before = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND
        ), "Страница не вернула код 404"
        self.assertEqual(
            Note.objects.count(), note_count_before
        ), "Заметка удалена"
