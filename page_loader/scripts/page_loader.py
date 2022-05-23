from page_loader import page_loader, logger
import os
import argparse


parser = argparse.ArgumentParser(
    description='Downloading internet pages',
    usage="page-loader [options] <url>")
parser.add_argument("url", help=argparse.SUPPRESS)
parser.add_argument(
    "-V", "--version",
    help='output the version number',
    action='version')
parser.add_argument(
    "-o", "--output",
    help='output dir (default: "/app")',
    metavar="",
    default=os.getcwd())
parser.add_argument(
    "-l", "--log_level",
    help='set log level (default: "INFO")',
    metavar="",
    default="INFO")
args = vars(parser.parse_args())

url = args["url"]
output_path = args["output"]
log_level = args["log_level"]


def main():
    LOGLEVEL = os.environ.get('LOGLEVEL', log_level).upper()
    logger.setLevel(LOGLEVEL)

    page_loader(url, output_path)


if __name__ == '__main__':
    main()
