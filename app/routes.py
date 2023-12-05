#!/usr/bin/env python3
"""
TODO:
-Just do one query and join in the database.
"""

import locale
import logging

from marshmallow import ValidationError

from flask import request, jsonify, abort, make_response, render_template

from app import app
from app import models as md
import config as cf
from app import database as db
from app import apispec_generate

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.WARNING)


class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This route does not exist.".encode()]


app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/kommuneinfo/v1')


class Validate:

    def srid(self, srid):
        if not srid:
            srid = str(cf.defSrid)
        if srid.lower().startswith('epsg:'):
            srid = srid.lower().split('epsg:')[1]
        try:
            return int(srid)
        except Exception as e:
            logging.warning('Invalid epsg-parameter: %s' % e)
            abort(400, "Feil i koordinatsystem-parameterene.")

    def lat_lon(self, lat, lon):
        try:
            return float(lat), float(lon)
        except Exception as e:
            logging.warning('Invalid lat/lon-parameters: %s' % e)
            abort(400, "Feil i parameterene.")

    def search_string(self, search):
        invalidChars = ('"', "'", ";", "/", '\\', '=')
        noWildcard = search.replace('*', '')
        if len(noWildcard) <= 1:
            abort(400, 'Søkestreng er for kort.')
        elif any((char in invalidChars) for char in noWildcard):
            abort(400, 'Ugyldige tegn i søkestreng.')
        return search

    def regionsnummer(self, nummer):
        """Might have preceding 0, which we need to preserve"""
        try:
            int(nummer)
            return nummer
        except Exception as e:
            logging.warning('Invalid regionsnummer: %s' % e)
            abort(400, "Feil i parameterene.")

    def orderByField(self, valueToCheck, dictOrListOfDictsToCheckAgainst):
        logging.info('value to check, orderby-field: "%s"' % valueToCheck)
        if valueToCheck is None:
            return None
        if isinstance(dictOrListOfDictsToCheckAgainst, dict):
            listToCheck = list(dictOrListOfDictsToCheckAgainst.keys())
        else:  # if list of dicts
            listToCheck = list(dictOrListOfDictsToCheckAgainst[0].keys())
        logging.info('liste å sjekke mot: %s' % listToCheck)
        if not any(valueToCheck == x for x in listToCheck):
            abort(make_response(jsonify(message="Ugyldige sorterings-parametere: %s."
                                        " Mulige årsaker: Skrivefeil. Sortering på flere felt er ikke tillatt."
                                        " Noen felter kan ikke sorteres på. " % valueToCheck), 400))


def combine_all_fylker_kommuner(fylkDict, komDict):
    """Add list of kommuner to the correct fylke in list of fylker"""
    dictFylkesnummer = {}
    for x in fylkDict:
        y = x.get('fylkesnummer')
        dictFylkesnummer[y] = []

    for x in komDict.get('kommuner'):
        y = x.get('fylkesnummer')
        listKommuner = dictFylkesnummer.get(y)
        listKommuner.append(x)

    for x in fylkDict:
        y = x.get('fylkesnummer')
        listKommuner = dictFylkesnummer.get(y)
        x['kommuner'] = listKommuner
    return fylkDict


def filter_model(modelMa, filterDict):
    try:
        return modelMa(**filterDict)
    except (ValueError, KeyError) as e:
        logging.debug(e)
        abort(400, "Feil i filtreringsparameter")


def create_filtering_dict(filterInput):
    inp = filterInput.get('filtrer')
    if inp:
        inclDict = {'only': inp.split(',')}
    else:
        inclDict = {}
    logging.debug('filtering Dict: %s' % inclDict)
    return inclDict


def deserialize_input_params(inputParams, modelObj):
    """
    inputParams should be a dict.
    modelObj should be a marshmallow model
    """
    logging.info('input params to deserialize: %s' % inputParams)
    if not inputParams:
        return {}
    try:
        deserializedParams = modelObj.load(inputParams)
    except ValidationError:
        abort(400, "Query params: {} ble ikke kjent igjen, gyldige paramtere er: {}".format(list(inputParams.keys()),
                                                                                            list(modelObj.dump_fields.keys())))
    logging.info('deserializedParams:  \n %s' % deserializedParams)
    return deserializedParams


def return_jsonify_dump(outSchema, outDict, many=False):
    try:
        return jsonify(outSchema.dump(outDict, many=many))
    except KeyError as e:
        logging.debug(e)
        abort(400, "Feil i filtreringsparameter. Husk på at underelementer må spesifiseres slik: filtrer=kommuner.kommunenummer")


