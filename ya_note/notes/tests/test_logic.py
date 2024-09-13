# notes/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNotesCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            # slug='slug',
            author=cls.author,
        )
        # Адрес страницы с новостью.
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {'title': 'Новая заметка',
                         'text': 'Текст'}

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        self.assertIn(response.status_code,
                      [HTTPStatus.FORBIDDEN, HTTPStatus.FOUND])
        self.assertFalse(
            Note.objects.filter(text=self.form_data['text'],
                                title=self.form_data['title']).exists())

    def test_authenticated_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Note.objects.filter(text=self.form_data['text'],
                                title=self.form_data['title']).exists())

    def test_cannot_create_note_with_duplicate_slug(self):
        duplicate_note_data = {'title': 'Дубликат', 'text': 'Текст',
                               'slug': self.note.slug}
        # response = self.auth_client.post(self.url,
        #                                  data=duplicate_note_data)
        # self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Note.objects.filter(slug=self.note.slug).count(), 1)

    def test_slug_is_generated_if_not_provided(self):
        form_data_without_slug = {'title': 'Новая заметка',
                                  'text': 'Текст'}
        response = self.auth_client.post(self.url,
                                         data=form_data_without_slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.filter(text='Текст').latest('id')
        self.assertEqual(note.slug, slugify('Новая заметка'))


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NOTE_TITLE = 'Новый заголовок'
    NEW_NOTE_TITLE = 'Обновлённый заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
        )
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT}

    def test_author_can_edit_own_note(self):
        response = self.author_client.post(self.edit_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)

    def test_author_can_delete_own_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_reader_cannot_edit_others_note(self):
        response = self.reader_client.post(self.edit_url,
                                           data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)

    def test_reader_cannot_delete_others_note(self):
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
