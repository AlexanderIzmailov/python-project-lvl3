import re
import os
import requests


def change_name(name):
    url_parse = re.search(
        "(?<=\/\/).*(?=\.\w*$)|(?<=\/\/).*",        # noqa: W605
        name)
    result = re.sub("\W", "-", url_parse[0])        # noqa: W605

    return result + ".html"


def page_loader(url, path):
    r = requests.get(url)
    file_name = change_name(url)

    output_file = os.path.join(path, file_name)

    with open(output_file, "w") as f:
        f.write(r.text)

    print(output_file)

    return output_file
