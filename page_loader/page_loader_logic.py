import re
import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def change_name(url):
    url_parse = urlparse(url)

    netloc = url_parse.netloc
    path = url_parse.path
    # path_ext = re.search("\.\w+$", path)
    # path_clear = re.search(".*(?=\.)|^.*[^\.].*", path)
    path_clear = re.search(r".*(?=\.|\/$)|^.*", path)    # noqa: W605

    result = re.sub(r"\W", "-", netloc)  # noqa: W605

    if path_clear:
        result += re.sub(r"\W", "-", path_clear[0])  # noqa: W605

    return result


def take_files_urls(file_url, domain, files_dir_name, files_dir_path):
    file_url_parse = urlparse(file_url)
    netloc = file_url_parse.netloc

    if netloc == "":
        domain_parse = urlparse(domain)
        netloc = domain_parse.netloc
        file_url = urljoin(domain, file_url)

    file_path = file_url_parse.path
    file_path_clear = re.search(r".*(?=\.|\/$)|^.*", file_path)    # noqa: W605
    file_path_clear = file_path_clear[0] if file_path_clear[0][0] == "/" else "/" + file_path_clear[0]  # noqa: E501
    file_path_ext = re.search(r"\.\w+$", file_path)    # noqa: W605

    file_name = re.sub(r"\W", "-", netloc + file_path_clear)   # noqa: W605
    file_url_for_html = os.path.join(files_dir_name, file_name + file_path_ext[0])  # noqa: E501

    name_with_ext = file_name + file_path_ext[0]
    full_file_path = os.path.join(files_dir_path, files_dir_name, name_with_ext)

    return file_url, file_url_for_html, full_file_path


def download_and_change_url_file(soup_object, main_url, files_dir_name, path, tag, open_mode):   # noqa: E501
    file_url = soup_object[tag]
    url_for_download, url_for_html, path_for_file = take_files_urls(file_url, main_url, files_dir_name, path)  # noqa: E501
    object_data = requests.get(url_for_download).content
    with open(path_for_file, open_mode) as handler:
        handler.write(object_data)

    soup_object[tag] = url_for_html


def page_loader(url, path):
    domain = urlparse(url).netloc
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    output_file_name = change_name(url) + ".html"

    images = soup.find_all('img')
    if len(images) > 0:
        files_dir_name = change_name(url) + "_files"

        files_dir = os.path.join(path, files_dir_name)
        os.mkdir(files_dir)

        create_file_flag = False
        for k in images:
            img_domain = urlparse(k["src"]).netloc
            if domain == img_domain or img_domain == "":
                create_file_flag = True
                download_and_change_url_file(k, url, files_dir_name, path, "src", "wb")  # noqa: E501

        if not create_file_flag:
            os.rmdir(files_dir)

    html_content = soup.prettify()

    output_file = os.path.join(path, output_file_name)

    with open(output_file, "w") as f:
        f.write(html_content)

    print(output_file)
    return html_content
