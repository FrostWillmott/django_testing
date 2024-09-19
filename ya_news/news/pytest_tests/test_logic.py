# test_logic.py
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from http import HTTPStatus
from news.models import Comment
from news.forms import BAD_WORDS, WARNING
import pytest


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
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.text == form_data['text']


def test_comment_with_prohibited_words(author_client, news):
    url = reverse('news:detail', args=[news.id])
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert news.comment_set.count() == 0


def test_author_can_edit_comment(author_client, form_data, news,
                                 id_post_for_args, id_for_args,
                                 comment):
    url = reverse('news:edit', args=id_for_args)
    response = author_client.post(url, form_data)
    expected_url = f'{reverse("news:detail", args=id_for_args)}#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.news == news
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, id_post_for_args,
                                   id_for_args):
    url = reverse('news:delete', args=id_post_for_args)
    response = author_client.post(url)
    expected_url = f'{reverse("news:detail", args=id_for_args)}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_edit_others_comment(not_author_client, form_data,
                                       comment):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.id == comment_from_db.id


def test_user_cant_delete_others_comment(not_author_client,
                                         id_post_for_args):
    url = reverse('news:delete', args=id_post_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
