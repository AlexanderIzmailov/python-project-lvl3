from page_loader.page_loader_logic import page_loader
# import requests
import requests_mock


#@requests_mock.Mocker()
def test_page_loader():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/serenewholecalmspell-neverssl-com-online.html").read()
        m.get("http://test.com", text=correct)

        result = page_loader("http://test.com")
        assert result == correct
