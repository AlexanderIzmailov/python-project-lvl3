from page_loader.page_loader_logic import page_loader
import requests_mock
import tempfile
import os
import pytest
import requests


def test_page_loader():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/without_imgages.html").read()
        m.get("http://test.com", text=correct)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = page_loader("http://test.com", tmpdir)
            assert result == correct


# def test_page_loader2():
#     with requests_mock.Mocker() as m:
#         correct = open("tests/fixtures/with_images.html").read()
#         m.get("https://with_images.ru", text=correct)
#         m.get("https://with_images.ru/test_jpg.jpg", text="image")
        
#         with tempfile.TemporaryDirectory() as tmpdir:
#             result = page_loader("https://with_images.ru", tmpdir)
#             image = os.path.join(tmpdir, "with_images-ru_files", "with_images-ru-test_jpg.jpg")
#             read_image = open(image).read()
#             assert read_image == "image"
#             assert result != correct


def test_page_loader2():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/with_images.html").read()
        m.get("https://with_images.ru", text=correct)
        m.get("https://with_images.ru/test_jpg.jpg", text="image")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = page_loader("https://with_images.ru", tmpdir)
            image = os.path.join(tmpdir, "with-images-ru_files", "with-images-ru-test-jpg.jpg")
            read_image = open(image).read()
            assert read_image == "image"
            assert result != correct


def test_page_loader3():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/link_script_test.html").read()
        m.get("https://link_script_test.ru", text=correct)
        m.get("https://cdn2.hexlet.io/assets/menu.css", text="css1")
        m.get("https://link_script_test.ru/assets/application.css", text="css2")
        m.get("https://link_script_test.ru/courses", text="html")
        m.get("https://link_script_test.ru/assets/professions/nodejs.png", text="image")
        m.get("https://cdn2.hexlet.io/assets/professions/nodejs.png", text="image_double")
        m.get("https://js.stripe.com/v3/", text="script1")
        m.get("https://link_script_test.ru/packs/js/runtime.js", text="script2")

        with tempfile.TemporaryDirectory() as tmpdir:
            result = page_loader("https://link_script_test.ru", tmpdir)
            
            css = os.path.join(tmpdir, "link-script-test-ru_files", "link-script-test-ru-assets-application.css")
            html = os.path.join(tmpdir, "link-script-test-ru_files", "link-script-test-ru-courses.html")
            script = os.path.join(tmpdir, "link-script-test-ru_files", "link-script-test-ru-packs-js-runtime.js")

            css_read = open(css).read()
            html_read = open(html).read()
            script_read = open(script).read()

            assert css_read == "css2"
            assert html_read == "html"
            assert script_read == "script2"
            assert result != correct


def test_exceptions_connection():
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/without_imgages.html").read()
        m.get("http://test.com", text=correct, status_code=404)
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(SystemExit, match=r".*404.*"):
                result = page_loader("http://test.com", tmpdir)


def test_exception_chmod():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test_dir")
        os.mkdir(test_dir)
        print(test_dir)
        os.chmod(test_dir, 000)

        with requests_mock.Mocker() as m:
            correct = open("tests/fixtures/without_imgages.html").read()
            m.get("http://test.com", text=correct)

            with pytest.raises(SystemExit, match=r".*Permission.*"):
                result = page_loader("http://test.com", test_dir)


def test_exception_file_404(caplog):
    with requests_mock.Mocker() as m:
        correct = open("tests/fixtures/with_images.html").read()
        m.get("https://with_images.ru", text=correct)
        m.get("https://with_images.ru/test_jpg.jpg", text="image", status_code=404)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = page_loader("https://with_images.ru", tmpdir)
            assert "404 Client Error: None for url: https://with_images.ru/test_jpg.jpg" in caplog.text