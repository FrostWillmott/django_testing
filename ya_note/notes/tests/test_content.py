# notes/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_note_in_object_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_list_excludes_other_users_notes(self):
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_forms_in_create_and_edit_pages(self):
        """На страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.author)
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
