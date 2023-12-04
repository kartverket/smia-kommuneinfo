# syntax=docker/dockerfile:1

FROM python:3-alpine AS base
EXPOSE 5000
WORKDIR /app
# Needed for psycopg2
RUN apk add build-base postgresql-dev
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM base AS app
COPY . .

FROM app AS api
CMD [ "gunicorn", "-c" , "gunicorn_config.py", "main:app"]

FROM app AS test-runner
RUN pip3 install -r dev_requirements.txt
ARG TEST_URL
ENV TAVERN_TEST_URL = ${TEST_URL}
CMD ["pytest"]