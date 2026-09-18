# Copilot instructions

## Build, run, and test

- The production runtime is Python 3.14 in Alpine. For local work, create a virtual environment and
  install all runtime and test dependencies:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r dev_requirements.txt
  ```
- The application requires a reachable PostgreSQL/PostGIS database populated by the separate
  `kartverket/smia-kommuneinfo-import` job. Importing `app` creates the connection pool immediately,
  so even app startup and imports that reach `app.database` need the database available.
  Configuration comes from `KOMMUNEINFO_DB_USER`, `KOMMUNEINFO_DB_PASSWORD`, and
  `KOMMUNEINFO_DB_URI`; use `config.py` as the source of truth for defaults.
- Start the development server with `flask run`. Public endpoints are mounted below
  `http://localhost:5000/kommuneinfo/v1`, including Swagger UI at that path and the generated
  specification at `/kommuneinfo/v1/openapi.json`.
- Run production-style locally with `gunicorn -c gunicorn_config.py main:app`.
- Build the same container checked by pull-request CI with:
  ```bash
  docker build -t kommuneinfo .
  ```
- Tests are live Tavern integration tests; they do not create or isolate a database. With the local
  app and database running:
  ```bash
  TAVERN_TEST_URL=http://localhost:5000/kommuneinfo/v1 pytest
  ```
- Run the integration file directly, or select one scenario by words from its `test_name`:
  ```bash
  TAVERN_TEST_URL=http://localhost:5000/kommuneinfo/v1 pytest tests/integration/test_api.tavern.yaml
  TAVERN_TEST_URL=http://localhost:5000/kommuneinfo/v1 pytest tests/integration/test_api.tavern.yaml -k "Sjekk and fungerer"
  ```
- `./run_tests.sh dev|test|prod` runs the same Tavern file against a deployed environment. There is
  no repository lint or formatting command configured.

## Architecture

- `main.py` exposes the Flask application created in `app/__init__.py`. App initialization
  configures CORS, Norwegian locale-aware sorting, JSON logging, and then imports `app/routes.py` to
  register routes.
- `app/routes.py` is the HTTP orchestration layer. A typical endpoint deserializes query parameters
  through a Marshmallow parameter schema, performs additional domain validation, builds a query
  through `app.database.Queries`, executes it through `DbConn`, then serializes and optionally
  filters the response through a Marshmallow response schema.
- `app/database.py` owns both data access layers: `Queries` builds SQL against the `kommuneinfo`
  PostgreSQL schema and PostGIS functions, while `DbConn` owns a process-wide blocking
  `ThreadedConnectionPool`, executes parameterized queries, maps cursor rows to dictionaries, and
  expands the three database name columns into `gyldigeNavn`.
- `app/models.py` defines both input and output contracts. Marshmallow `attribute` mappings bridge
  database snake_case fields to API camelCase fields such as `punktIOmrade` and
  `samiskForvaltningsomrade`.
- OpenAPI is generated at import time. `app/apispec_generate.py` configures APISpec, endpoint
  docstrings in `app/routes.py` define operations, and every documented view is explicitly
  registered with `spec.path(...)` near the bottom of that file. `app/templates/swagger-ui.html`
  displays the generated `/openapi.json`.
- `PrefixMiddleware` mounts the entire API at `config.basepath` (`/kommuneinfo/v1`). Prometheus
  metrics group dynamic route segments as `:id`; `/healthx` is process liveness and `/healthz`
  verifies the database.
- The default output SRID is EPSG:4258. Database views provide prepared JSON geometry for that
  default; requests for another `utkoordsys` use PostGIS transformations in `Queries`.

## Repository conventions

- Keep endpoint changes synchronized across the route's Marshmallow input/output schemas, SQL
  projection aliases, APISpec docstring, explicit `spec.path(...)` registration, and Tavern
  scenarios. A route alone does not become part of the generated OpenAPI document.
- Preserve Norwegian public parameter names, response fields, and error messages. Region identifiers
  are strings so leading zeroes survive (`"03"`, `"0301"`); do not coerce them to integers after
  validation.
- Accept query parameters through `deserialize_input_params` so unknown parameters consistently
  return HTTP 400. Use `Validate` for SRIDs, coordinates, region numbers, search text, and sort
  fields, and use `filter_model`/`return_jsonify_dump` for the existing `filtrer` behavior,
  including dotted nested fields.
- Keep user values separate from SQL text: `Queries` may compose repository-controlled `WHERE`
  fragments, but values must use psycopg2 `%s` placeholders and be passed to `perform_query*`. Point
  searches intentionally order input as longitude/easting first, then latitude/northing for WKT.
- Choose `perform_query_format_response` for normal tabular results and `perform_query_get_response`
  only when SQL already returns a complete JSON value, as the illustration-map query does.
- For list endpoints, validate the requested sort field before calling locale-aware
  `sorting_list_of_dicts`. Norwegian alphabetical order depends on `config.locale_choice`.
- Database query failures are translated centrally: unsupported SRIDs and projection-domain errors
  are HTTP 400, empty result sets are HTTP 404, and other database errors are HTTP 500. Ensure every
  acquired pooled connection is returned on new success and error paths.
- The two route spellings `/fylkerKommuner` and `/fylkerkommuner` are intentional compatibility
  aliases. Avoid removing or renaming public routes or fields without treating the change as an API
  compatibility change.
