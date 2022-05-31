import re
import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from progress.bar import Bar
import sys

import logging

logger = logging.getLogger("page_loader_logic")
logger.setLevel(logging.INFO)

f = logging.Formatter("%(levelname)s | %(funcName)s | %(message)s")  # noqa: E501
sh = logging.StreamHandler()
sh.setFormatter(f)

logger.addHandler(sh)


def change_name(url):
    url_parse = urlparse(url)

    netloc = url_parse.netloc
    path = url_parse.path
    # path_ext = re.search("\.\w+$", path)
    # path_clear = re.search(".*(?=\.)|^.*[^\.].*", path)
    path_clear = re.search(r".*(?=\.|\/$)|^.*", path)    # noqa: W605

    result = re.sub(r"[^a-zA-Z0-9]", "-", netloc)  # noqa: W605

    if path_clear:
        result += re.sub(r"[^a-zA-Z0-9]", "-", path_clear[0])  # noqa: W605

    return result


def take_files_urls(file_url, domain, files_dir_name, files_dir_path):
    file_url_parse = urlparse(file_url)
    netloc = file_url_parse.netloc

    if netloc == "":
        logger.debug("url without netloc: {}".format(file_url))
        domain_parse = urlparse(domain)
        netloc = domain_parse.netloc
        file_url = urljoin(domain, file_url)
        logger.debug("url after urljoin: {}".format(file_url))

    file_path = file_url_parse.path
    # file_path = file_url_parse.path + "" if file_url_parse.query == "" else "?" + file_url_parse.query  # noqa: E501
    file_path_clear = re.search(r".*(?=\.|\/$)|^.*", file_path)    # noqa: W605
    file_path_clear = file_path_clear[0] if file_path_clear[0][0] == "/" else "/" + file_path_clear[0]  # noqa: E501
    logger.debug("file_path_clear: {}".format(file_path_clear))

    file_path_ext = re.search(r"\.\w+$", file_path)    # noqa: W605
    if file_path_ext:
        file_path_ext = file_path_ext[0]
    else:
        file_path_ext = ".html"
    logger.debug("file_path_ext: {}".format(file_path_ext))

    file_name = re.sub(r"[^a-zA-Z0-9]", "-", netloc + file_path_clear)   # noqa: W605, E501
    file_url_for_html = os.path.join(files_dir_name, file_name + file_path_ext)  # noqa: E501

    name_with_ext = file_name + file_path_ext
    full_file_path = os.path.join(files_dir_path, files_dir_name, name_with_ext)
    logger.debug("full_file_path: {}".format(full_file_path))

    return file_url, file_url_for_html, full_file_path


def download_and_change_url_file(soup_object, main_url, files_dir_name, path, tag, open_mode):   # noqa: E501
    file_url = soup_object[tag]
    url_for_download, url_for_html, path_for_file = take_files_urls(file_url, main_url, files_dir_name, path)  # noqa: E501

    # object_data = requests.get(url_for_download).content

    try:
        object_data = requests.get(url_for_download)
        object_data.raise_for_status()
    except requests.exceptions.ConnectionError as errc:
        logger.error("Downloading file: {}. Connection error: {}".format(url_for_download, errc))  # noqa: E501
        raise SystemExit(errc) from None
    except requests.exceptions.RequestException as err:
        logger.warning("Downloading file: {}. Error: {}".format(url_for_download, err))  # noqa: E501
    else:

        bar = Bar(soup_object[tag], max=1)
        bar.next()

        object_data = object_data.content

        with open(path_for_file, open_mode) as handler:
            handler.write(object_data)

        logger.debug("url_for_html: {}".format(url_for_html))
        soup_object[tag] = url_for_html
        bar.finish()


# def page_loader(url, path):
#     domain = urlparse(url).netloc
#     r = requests.get(url)
#     soup = BeautifulSoup(r.text, "html.parser")

#     files_dir_name = change_name(url) + "_files"
#     files_dir = os.path.join(path, files_dir_name)
#     os.mkdir(files_dir)

#     images = soup.find_all('img')
#     if len(images) > 0:
#         for k in images:
#             img_domain = urlparse(k["src"]).netloc
#             if domain == img_domain or img_domain == "":
#                 download_and_change_url_file(k, url, files_dir_name, path, "src", "wb")  # noqa: E501

#     if len(os.listdir(files_dir)) == 0:
#         os.rmdir(files_dir)

#     output_file_name = change_name(url) + ".html"
#     output_file = os.path.join(path, output_file_name)
#     html_content = soup.prettify()

#     with open(output_file, "w") as f:
#         f.write(html_content)

#     print(output_file)
#     return html_content


def is_valid_for_downloading(domain, file_domain):
    if domain == file_domain or file_domain == "":
        return True
    else:
        return False


def download(url, path):  # noqa: C901
    logger.info("Start page loader")
    logger.debug("url: {}, path {}".format(url, path))

    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.ConnectionError as errc:
        logger.error("Connection error: {}".format(errc))
        # raise SystemExit(errc) from None
        sys.exit(1)
    except requests.exceptions.HTTPError as errh:
        logger.error("HTTP error: {}".format(errh))
        # raise SystemExit(errh) from None
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        logger.error("Network error: {}".format(err))
        sys.exit(1)

    soup = BeautifulSoup(r.text, "html.parser")
    domain = urlparse(url).netloc

    files_dir_name = change_name(url) + "_files"
    files_dir = os.path.join(path, files_dir_name)
    logger.info("Creating directory for files: {}".format(files_dir))

    try:
        os.mkdir(files_dir)
    except PermissionError as err:
        logger.error("Permission error: {}".format(err))
        raise SystemExit(err) from None

    images = soup.find_all('img')
    if len(images) > 0:
        for k in images:
            img_domain = urlparse(k["src"]).netloc
            if is_valid_for_downloading(domain, img_domain):
                logger.debug("Start downloading image: {}".format(k["src"]))
                download_and_change_url_file(k, url, files_dir_name, path, "src", "wb")  # noqa: E501

    links = soup.find_all('link')
    if len(links) > 0:
        for link in links:
            if link.get("type") == "application/rss+xml":   # pass RSS
                continue

            link_domain = urlparse(link["href"]).netloc
            if is_valid_for_downloading(domain, link_domain):
                logger.debug("Start downloading link: {}".format(link["href"]))
                download_and_change_url_file(link, url, files_dir_name, path, "href", "wb")  # noqa: E501

    scripts = soup.find_all('script')
    if len(scripts) > 0:
        for s in scripts:

            if s.has_attr("src") is False:
                continue

            script_domain = urlparse(s["src"]).netloc
            if is_valid_for_downloading(domain, script_domain):
                logger.debug("Start downloading script: {}".format(s["src"]))
                download_and_change_url_file(s, url, files_dir_name, path, "src", "wb")  # noqa: E501

    if len(os.listdir(files_dir)) == 0:
        logger.info("Created directory is empty. Remove directory")
        os.rmdir(files_dir)

    output_file_name = change_name(url) + ".html"
    output_file = os.path.join(path, output_file_name)
    html_content = soup.prettify()

    with open(output_file, "w") as f:
        f.write(html_content)

    logger.info("The download is finished.")
    print(output_file)
    # return html_content
    return output_file
