#!/bin/python

import argparse
import logging
import requests
from urllib.parse import urlparse


def save_data(filename, data):
    with open(filename, mode="w") as f:
        f.write(data)


def fetch_url(url):
    r = requests.get(url)
    r.raise_for_status()
    u = urlparse(url)
    save_data(f"{u.hostname}.html", r.text)


def is_valid_url(url):
    if not url.startswith(("http://", "https://")):
        logging.error(f"{url} is not a valid url")
        return False

    # TODO: Support non-root URLs
    if urlparse(url).path():
        logging.error(f"{url} is non-root URLs are not currently supported")
        return False

    return True


def fetch_urls(urls):
    for url in urls:
        if not is_valid_url(url):
            continue

        try:
            fetch_url(url)
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as e:
            logging.error(f"Unable to retrieve {url}. Error: {e}.")


def main():
    parser = argparse.ArgumentParser(
        prog="fetch",
        description="A command line program that retrieves web pages and saves them locally",
    )
    parser.add_argument(
        "urls",
        metavar="URL",
        type=str,
        nargs="+",
        help="The URLs of the web pages to retrieve"
    )
    args = parser.parse_args()

    fetch_urls(args.urls)


if __name__ == "__main__":
    main()

