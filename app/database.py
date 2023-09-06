
import logging

from flask import abort
import psycopg2

import config as cf


logging = logging.getLogger(__name__)


class DbConn():
    """Connect to the db, perform a query and format the response"""

    def __init__(self, dbc):
        self.conn = psycopg2.connect(**dbc)
        self.cur = self.conn.cursor()

    def perform_query_format_response(self, query, userInput=False):
        queryResult = self.perform_query(query, userInput)
        out = self.format_response(queryResult)
        return self.format_names(out)

    def perform_query_get_response(self, query, userInput=False):
        queryResult = self.perform_query(query, userInput)
        return queryResult

    def perform_query(self, query, userInput=False):
        """userInput is included here because of protection against sql-injection when
        the parameters are inserted as a tuple in the cur.execute-command.
        """
        logging.debug('Query to execute: %s. With input: %s' % (query, userInput))
        if not isinstance(userInput, tuple):
            userInput = (userInput,)
        try:
            if userInput:
                self.cur.execute(query, userInput)
            else:
                self.cur.execute(query)
        except Exception as e:
            logging.error('Encountered exception when performing query: %s' % e)
            if "Cannot find SRID" in str(e):
                abort(400, "Koordinatsystemet/SRID er ikke støttet.")
            else:
                abort(500)
        result = self.cur.fetchall()
        logging.debug('Query result: %s' % result)
        if len(result) == 0:
            abort(404, "Ingen treff, sjekk parameterene.")
        return result

    def format_names(self, inputNames):
        for x in inputNames:
            navn1 = {'prioritet': 1, 'navn': None, 'sprak': None}
            navn2 = {'prioritet': 2, 'navn': None, 'sprak': None}
            navn3 = {'prioritet': 3, 'navn': None, 'sprak': None}
            for key, value in x.items():
                if key == 'navn_pri_1':
                    navn1['navn'] = value
                elif key == 'navn_pri_2':
                    navn2['navn'] = value
                elif key == 'navn_pri_3':
                    navn3['navn'] = value
                if key == 'navn_pri_1_sprak':
                    navn1['sprak'] = value
                elif key == 'navn_pri_2_sprak':
                    navn2['sprak'] = value
                elif key == 'navn_pri_3_sprak':
                    navn3['sprak'] = value
            x['gyldigeNavn'] = [navn1, navn2, navn3]
        return inputNames

    def format_response(self, query_result):
        outList = []
        for row in query_result:
            tempDict = {}
            for index, data in enumerate(row):
                colName = self.cur.description[index][0]
                tempDict[colName] = data
            outList.append(tempDict)
        return outList

    def __del__(self):
        """close connection if not already done"""
        if self.conn:
            self.conn.close()


class Queries:

    def __init__(self, toSrid=cf.defSrid, fromSrid=cf.defSrid):
        self.toSrid = toSrid
        self.fromSrid = fromSrid

    def kom_fylke_enkel(self, where=''):
        return """SELECT kommunenummer,
                         navn_pri_1 as kommunenavn,
                         fylkesnummer,
                         fylkesnavn
                  FROM matview_kommuner {0};""".format(where)

    def kom_enkel(self, where=''):
        return """SELECT kommunenummer,
                         navn_pri_1 as kommunenavn,
                         navn_norsk as "kommunenavnNorsk"
                  FROM matview_kommuner {0};""".format(where)

    def kom_illustrasjonskart(self):
        if self.toSrid == 4258:
            return """SELECT featurecollection
                        FROM matview_api_kommuner_illustrasjonskart_geojson;"""
        return """SELECT jsonb_build_object(
                    'type',     'FeatureCollection',
                    'features', jsonb_agg(features.feature)
                ) as featurecollection
                FROM (
                  SELECT jsonb_build_object(
                    'type',       'Feature',
                    'geometry',   ST_AsGeoJSON(ST_Transform(omrade, {0}), 3, 2)::jsonb,
                    'properties', jsonb_build_object('kommunenummer', kommunenummer,
                                                     'kommunenavn', kommunenavn )
                  ) AS feature
                  FROM (
                    SELECT * FROM matview_api_kommuner_illustrasjonskart) inputs) features;""".format(self.toSrid)

    def fylke_enkel(self, where=''):
        return """SELECT fylkesnummer, navn_pri_1 as fylkesnavn
                    FROM matview_fylker {0} """.format(where)

    def fylke_full(self, where=''):
        # save about 50 milliseconds by retrieving the prepared JSON-rows
        if self.toSrid == self.fromSrid:
            geomCols = """bbox_json AS avgrensningsboks"""
        else:
            geomCols = """ST_AsGeoJSON(ST_Envelope(ST_Transform(omrade, {0})), 15, 2)::json AS avgrensningsboks""".format(self.toSrid)
        return """SELECT fylkesnummer,
                    navn_pri_1 as fylkesnavn,
                    {1}
                FROM matview_fylker {0};""".format(where, geomCols)

    def kom_neighbours(self):
        return """SELECT b.kommunenummer, b.navn_pri_1 as kommunenavn,
                    b.navn_norsk as "kommunenavnNorsk"
                   FROM matview_kommuner as a,
                        matview_kommuner as b
                   WHERE ST_Intersects(a.omrade, b.omrade)
                   AND a.kommunenummer != b.kommunenummer
                   AND a.kommunenummer = %s;"""

    def kom_full(self, where=''):
        # save about 50 milliseconds by retrieving the prepared JSON-rows
        if self.toSrid == self.fromSrid:
            geomCols = """punkt_i_omrade_json AS punkt_i_omrade,
                       bbox_json AS avgrensningsboks"""
        else:
            geomCols = """ST_AsGeoJSON(ST_Transform(punkt_i_omrade, {0}), 15, 2)::json AS punkt_i_omrade,
                    ST_AsGeoJSON(ST_Envelope(ST_Transform(omrade, {0})), 15, 2)::json AS avgrensningsboks""".format(self.toSrid)
        return """SELECT kommunenummer,
                    samiskforvaltningsomrade,
                    fylkesnavn,
                    fylkesnummer,
                    navn_pri_1,
                    navn_pri_1 as kommunenavn,
                    navn_pri_2,
                    navn_pri_3,
                    navn_pri_1_sprak,
                    navn_pri_2_sprak,
                    navn_pri_3_sprak,
                    navn_norsk as "kommunenavnNorsk",
                    {1}
                FROM matview_kommuner {0};""".format(where, geomCols)

    def kom_polygon(self, where=''):
        return """SELECT kommunenummer,
                        navn_pri_1 AS kommunenavn,
                        ST_AsGeoJSON(ST_Transform(omrade, {1}), 15, 2)::json AS omrade
                    FROM matview_kommuner {0};""".format(where, self.toSrid)

    def fylke_polygon(self, where=''):
        return """SELECT fylkesnummer,
                        navn_pri_1 AS fylkesnavn,
                        ST_AsGeoJSON(ST_Transform(omrade, {1}), 15, 2)::json AS omrade
                    FROM matview_fylker {0};""".format(where, self.toSrid)