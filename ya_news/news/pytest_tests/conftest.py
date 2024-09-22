import pytest
from django.test.client import Client
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(
        not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def lots_of_news():
    for i in range(1, 11):
        News.objects.create(
            title=f'Заголовок {i}',
            text=f'Текст {i}'
        )
    return News.objects.all()


@pytest.fixture
def lots_of_comments(news, author):
    for i in range(1, 11):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
    return Comment.objects.all()


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def id_post_for_args(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }


@pytest.fixture
def home_page_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(id_for_args):
    return reverse('news:detail', args=id_for_args)


@pytest.fixture
def user_login_url():
    return reverse('users:login')


@pytest.fixture
def user_logout_url():
    return reverse('users:logout')


@pytest.fixture
def user_signup_url():
    return reverse('users:signup')


@pytest.fixture
def news_edit_url(id_post_for_args):
    return reverse('news:edit', args=id_post_for_args)


@pytest.fixture
def news_delete_url(id_post_for_args):
    return reverse('news:delete', args=id_post_for_args)
