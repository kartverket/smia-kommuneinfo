# syntax=docker/dockerfile:1

FROM python:3.14-alpine@sha256:5a824eb82cc75361f98611f3cfc5091ea33f10a6ccea4d4ebdabbc523b9a1614

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
