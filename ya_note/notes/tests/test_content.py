from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тесты проверяют, что на страницах присутствует ожидаемый контент."""

    @classmethod
    def setUpTestData(cls):
        """Создаём пользователей и заметку."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_notes_accessibility_for_different_users(self):
        """
        Проверяем, что отдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context
        """
        expected_resaults = (
            (
                self.author_client,
                True
            ),
            (
                self.reader_client,
                False
            ),
        )
        for user_client, expected_context in expected_resaults:
            with ((((self.subTest(user_client=user_client))))):
                url = reverse('notes:list')
                response = user_client.get(url)
                self.assertIs(expected_context,
                              self.note in response.context[
                                  'object_list']),
                "Статус наличия заметки в списке object_list не соответствует ожидаемому"

    def test_forms_in_create_and_edit_pages(self):
        """
        Проверяем, что на страницы создания
        и редактирования заметки передаются формы.
        """
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        for url in urls:
            with (((((self.subTest(url=url)))))):
                response = self.author_client.get(url)
                self.assertIn('form',
                              response.context),
                "На страницу не передана форма"
                self.assertIsInstance(response.context['form'],
                                      NoteForm),
                "Форма передана, но это не форма NoteForm"
