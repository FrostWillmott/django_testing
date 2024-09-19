# test_logic.py
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from http import HTTPStatus
from news.models import Comment, News
from news.forms import CommentForm
from news.forms import BAD_WORDS, WARNING
import pytest

from news.pytest_tests.conftest import id_for_args


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, form_data,
                                          id_for_args, news):
    url = reverse('news:detail', args=id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert news.comment_set.count() == 0


def test_authenticated_user_can_post_comment(not_author_client,
                                             form_data,
                                             news, id_for_args):
    url = reverse('news:detail', args=id_for_args)
    response = not_author_client.post(url, data=form_data)
    expected_url = f'{reverse("news:detail", args=id_for_args)}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.news == news
    assert new_comment.text == form_data['text']
    # Вроде бы здесь нарушен принцип "один тест - одна проверка";
    # но если хоть одна из этих проверок провалится -
    # весь тест можно признать провалившимся, а последующие невыполненные проверки
    # не внесли бы в отчёт о тесте ничего принципиально важного.


def test_comment_with_prohibited_words(author_client, news):
    url = reverse('news:detail', args=[news.id])
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    assert news.comment_set.count() == 0


# @pytest.mark.django_db
# def test_author_can_edit_own_comment(author_client, form_data, comment,
#                                      news):
#     url = reverse('news:edit_comment', args=[comment.id])
#     response = author_client.post(url, data=form_data)
#     assertRedirects(response,
#                     reverse('news:detail', args=[comment.news.id]))
#     comment.refresh_from_db()
#     assert comment.text == form_data['text']


# В параметрах вызвана фикстура note: значит, в БД создана заметка.
def test_author_can_edit_comment(author_client, form_data, news,
                                 id_post_for_args, id_for_args,
                                 comment):
    # Получаем адрес страницы редактирования заметки:
    url = reverse('news:edit', args=id_for_args)
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(url, form_data)
    # Проверяем редирект:
    expected_url = f'{reverse("news:detail", args=id_for_args)}#comments'
    assertRedirects(response, expected_url)
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    comment.refresh_from_db()
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    assert comment.news == news
    assert comment.text == form_data['text']


# def test_author_can_delete_own_comment(author_client, id_post_for_args,
#                                        id_for_args, comment, news):
#     url = reverse('news:delete_comment', args=id_post_for_args)
#     response = author_client.post(url)
#     assertRedirects(response,
#                     reverse('news:detail', args=id_for_args))
#     assert comment.news.comment_set.count() == 0

def test_author_can_delete_comment(author_client, id_post_for_args,
                                   id_for_args):
    url = reverse('news:delete', args=id_post_for_args)
    response = author_client.post(url)
    expected_url = f'{reverse("news:detail", args=id_for_args)}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


# def test_user_cant_edit_others_comment(not_author_client, form_data,
#                                        comment):
#     url = reverse('news:edit_comment', args=[comment.id])
#     response = not_author_client.post(url, data=form_data)
#     assert response.status_code == HTTPStatus.FORBIDDEN
#     comment_from_db = comment.news.comment_set.get(id=comment.id)
#     assert comment.text == comment_from_db.text

def test_user_cant_edit_others_comment(not_author_client, form_data,
                                       comment):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=comment.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text
    assert comment.id == comment_from_db.id


# @pytest.mark.django_db
# def test_user_cant_delete_others_comment(not_author_client, comment):
#     url = reverse('news:delete_comment', args=[comment.id])
#     response = not_author_client.post(url)
#     assert response.status_code == HTTPStatus.FORBIDDEN
#     assert comment.news.comment_set.count() == 1

def test_user_cant_delete_others_comment(not_author_client,
                                         id_post_for_args):
    url = reverse('news:delete', args=id_post_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
