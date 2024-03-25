# fetch CLI utility

```
usage: fetch [-h] [--metadata | --no-metadata]
             [--download-js | --no-download-js]
             URL [URL ...]

A command line program that retrieves web pages and saves them locally

positional arguments:
  URL                   The URLs of the web pages to retrieve

options:
  -h, --help            show this help message and exit
  --metadata, --no-metadata
                        Print metadata
  --download-js, --no-download-js
                        Download JS assets
```

## Running via Docker
1. Build image
    - `docker build -t github.com/kurtkerwinko/fetch:latest .`
2. Run command
    - `docker run github.com/kurtkerwinko/fetch:latest --metadata https://www.google.com`
3. Alternatively, bind current directory with the container to skip copying the save directory from the Docker container to the host
    - `docker run --rm -v .:/root github.com/kurtkerwinko/fetch:latest --metadata https://www.google.com`

## TODO
1. Save assets from CSS files [`url(...)`]
    - Use regex in CSS files to look for and download/rewrite `url(...)` function calls
2. Check if there are other content types to consider when downloading assets
3. Allow URL inputs that are missing http/https (`python fetch.py www.google.com`)
4. Debug issue where some images aren't shown when opening an HTML page locally
