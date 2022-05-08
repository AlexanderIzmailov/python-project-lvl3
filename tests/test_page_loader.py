from page_loader.page_loader_logic import page_loader, change_name
# import requests
import requests_mock


#@requests_mock.Mocker()
def test_page_loader():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/serenewholecalmspell-neverssl-com-online.html").read()
        m.get("http://test.com", text=correct)

        result = page_loader("http://test.com")
        assert result == correct


def test_change_name():
    url = "https://ru.hexlet.io/courses"
    result = change_name(url)
    assert result == "ru-hexlet-io-courses.html"
