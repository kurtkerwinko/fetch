#!/bin/python

import argparse
import datetime
import os
import re
import requests
import sys
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import quote


def convert_url_to_filepath(url):
    fp = quote(re.sub(r"http://|https://", "", url), safe="")
    return Path(fp + ".html")


def save_data(filepath, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(data)


def fetch_url(url, metadata):
    r = requests.get(url)
    r.raise_for_status()
    filepath = convert_url_to_filepath(url)

    try:
        last_modified = os.path.getmtime(filepath)
    except FileNotFoundError:
        last_modified = None

    save_data(filepath, r.text)

    if metadata:
        if last_modified:
            last_modified = datetime.datetime.fromtimestamp(last_modified, datetime.UTC)
            last_modified = last_modified.strftime("%a %b %d %Y %H:%M %Z")

        soup = BeautifulSoup(r.text, features="html.parser")
        print(
            f"site: {url}\n" +
            f"num_links: {len(soup.find_all('a'))} \n" +
            f"images: {len(soup.find_all('img'))}\n" +
            f"last_fetch: {last_modified}\n"
        )


def is_valid_url(url):
    if not url.startswith(("http://", "https://")):
        print(f"{url} is not a valid url", file=sys.stderr)
        return False
    return True


def fetch_urls(urls, metadata):
    for url in urls:
        if not is_valid_url(url):
            continue

        try:
            fetch_url(url, metadata)
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as e:
            print(f"Unable to retrieve {url}. Error: {e}.", file=sys.stderr)


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
        help="The URLs of the web pages to retrieve",
    )
    parser.add_argument(
        "--metadata",
        action=argparse.BooleanOptionalAction,
        help="Print metadata",
    )
    args = parser.parse_args()
    fetch_urls(args.urls, args.metadata)


if __name__ == "__main__":
    main()

