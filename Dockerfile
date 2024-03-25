FROM python:3.11

WORKDIR /root

COPY fetch.py /usr/bin/fetch
RUN chmod +x /usr/bin/fetch

# Symlinking as the python3 env uses a separate env from the pip3 command below
RUN ln -sf /usr/local/bin/python /bin/python3

RUN apt update && apt install -y libmagic1
COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENTRYPOINT ["/usr/bin/fetch"]
CMD ["--help"]
