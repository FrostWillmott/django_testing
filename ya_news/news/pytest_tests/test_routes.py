from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name_url',
    (
            pytest.lazy_fixture('home_page_url'),
            pytest.lazy_fixture('news_detail_url'),
            pytest.lazy_fixture('user_login_url'),
            pytest.lazy_fixture('user_logout_url'),
            pytest.lazy_fixture('user_signup_url'),
    )
)
def test_pages_availability_for_anonymous_user(client, name_url):
    """Проверяем доступность страниц для анонимного пользователя."""
    response = client.get(name_url)
    assert response.status_code == HTTPStatus.OK,\
        f'Страница {name_url} недоступна'


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
            (pytest.lazy_fixture('not_author_client'),
             HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name_url',
    (
            pytest.lazy_fixture('news_edit_url'),
            pytest.lazy_fixture('news_delete_url'),
    )
)
def test_pages_availability_for_different_users(parametrized_client,
                                                expected_status,
                                                name_url):
    """
    Проверяем, что удаления и редактирования комментария доступны автору комментария,
    авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404).
    """
    response = parametrized_client.get(name_url)
    assert response.status_code == expected_status,\
        (f'Page {name_url} returned {response.status_code}'
         f' for {parametrized_client}, but expected {expected_status}')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name_url',
    (
            pytest.lazy_fixture('news_edit_url'),
            pytest.lazy_fixture('news_delete_url'),
    ),
)
def test_redirects(client, name_url, user_login_url):
    """
    Проверяем, что при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
    """
    expected_url = f'{user_login_url}?next={name_url}'
    response = client.get(name_url)
    (assertRedirects(response,
                    expected_url),
     f'Page {name_url} not redirected to {expected_url}')
