# syntax=docker/dockerfile:1

FROM python:3.14-alpine@sha256:003970a263347645cd23d4f90929ad16ba7ce7d808ee4674ffcc93cb21cc289f

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
