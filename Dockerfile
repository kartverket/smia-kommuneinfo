# syntax=docker/dockerfile:1

FROM python:3.13.7-alpine3.21@sha256:8f70fe393f5f8ba6c28f24e8f0670d62ae1dcdf3d73bc5f0a849d5764496dd34

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

EXPOSE 5000

WORKDIR /app

COPY requirements.txt requirements.txt

# Needed for psycopg2
RUN apk update && \
    apk upgrade && \
    apk add --no-cache build-base postgresql-dev && \
    rm -rf /var/cache/apk/*

RUN pip3 install -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

CMD [ "gunicorn", "-c" , "gunicorn_config.py", "main:app"]
