#!/bin/python3

import argparse
import datetime
import magic
import os
import re
import requests
import sys
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import quote, urlparse


TAG_SRC_ATTR = {
    "img": "src",
    "link": "href",
}

REQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
}


def save_data(filepath, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(data)


def convert_to_full_url(root_url, url):
    asset_url = urlparse(url)
    if asset_url.hostname:
        if not asset_url.scheme:
            return asset_url._replace(scheme="https").geturl()
        return url

    if not asset_url.geturl().startswith("/"):
        return root_url + "/" + asset_url.geturl()

    return root_url + asset_url.geturl()


def is_downloadable(url, content_type):
    dl_content_types = ("image/", "text/css", "text/javascript", "text/plain")
    if not content_type.startswith(dl_content_types):
        return False

    if "text/plain" in content_type and not urlparse(url).path.endswith((".js", ".css")):
        return False

    return True


def save_asset(url, save_dir):
    content_type = requests.head(url, headers=REQ_HEADERS).headers.get("content_type", None)
    if content_type and not is_downloadable(url, content_type):
        return

    try:
        asset_data = requests.get(url, headers=REQ_HEADERS).content
    except:
        print(f"Unable to retrieve asset {url}.", file=sys.stderr)
        return

    if content_type is None:
        content_type = magic.from_buffer(asset_data, mime=True)

    if not is_downloadable(url, content_type):
        return

    asset_path = "/" + quote(re.sub(r"http://|https://", "", url))

    # Ensure assets are only saved within the save dir
    asset_path = Path(asset_path).resolve().relative_to("/")
    asset_save_path = Path("assets") / asset_path

    save_data(save_dir / asset_save_path, asset_data)

    return asset_save_path


def save_assets(soup, root_url, tag, attr, save_dir):
    # TODO: Save assets from CSS files [url(...)]
    for asset in soup.find_all(tag):
        if not asset.get(attr, None):
            continue

        if asset[attr].startswith("data:"):
            continue

        asset[attr] = convert_to_full_url(
            root_url,
            asset[attr],
        )

        asset_filepath = save_asset(asset[attr], save_dir)
        if asset_filepath:
            asset[attr] = quote(str(asset_filepath))


def fetch_url(url, metadata, download_js):
    r = requests.get(url, headers=REQ_HEADERS)
    r.raise_for_status()
    save_dir = Path(quote(re.sub(r"http://|https://", "", url), safe=""))
    filepath = save_dir / "page.html"

    try:
        last_modified = os.path.getmtime(filepath)
    except FileNotFoundError:
        last_modified = None

    soup = BeautifulSoup(r.text, features="html.parser")
    root_url = urlparse(url).scheme + "://" + urlparse(url).hostname
    for tag, attr in TAG_SRC_ATTR.items():
        if tag == "script" and not download_js:
            continue

        save_assets(soup, root_url, tag, attr, save_dir)

    save_data(filepath, str(soup).encode())
    print(f"Saved {url} to the {save_dir} directory")

    if metadata:
        if last_modified:
            last_modified = datetime.datetime.fromtimestamp(last_modified, datetime.UTC)
            last_modified = last_modified.strftime("%a %b %d %Y %H:%M %Z")

        print(
            f"site: {url}\n" +
            f"num_links: {len(soup.find_all('a'))}\n" +
            f"images: {len(soup.find_all('img'))}\n" +
            f"last_fetch: {last_modified}\n"
        )


def is_valid_url(url):
    if not url.startswith(("http://", "https://")):
        print(f"{url} is not a valid url", file=sys.stderr)
        return False
    return True


def fetch_urls(urls, metadata, download_js):
    for url in urls:
        if not is_valid_url(url):
            continue

        try:
            fetch_url(url, metadata, download_js)
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
    parser.add_argument(
        "--download-js",
        action=argparse.BooleanOptionalAction,
        help="Download JS assets",
    )
    args = parser.parse_args()
    fetch_urls(args.urls, args.metadata, args.download_js)


if __name__ == "__main__":
    main()