def sorting_list_of_dicts(listOfDicts, sortByKeyName):
    logging.debug('Trying to sort "%s" by key "%s"' %
                  (listOfDicts, sortByKeyName))
    if sortByKeyName is None:
        return listOfDicts
    try:
        return sorted(listOfDicts, key=lambda t: locale.strxfrm(t[sortByKeyName]))
    except TypeError as e:
        logging.warning(
            'User probably tried to sort by key which points to a dict/list: %s' % e)
        abort(make_response(jsonify(
            message="Feil i sorterings-parameterene: %s. Felt må peke på verdi. " % sortByKeyName), 400))


def order_fields(result):
    orderBy = request.args.get('sorter')
    logging.debug('sorter: %s' % orderBy)
    if orderBy:
        Validate().orderByField(orderBy, result)
        return sorting_list_of_dicts(result, orderBy)
    return result


@app.route('/fylker')
def get_fylker():
    """Fylker i Norge.
    ---
    get:
        summary: Fylker i Norge.
        description: Oversikt over alle fylker i Norge med fylkesnavn og fylkesnummer.
        parameters:
            - in: query
              schema: ParamsStandard
        responses:
            200:
                description: OK
                schema: 
                    type: array
                    items: FylkerEnkel
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsStandard())
    filters = create_filtering_dict(validParams)
    query = db.Queries().fylke_enkel()
    dbObj = db.DbConn()
    output = dbObj.perform_query_format_response(query)
    filterModel = filter_model(md.FylkerEnkel, filters)
    sortedResult = order_fields(output)
    return return_jsonify_dump(filterModel, sortedResult, many=True)


@app.route('/fylker/<string:fylkesnummer>')
def get_kommuner_in_fylke(fylkesnummer):
    """Vis mer informasjon om et fylke, inkludert kommuner i fylket.
    ---
    get:
        summary: Vis mer informasjon om et fylke, inkludert kommuner i fylket.
        description: Vis mer informasjon om et fylke, inkludert kommuner i fylket.
        parameters:
            - in: path
              schema: ParamsFylkesnummer
            - in: query
              schema: ParamsStandardKoordsys
        responses:
            200:
                description: OK
                schema: FylkerKommunerEnkel
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsStandardKoordsys())
    fylkesnummer = Validate().regionsnummer(fylkesnummer)
    outSrid = Validate().srid(request.args.get('utkoordsys'))
    filters = create_filtering_dict(validParams)
    dbObj = db.DbConn()
    query = db.Queries().kom_enkel(where="WHERE fylkesnummer = %s")
    kommResult = dbObj.perform_query_format_response(query, fylkesnummer)
    kommOutDict = {}
    kommOutDict['kommuner'] = order_fields(kommResult)

    query2 = db.Queries(toSrid=outSrid).fylke_full(
        where="WHERE fylkesnummer = %s")
    fylkeResult = dbObj.perform_query_format_response(query2, fylkesnummer)[0]
    filterModel = filter_model(md.FylkerKommunerEnkel, filters)
    output = fylkeResult.copy()
    output.update(kommOutDict)
    return return_jsonify_dump(filterModel, output, many=False)


@app.route('/fylker/<string:fylkesnummer>/omrade')
def get_fylke_polygon(fylkesnummer):
    """Områdepolygon for et spesifikt fylke
    ---
    get:
        summary: Områdepolygon for et spesifikt fylke
        description: Områdepolygon for et spesifikt fylke
        parameters:
            - in: path
              schema: ParamsFylkesnummer
            - in: query
              schema: ParamsStandardKoordsys
        responses:
            200:
                description: OK
                schema: FylkerEnkelOmrade
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsStandardKoordsys())
    fylkesnummer = Validate().regionsnummer(fylkesnummer)
    outSrid = Validate().srid(request.args.get('utkoordsys'))
    filters = create_filtering_dict(validParams)
    query = db.Queries(toSrid=outSrid).fylke_polygon(
        where="WHERE fylkesnummer = %s")
    output = db.DbConn().perform_query_format_response(query, fylkesnummer)[0]
    filterModel = filter_model(md.FylkerEnkelOmrade, filters)
    return return_jsonify_dump(filterModel, output, many=False)


@app.route('/fylkerKommuner')
@app.route('/fylkerkommuner')
def fylker_kommuner_full():
    """Full info om alle fylker og alle kommuner
    ---
    get:
        summary: Full informasjon om alle fylker og alle kommuner.
        description: Full informasjon om alle fylker og alle kommuner.
        parameters:
            - in: query
              schema: ParamsKomFylk
        responses:
            200:
                description: OK
                schema: 
                    type: array
                    items: FylkerKommunerFull
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsKomFylk())
    orderKomBy = request.args.get('sorterkommuner')
    orderFylkBy = request.args.get('sorterfylker')
    outSrid = Validate().srid(request.args.get('utkoordsys'))
    filters = create_filtering_dict(validParams)
    dbObj = db.DbConn()
    # get kommuner
    query = db.Queries(toSrid=outSrid).kom_full()
    kommResult = dbObj.perform_query_format_response(query)
    Validate().orderByField(orderKomBy, kommResult)
    kommOutDict = {}
    kommOutDict['kommuner'] = sorting_list_of_dicts(kommResult, orderKomBy)
    # get fylker
    query2 = db.Queries(toSrid=outSrid).fylke_full()
    fylkeResult = dbObj.perform_query_format_response(query2)
    Validate().orderByField(orderFylkBy, fylkeResult)
    filterModel = filter_model(md.FylkerKommunerFull, filters)
    fylkeResult = sorting_list_of_dicts(fylkeResult, orderFylkBy)
    output = combine_all_fylker_kommuner(fylkeResult, kommOutDict)
    return return_jsonify_dump(filterModel, output, many=True)


