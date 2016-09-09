FROM python:2.7-alpine
MAINTAINER Andrew Ekstedt <ekstedta@oregonstate.edu>

RUN pip install gunicorn

COPY requirements.txt /src/requirements.txt
RUN apk update \
    && apk add build-base openssl-dev libffi-dev \
    && pip install -r /src/requirements.txt  \
    && apk add openssl libffi \
    && apk del build-base openssl-dev libffi-dev

COPY ["setup.py", "consent.py", "/src/"]
COPY templates /src/templates/
RUN pip install -e /src

ENV CONSENT_CONFIG /src/config.py
ENV TZ America/Los_Angeles
USER nobody
CMD ["gunicorn", "--bind", ":8000", "consent:app"]
