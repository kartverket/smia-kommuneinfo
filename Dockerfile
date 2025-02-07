# syntax=docker/dockerfile:1

FROM python:3-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

EXPOSE 5000

WORKDIR /app

COPY requirements.txt requirements.txt

# Needed for psycopg2
RUN apk add build-base postgresql-dev --no-cache

RUN pip3 install -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

CMD [ "gunicorn", "-c" , "gunicorn_config.py", "main:app"]
