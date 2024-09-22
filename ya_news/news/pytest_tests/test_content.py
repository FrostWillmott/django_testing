import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_on_homepage(client, home_page_url, lots_of_news):
    """
    Проверяем, что количество новостей на главной странице
    равно NEWS_COUNT_ON_HOME_PAGE.
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    assert 'object_list' in client.get(
        home_page_url).context, "Key 'object_list' not found in context"
    all_news = client.get(home_page_url).context.get('object_list')
    all_timestamps = [news.date for news in all_news]
    sorted_timestamps = sorted(all_timestamps)
    assert all_news.count() == NEWS_COUNT_ON_HOME_PAGE,\
        "Number of news on the home page is not equal to NEWS_COUNT_ON_HOME_PAGE"
    assert all_timestamps == sorted_timestamps,\
        "News are not sorted by date, the newest news should be at the top of the list"


@pytest.mark.django_db
def test_comments_order_on_news_detail(news,
                                       lots_of_comments,
                                       news_detail_url):
    """
    Проверяем, что комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps,\
        "Comments are not sorted by date, the newest comments should be at the bottom of the list"


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_login_type, expected_answer',
    (
            (pytest.lazy_fixture('client'), not 'form'),
            (pytest.lazy_fixture('not_author_client'), 'form'),
    )
)
def test_comment_form_visibility(user_login_type,
                                 expected_answer, news_detail_url):
    """
    Проверяем, что анонимному пользователю недоступна форма
    для отправки комментария на странице отдельной новости,
    а авторизованному доступна.
    """
    response = user_login_type.get(news_detail_url)
    assert expected_answer in response.context,\
        f"No {expected_answer} for {user_login_type} in context"
    if expected_answer == 'form':
        assert isinstance(response.context['form'],
                          CommentForm), "Form is not an instance of CommentForm"
