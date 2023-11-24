#!/usr/bin/env python3
"""
Generates an open-api spec from the endpoints and models.
"""

import os
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
import config as cf

is_dev = True if os.environ.get('FLASK_DEBUG') == "1" else False

host = cf.app_ingress
basepath = "/" if is_dev else "/kommuneinfo/v1"
scheme = "http" if is_dev else "https"

spec = APISpec(
    title='Åpent API fra Kartverket for administrative enheter.',
    version='1.1.1',
    openapi_version='2.0',
    info=dict(
        description="""Api fra Kartverket som leverer informasjon om administrative enheter som fylker og kommuner.
            Det er ikke nødvendig med innlogging/autorisasjon for å bruke API-et.
            Større funksjonalitetsødeleggende endringer i API-et vil bli annonsert minst 3 måneder i forveien på https://geonorge.no/aktuelt/varsler/Tjenestevarsler/
            Hvis man ønsker å hente ned hele datasettet så anbefales det å laste ned filene som er tilgjengeliggjort via https://geonorge.no.
        """
    ),
    consumes=["application/json"],
    produces=["application/json"],
    host=host,
    basePath=basepath,
    schemes=[scheme],
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)
