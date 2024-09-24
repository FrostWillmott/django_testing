import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count_on_homepage(client, home_page_url, lots_of_news):
    """
    Проверяем, что количество новостей на главной странице
    равно NEWS_COUNT_ON_HOME_PAGE.
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    all_news = client.get(home_page_url).context.get("object_list")
    assert all_news.count() == NEWS_COUNT_ON_HOME_PAGE, (
        "Количество новостей на главной странице"
        " не равно NEWS_COUNT_ON_HOME_PAGE"
    )


@pytest.mark.django_db
def test_news_order_on_homepage(client, home_page_url, lots_of_news):
    all_news = client.get(home_page_url).context.get("object_list")
    all_timestamps = [news.date for news in all_news]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps, (
        "Новости на главной странице не отсортированы по дате,"
        " самые свежие новости должны быть в начале списка"
    )


@pytest.mark.django_db
def test_comments_order_on_news_detail(
    client, news, lots_of_comments, news_detail_url
):
    """
    Проверяем, что комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    all_comments = response.context.get("object").comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert (
        all_timestamps == sorted_timestamps
    ), "Комментарии на странице отдельной новости не отсортированы по дате"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_login_type, expected_answer",
    (
        (pytest.lazy_fixture("client"), False),
        (pytest.lazy_fixture("not_author_client"), True),
    ),
)
def test_comment_form_visibility(
    user_login_type, expected_answer, news_detail_url
):
    """
    Проверяем, что анонимному пользователю
    недоступна форма для отправки комментария на странице отдельной новости,
    а авторизованному доступна.
    """
    response = user_login_type.get(news_detail_url)
    assert ("form" in response.context) is expected_answer, (
        "Признак наличия формы для отправки комментария"
        " не соответствует ожидаемому"
    )
    if expected_answer:
        assert isinstance(response.context["form"], CommentForm), (
            "Форма для отправки комментария авторизованным пользователем"
            " не является формой CommentForm"
        )
