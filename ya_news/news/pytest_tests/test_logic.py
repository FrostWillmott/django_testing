from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(
    client, form_data, news_detail_url, user_login_url
):
    """
    Проверяем, что анонимный пользователь
    не может оставить комментарий.
    """
    response = client.post(news_detail_url, data=form_data)
    expected_url = f"{user_login_url}?next={news_detail_url}"
    assertRedirects(response, expected_url)
    assert (
        Comment.objects.count() == 0
    ), "Комментарий создан, но не должен быть"


def test_authenticated_user_can_post_comment(
    not_author_client, news_detail_url, not_author, form_data, news
):
    """
    Проверяем, что авторизованный пользователь
    может оставить комментарий.
    """
    response = not_author_client.post(news_detail_url, data=form_data)
    expected_url = f"{news_detail_url}#comments"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1, "Комментарий не создан"
    new_comment = Comment.objects.get()
    assert new_comment.news == news, "Комментарий создан для другой новости"
    assert new_comment.text == form_data["text"], "Текст комментария неверный"
    assert new_comment.author == not_author, "Автор комментария неверный"


@pytest.mark.parametrize("bad_word", BAD_WORDS)
def test_comment_with_prohibited_words(
    author_client, bad_word, news_detail_url
):
    """
    Проверяем, что комментарий с запрещенными словами не будет опубликован,
    а форма вернёт ошибку.
    """
    bad_words_data = {"text": f"Какой-то текст, {bad_word}, еще текст"}
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)
    assert (
        Comment.objects.count() == 0
    ), "Комментарий создан, но не должен быть"


def test_author_can_edit_comment(
    author_client,
    form_data,
    news,
    author,
    news_detail_url,
    news_edit_url,
    comment,
):
    """Проверяем, что автор новости может отредактировать свой комментарий."""
    response = author_client.post(news_edit_url, form_data)
    expected_url = f"{news_detail_url}#comments"
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert (
        comment.news == news
    ), "Комментарий отредактирован для другой новости"
    assert comment.text == form_data["text"], "Текст комментария не изменен"
    assert comment.author == author, "Автор комментария неверный"


def test_author_can_delete_comment(
    author_client, news_delete_url, news_detail_url
):
    """Проверяем, что автор новости может удалить свой комментарий."""
    response = author_client.post(news_delete_url)
    expected_url = f"{news_detail_url}#comments"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0, "Комментарий не удален"


def test_user_cant_edit_others_comment(
    not_author_client, form_data, comment, author, news_edit_url
):
    """Проверяем, что пользователь
    не может редактировать чужой комментарий."""
    response = not_author_client.post(news_edit_url, form_data)
    assert (
        response.status_code == HTTPStatus.NOT_FOUND
    ), "Пользователь может редактировать чужой комментарий"
    comment_from_db = Comment.objects.get(id=comment.id)
    assert (
        comment.text == comment_from_db.text
    ), "Текст комментария был изменен"
    assert (
        comment.author == comment_from_db.author
    ), "Автор комментария был изменен"


def test_user_cant_delete_others_comment(not_author_client, news_delete_url):
    """Проверяем, что пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(news_delete_url)
    assert (
        response.status_code == HTTPStatus.NOT_FOUND
    ), "Пользователь может удалить чужой комментарий"
    assert Comment.objects.count() == 1, "Комментарий был удален"