@app.route('/kommuner')
def get_kommuner():
    """Kommuner i Norge.
    ---
    get:
        summary: Kommuner i Norge.
        description: Kommunenavn og kommunenummer for alle kommuner i Norge.
        parameters:
            - in: query
              schema: ParamsStandard
        responses:
            200:
                description: OK
                schema: 
                    type: array
                    items: KomEnkelNorskNavn
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsStandard())
    filters = create_filtering_dict(validParams)
    query = db.Queries().kom_enkel()
    dbObj = db.DbConn()
    output = dbObj.perform_query_format_response(query)
    sortedOutput = order_fields(output)
    filterModel = filter_model(md.KomEnkelNorskNavn, filters)
    return return_jsonify_dump(filterModel, sortedOutput, many=True)


@app.route('/kommuner/illustrasjonskart')
def get_kommuner_illustrasjonskart():
    """Illustrasjonskart over kommuner i Norge.
    ---
    get:
        summary: Illustrasjonskart over kommuner i Norge.
        description: En geojson-featurecollection med grovt forenklede kommunegrenser. Hver kommune er en feature og har kommunenavn og kommunenummer i properties-elementet. Kun ment til å brukes som et illustrasjonskart.
        parameters:
            - in: query
              schema: ParamsSridOut
        responses:
            200:
                description: OK
                schema: geoJsonFeatureCollection
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsSridOut())
    outSrid = Validate().srid(request.args.get('utkoordsys'))
    filters = create_filtering_dict(validParams)
    query = db.Queries(toSrid=outSrid).kom_illustrasjonskart()
    dbObj = db.DbConn()
    output = dbObj.perform_query_get_response(query)[0][0]
    filterModel = filter_model(md.geoJsonFeatureCollection, filters)
    return return_jsonify_dump(filterModel, output, many=False)


@app.route('/kommuner/<string:kommunenummer>')
def get_kommune(kommunenummer):
    """Full info om spesifikk kommune
    ---
    get:
        summary: Full informasjon om spesifikk kommune
        description: Full informasjon om spesifikk kommune
        parameters:
            - in: path
              schema: ParamsKommunenummer
            - in: query
              schema: ParamsStandardKoordsys
        responses:
            200:
                description: OK
                schema: KomFull
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsStandardKoordsys())
    knr = Validate().regionsnummer(kommunenummer)
    outSrid = Validate().srid(request.args.get('utkoordsys'))
    filters = create_filtering_dict(validParams)
    query = db.Queries(toSrid=outSrid).kom_full(
        where="WHERE kommunenummer = %s")
    dbObj = db.DbConn()
    output = dbObj.perform_query_format_response(query, knr)[0]
    filterModel = filter_model(md.KomFull, filters)
    return return_jsonify_dump(filterModel, output, many=False)


@app.route('/kommuner/<string:kommunenummer>/nabokommuner')
def get_neighbouring_kommune(kommunenummer):
    """Finn nabokommuner til en kommune
    ---
    get:
        summary: Finn nabokommuner til en kommune
        description: Finn nabokommuner til en kommune
        parameters:
            - in: path
              schema: ParamsKommunenummer
            - in: query
              schema: ParamsStandard
        responses:
            200:
                description: OK
                schema:
                    type: array
                    items: KomEnkelNorskNavn
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsStandard())
    knr = Validate().regionsnummer(kommunenummer)
    filters = create_filtering_dict(validParams)
    query = db.Queries().kom_neighbours()
    dbObj = db.DbConn()
    output = dbObj.perform_query_format_response(query, knr)
    sortedOutput = order_fields(output)
    filterModel = filter_model(md.KomEnkelNorskNavn, filters)
    return return_jsonify_dump(filterModel, sortedOutput, many=True)


