from page_loader.page_loader_logic import page_loader
import requests_mock
import tempfile
import os


def test_page_loader():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/without_imgages.html").read()
        m.get("http://test.com", text=correct)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = page_loader("http://test.com", tmpdir)
            assert result == correct


def test_page_loader3():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/with_images.html").read()
        m.get("https://with_images.ru", text=correct)
        m.get("https://with_images.ru/test_jpg.jpg", text="image")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = page_loader("https://with_images.ru", tmpdir)
            image = os.path.join(tmpdir, "with_images-ru_files", "with_images-ru-test_jpg.jpg")
            read_image = open(image).read()
            assert read_image == "image"
            assert result != correct
