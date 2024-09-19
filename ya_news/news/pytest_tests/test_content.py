# test_content.py
import pytest
from django.urls import reverse
from http import HTTPStatus
from news.forms import CommentForm


def test_news_count_on_homepage(not_author_client):
    response = not_author_client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['news_list']) <= 10


def test_news_order_on_homepage(not_author_client):
    response = not_author_client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    assert all(
        object_list[i].pub_date >= object_list[i + 1].pub_date for i in
        range(len(object_list) - 1))


def test_comments_order_on_news_detail(not_author_client, news,
                                       comment):
    response = not_author_client.get(
        reverse('news:detail', args=[news.id]))
    assert response.status_code == HTTPStatus.OK
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_args')),
    )
)
def test_comment_form_visibility_for_anonymous_user(anonymous_client,
                                                    name, args):
    response = anonymous_client.get(
        reverse('news:detail', args=args))
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_args')),
    )
)
def test_comment_form_visibility_for_authenticated_user(
        not_author_client, name, args):
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = not_author_client.get(url)

    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], CommentForm)