@app.route('/kommuner/<string:kommunenummer>/omrade')
def get_kommune_polygon(kommunenummer):
    """Områdepolygon for spesifikk kommune
    ---
    get:
        summary: Områdepolygon for spesifikk kommune
        description: Områdepolygon for spesifikk kommune
        parameters:
            - in: path
              schema: ParamsKommunenummer
            - in: query
              schema: ParamsStandardKoordsys
        responses:
            200:
                description: OK
                schema: KomEnkelOmrade
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsStandardKoordsys())
    knr = Validate().regionsnummer(kommunenummer)
    outSrid = Validate().srid(request.args.get('utkoordsys'))
    filters = create_filtering_dict(validParams)
    query = db.Queries(toSrid=outSrid).kom_polygon(
        where="WHERE kommunenummer = %s")
    dbObj = db.DbConn()
    output = dbObj.perform_query_format_response(query, knr)[0]
    filterModel = filter_model(md.KomEnkelOmrade, filters)
    return return_jsonify_dump(filterModel, output, many=False)


@app.route('/punkt')
def get_kommune_for_point():
    """Finn kommune og fylke for et gitt geografisk punkt
    ---
    get:
        summary: Finn kommune og fylke for et gitt geografisk punkt
        description: Finn kommune og fylke for et gitt geografisk punkt
        parameters:
            - in: query
              schema: ParamsPunktSok
        responses:
            200:
                description: OK
                schema: KommuneFylkeEnkel
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsPunktSok())
    nord, ost = Validate().lat_lon(request.args.get('nord'), request.args.get('ost'))
    srid = Validate().srid(request.args.get('koordsys'))
    filters = create_filtering_dict(validParams)

    queryInput = ost, nord, srid, cf.defSrid

    where = """WHERE ST_Within(ST_Transform(ST_GeomFromText('POINT(%s %s)', %s), %s), kommune.omraade)"""
    query = db.Queries().kom_fylke_enkel(where)
    dbObj = db.DbConn()
    output = dbObj.perform_query_format_response(query, queryInput)[0]
    filterModel = filter_model(md.KommuneFylkeEnkel, filters)
    return return_jsonify_dump(filterModel, output, many=False)


@app.route('/sok')
def search_by_kommunenavn():
    """Søk etter kommunenavn.
    ---
    get:
        summary: Søk etter kommunenavn.
        description: Søk etter kommunenavn.
        parameters:
            - in: query
              schema: ParamsNavnSok
        responses:
            200:
                description: OK
                schema: NavnSokKommune
    """
    validParams = deserialize_input_params(request.args.to_dict(),
                                           md.ParamsNavnSok())
    sokString = Validate().search_string(request.args.get('knavn'))
    outSrid = Validate().srid(request.args.get('utkoordsys'))
    filters = create_filtering_dict(validParams)
    sokNoWildcard = sokString.replace('*', '')
    if sokString.startswith('*') and sokString.endswith('*'):
        likeString = """LIKE LOWER('%%' || %s || '%%') """
    elif sokString.startswith('*'):
        likeString = """LIKE LOWER('%%' || %s) """  # %% escapes % in postgresql
    elif sokString.endswith('*'):
        likeString = """LIKE LOWER(%s || '%%') """
    else:
        likeString = """LIKE LOWER(%s) """
    query = db.Queries(toSrid=outSrid).kom_full(where='''WHERE LOWER(navn_pri_1) {0}
                                       OR LOWER(navn_pri_2) {0}
                                        OR LOWER(navn_pri_3) {0}'''.format(likeString))
    dbObj = db.DbConn()
    userInput = sokNoWildcard, sokNoWildcard, sokNoWildcard
    output = dbObj.perform_query_format_response(query, userInput)
    filterModel = filter_model(md.NavnSokKommune, filters)
    sortedOutput = order_fields(output)
    finalRes = {}
    finalRes['antallTreff'] = len(sortedOutput)
    finalRes['kommuner'] = sortedOutput
    return return_jsonify_dump(filterModel, finalRes, many=False)


spec = apispec_generate.spec


with app.test_request_context():
    spec.path(view=get_fylker)
    spec.path(view=get_kommuner_in_fylke)
    spec.path(view=get_fylke_polygon)
    spec.path(view=fylker_kommuner_full)
    spec.path(view=get_kommuner)
    spec.path(view=get_kommuner_illustrasjonskart)
    spec.path(view=get_kommune)
    spec.path(view=get_neighbouring_kommune)
    spec.path(view=get_kommune_polygon)
    spec.path(view=get_kommune_for_point)
    spec.path(view=search_by_kommunenavn)


# this is where it was originally placed
@app.route('/static/openapi_doc.json')
@app.route('/openapi.json')
def openapi_json():
    return jsonify(spec.to_dict())


@app.route('/')
@app.route('/index.html')
def swagger_ui():
    return render_template('swagger-ui.html')
