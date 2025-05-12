# syntax=docker/dockerfile:1

FROM python:3.13-alpine3.21@sha256:452682e4648deafe431ad2f2391d726d7c52f0ff291be8bd4074b10379bb89ff

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
