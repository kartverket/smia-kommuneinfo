#!/usr/bin/env python3
"""
Generates an open-api spec from the endpoints and models.
"""

from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
import config as cf

scheme = "http" if cf.is_dev else "https"

spec = APISpec(
    title='Åpent API fra Kartverket for administrative enheter',
    version='1.2',
    openapi_version='3.0.3',
    info=dict(
        description="""
I dette APIet finner du data om administrative enheter, spesifikt fylker og kommuner.
APIet gir blant annet informasjon som navn, nummer, område og representasjonspunkter.

Det er ikke nødvendig med innlogging/autorisasjon for å bruke APIet.

Medio desember 2023 ble APIet flyttet til et nytt endepunkt som er tilgjengelig på <a href="https://api.kartverket.no/kommuneinfo/v1">https://api.kartverket.no/kommuneinfo/v1</a>.
Det tidligere endepunktet <a href="https://ws.geonorge.no/kommuneinfo/v1">https://ws.geonorge.no/kommuneinfo/v1</a> vil være tilgjengelig inntil videre, og vil fungere som en proxy til det nye endepunktet.
Vi anbefaler likevel å bytte til det nye endepunktet.

Dersom det finnes relevante testdata for APIet vil dette bli tilgjengeliggjort på <a href="https://api.test.kartverket.no/kommuneinfo/v1">https://api.test.kartverket.no/kommuneinfo/v1</a>.
Testmiljøet kan for eksempel brukes til å legge ut nye data før de inntreffer. Eksempelvis ble data for 2024 lagt ut medio desember 2023.
Slike endringer på testmiljø vil ikke nødvendigvis forhåndsannonseres, men vil bli annonsert på <a href="https://status.kartverket.no">https://status.kartverket.no</a> når det blir gjort endringer.

Større eller ikke-kompatible endringer i APIet vil bli annonsert med minst 3 måneder forvarsel på <a href="https://status.kartverket.no">https://status.kartverket.no</a>.

I tillegg til å leveres som API, kan hele datasettet for henholdsvis fylker og kommuner lastes ned fra Geonorge:


<a href="https://kartkatalog.geonorge.no/metadata/administrative-enheter-fylker/6093c8a8-fa80-11e6-bc64-92361f002671">Fylker</a>

<a href="https://kartkatalog.geonorge.no/metadata/administrative-enheter-kommuner/041f1e6e-bdbc-4091-b48f-8a5990f3cc5b">Kommuner</a> """
    ),
    servers=[
        dict(
            url=scheme+"://"+cf.app_ingress+cf.basepath
        )
    ],
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)
