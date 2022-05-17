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


def take_img_urls(url, domain, img_dir_name, img_dir_path):
    url_parse = urlparse(url)
    netloc = url_parse.netloc

    if netloc == "":
        domain_parse = urlparse(domain)
        netloc = domain_parse.netloc
        url = urljoin(domain, url)

    path = url_parse.path
    path_clear = re.search(r".*(?=\.|\/$)|^.*", path)    # noqa: W605
    path_clear = path_clear[0] if path_clear[0][0] == "/" else "/" + path_clear[0]  # noqa: E501
    path_ext = re.search(r"\.\w+$", path)    # noqa: W605

    img_file_name = re.sub(r"\W", "-", netloc + path_clear)   # noqa: W605
    img_url_for_html = os.path.join(img_dir_name, img_file_name + path_ext[0])

    name_with_ext = img_file_name + path_ext[0]
    full_img_path = os.path.join(img_dir_path, img_dir_name, name_with_ext)

    return url, img_url_for_html, full_img_path


def download_and_change_url_img(soup_img_object, url, images_dir_name, path):
    img_url = soup_img_object["src"]
    url_for_download, url_for_html, path_for_file = take_img_urls(img_url, url, images_dir_name, path)  # noqa: E501
    img_data = requests.get(url_for_download).content
    with open(path_for_file, 'wb') as handler:
        handler.write(img_data)

    soup_img_object["src"] = url_for_html


def page_loader(url, path):
    domain = urlparse(url).netloc
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    output_file_name = change_name(url) + ".html"

    images = soup.find_all('img')
    if len(images) > 0:
        images_dir_name = change_name(url) + "_files"

        images_dir = os.path.join(path, images_dir_name)
        os.mkdir(images_dir)

        create_file_flag = False
        for k in images:
            img_domain = urlparse(k["src"]).netloc
            if domain == img_domain or img_domain == "":
                create_file_flag = True
                download_and_change_url_img(k, url, images_dir_name, path)

        if not create_file_flag:
            os.rmdir(images_dir)

    html_content = soup.prettify()

    output_file = os.path.join(path, output_file_name)

    with open(output_file, "w") as f:
        f.write(html_content)

    print(output_file)
    return html_content
