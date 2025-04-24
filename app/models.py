#!/usr/bin/env python3
from marshmallow import Schema, fields


class geoJsonEpsg(Schema):
    name = fields.Str()


class geoJsonCrs(Schema):
    type = fields.Str()
    properties = fields.Nested(geoJsonEpsg)


class geoJsonStandard(Schema):
    type = fields.Str()
    crs = fields.Nested(geoJsonCrs)


class geoJson(geoJsonStandard):
    coordinates = fields.List(fields.Float)


class geoJsonPoly(geoJsonStandard):
    coordinates = fields.List(fields.List(fields.List(fields.Float)))


class geoJsonRaw(geoJsonStandard):
    coordinates = fields.List(fields.Raw)


class NavnFull(Schema):
    prioritet = fields.Integer()
    navn = fields.Str()
    sprak = fields.Str()


class KomEnkel(Schema):
    kommunenummer = fields.Str(
        metadata={'description': 'Nummerering av kommuner. Tekstverdi som må bestå av 4 tall. 0301 er for eksempel gyldig, mens 301 er ikke gyldig.'}
    )
    kommunenavn = fields.Str()


class KomEnkelNorskNavn(KomEnkel):
    kommunenavnNorsk = fields.Str()


class KomEnkelOmrade(KomEnkel):
    omrade = fields.Nested(geoJsonRaw)


class geoJsonFeature(Schema):
    type = fields.Str()
    properties = fields.Nested(KomEnkel)
    geometry = fields.Nested(geoJsonRaw)


class geoJsonFeatureCollection(Schema):
    type = fields.Str()
    features = fields.Nested(geoJsonFeature, many=True)


class FylkerEnkel(Schema):
    fylkesnummer = fields.Str(
        metadata={'description': 'Nummerering av fylke. Tekstverdi som må bestå av 2 tall. 03 er for eksempel gyldig, mens 3 er ikke gyldig.'})
    fylkesnavn = fields.Str(metadata={'description': 'Navn (norsk) på et fylke'})


class FylkerEnkelOmrade(FylkerEnkel):
    omrade = fields.Nested(geoJsonRaw)


class KommuneFylkeEnkel(KomEnkel, FylkerEnkel):
    pass


class FylkerKommunerEnkel(FylkerEnkel):
    avgrensningsboks = fields.Nested(geoJsonPoly)
    kommuner = fields.Nested(KomEnkel, many=True)


class KomFull(KomEnkel, FylkerEnkel):
    kommunenavnNorsk = fields.Str()
    samiskForvaltningsomrade = fields.Boolean(
        attribute='samiskforvaltningsomrade')
    punktIOmrade = fields.Nested(geoJson, attribute='punkt_i_omrade')
    gyldigeNavn = fields.Nested(NavnFull, many=True)
    avgrensningsboks = fields.Nested(geoJsonPoly)


class FylkerKommunerFull(FylkerEnkel):
    avgrensningsboks = fields.Nested(geoJsonPoly)
    kommuner = fields.Nested(KomFull, many=True)


class NavnSokKommune(Schema):
    antallTreff = fields.Integer()
    kommuner = fields.Nested(KomFull, many=True)


class ParamsFilter(Schema):
    filtrer = fields.Str(
        metadata={'description': 'Kommaseparert liste med de objektene du ønsker å få returnert. For å hente ut underobjekter bruk "."-notasjon, f.eks.: &filtrer=kommuner.kommunenummer,fylkesnavn'})


class ParamsSort(Schema):
    sorter = fields.Str(metadata={'description': 'Sorter resultat etter felt.'})


class ParamsSridOut(Schema):
    utkoordsys = fields.Integer(
        metadata={'description': 'Angi det koordinatsystemet som du ønsker at geometrien i returen skal transformeres til. Standard er 4258.'})


class ParamsSorterKomFylk(Schema):
    sorterkommuner = fields.Str(
        metadata={'description': 'Sorter listen med kommuner etter felt.'})
    sorterfylker = fields.Str(
        metadata={'description': 'Sorter listen med fylker etter felt.'})


class ParamsStandard(ParamsFilter, ParamsSort):
    pass


class ParamsFylkesnummer(Schema):
    fylkesnummer = fields.Str(
        metadata={'description': 'Fylkesnummer bestående av 2 tegn, med ledende null om nødvendig.', 'required': True})


class ParamsKommunenummer(Schema):
    kommunenummer = fields.Str(
        metadata={'description': 'kommunenummer bestående av 4 tegn, med ledende null om nødvendig.', 'required': True})


class ParamsNavnSok(ParamsStandard, ParamsSridOut):
    # \ will not show in the OpenAPI spec, removing from description to avoid extra comma
    knavn = fields.Str(
        required=True, metadata={'description': "Kommunenavnet du ønsker å søke etter. Wildcard (*) kan benyttes i søket. Spesialtegnene \", \', ;, /, og = kan ikke brukes"})


class ParamsKomFylk(ParamsFilter, ParamsSridOut, ParamsSorterKomFylk):
    pass


class ParamsPunktSok(ParamsFilter):
    nord = fields.Float(required=True, metadata={'description': "nord/latitude-koordinaten"})
    ost = fields.Float(required=True, metadata={'description': "øst/longitude-koordinaten"})
    koordsys = fields.Integer(
        required=True, metadata={'description': "Koordinatsystemet til koordinatene du søker med. Angis som en SRID, for eksempel 4258 eller 25833."})


class ParamsStandardKoordsys(ParamsFilter, ParamsSridOut):
    pass
