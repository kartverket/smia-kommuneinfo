
import logging
import signal
import sys
from flask import abort
import config as cf
from psycopg2.pool import ThreadedConnectionPool as _ThreadedConnectionPool
from threading import Semaphore


logger = logging.getLogger(__name__)


# ThreadedConnectionPool doesn't have any blocking functionality for getconn(), when maxconn is exceeded 
# https://stackoverflow.com/questions/48532301/python-postgres-psycopg2-threadedconnectionpool-exhausted/49366850#49366850
# Also adding signal handling if Kubernetes kills a container
class ThreadedConnectionPool(_ThreadedConnectionPool):
    def __init__(self, minconn, maxconn, *args, **kwargs):
        self._semaphore = Semaphore(maxconn)
        super().__init__(minconn, maxconn, *args, **kwargs)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def getconn(self, *args, **kwargs):
        self._semaphore.acquire()
        try:
            return super().getconn(*args, **kwargs)
        except:
            self._semaphore.release()
            raise
    
    def handle_signal(self, sig, frame):
        exit_status = 0
        logger.info("Recieved signal: {}. Closing all db-connection(s)".format(signal.Signals(sig).name))

        try:
            self.closeall()
        except Exception as e:
            logger.error(e)
            exit_status = 1
        sys.exit(exit_status)

    def putconn(self, *args, **kwargs):
        try:
            super().putconn(*args, **kwargs)
        finally:
            self._semaphore.release()

    def closeall(self):
        return super().closeall()


class DbConn():
    """Connect to the db, perform a query and format the response"""  

    pool = ThreadedConnectionPool(
                minconn=cf.min_db_connections, maxconn=cf.max_db_connections,
                dsn=cf.db_uri, user=cf.db_user, password=cf.db_password
            )
    
    def get_db_connection(self):
        try:
            return self.pool.getconn()
        except Exception as e:
            logger.error(
                "Exception under databaseconnection: {}".format(e))
            abort(500, "Noe gikk galt, prøv igjen senere")  

    def perform_query_format_response(self, query, userInput=False):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        queryResult = self.perform_query(connection, cursor, query, userInput)
        out = self.format_response(cursor, queryResult)
        self.pool.putconn(connection)
        return self.format_names(out)

    def perform_query_get_response(self, query, userInput=False):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        queryResult = self.perform_query(connection, cursor, query, userInput)
        self.pool.putconn(connection)
        return queryResult
    
    def abort_with_db_release(self, db_connection, status_code, message=None):
        if db_connection is not None:
            self.pool.putconn(db_connection)
        abort(status_code, message)

    def perform_query(self, connection, cursor, query, userInput=False):
        """userInput is included here because of protection against sql-injection when
        the parameters are inserted as a tuple in the cur.execute-command.
        """

        logger.debug('Query to execute: %s. With input: %s' %
                    (query, userInput))
        
        if not isinstance(userInput, tuple):
            userInput = (userInput,)
        try:
            if userInput:
                cursor.execute(query, userInput)
            else:
                cursor.execute(query)
        except Exception as e:
            logger.error(
                'Encountered exception when performing query: %s' % e)
            if "Cannot find SRID" in str(e):
                self.abort_with_db_release(connection, 400, "Koordinatsystemet/SRID er ikke støttet.")
            else:
                self.abort_with_db_release(connection, 500)
        result = cursor.fetchall()
        logger.debug('Query result: %s' % result)
        if len(result) == 0:
            self.abort_with_db_release(connection, 404, "Ingen treff, sjekk parameterene.")
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

    def format_response(self, cursor, query_result):
        outList = []

        for row in query_result:
            tempDict = {}
            for index, data in enumerate(row):
                colName = cursor.description[index][0]
                tempDict[colName] = data
            outList.append(tempDict)
        return outList



class Queries:

    def __init__(self, to_srid=cf.defSrid, default_srid=cf.defSrid):
        self.to_srid = to_srid
        self.default_srid = default_srid

    def readiness():
        return 'SELECT 1;'

    def kom_fylke_enkel(self, where=''):
        return """SELECT kommunenummer,
                         navn_pri_1 as kommunenavn,
                         fylkesnummer,
                         fylkesnavn
                  FROM kommuneinfo.kommune {0};""".format(where)

    def kom_enkel(self, where=''):
        return """SELECT kommunenummer,
                         navn_pri_1 as kommunenavn,
                         navn_norsk as "kommunenavnNorsk"
                  FROM kommuneinfo.kommune {0};""".format(where)

    def kom_illustrasjonskart(self):
        if self.to_srid == self.default_srid:
            return """SELECT featurecollection
                        FROM kommuneinfo.illustrasjonskart_json;"""
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
                    SELECT * FROM kommuneinfo.illustrasjonskart) inputs) features;""".format(self.to_srid)

    def fylke_enkel(self, where=''):
        return """SELECT fylkesnummer, navn_pri_1 as fylkesnavn
                    FROM kommuneinfo.fylke {0} """.format(where)

    def fylke_full(self, where=''):
        # save about 50 milliseconds by retrieving the prepared JSON-rows
        if self.to_srid == self.default_srid:
            geomCols = """bbox_json AS avgrensningsboks"""
        else:
            geomCols = """ST_AsGeoJSON(ST_Envelope(ST_Transform(fylke.omrade, {0})), 15, 2)::json AS avgrensningsboks""".format(
                self.to_srid)
        return """SELECT fylkesnummer,
                    navn_pri_1 as fylkesnavn,
                    {1}
                FROM kommuneinfo.fylke {0};""".format(where, geomCols)

    def kom_neighbours(self):
        return """SELECT b.kommunenummer, b.navn_pri_1 as kommunenavn,
                    b.navn_norsk as "kommunenavnNorsk"
                   FROM kommuneinfo.kommune as a,
                        kommuneinfo.kommune as b
                   WHERE ST_Intersects(a.omraade, b.omraade)
                   AND a.kommunenummer != b.kommunenummer
                   AND a.kommunenummer = %s;"""

    def kom_full(self, where=''):
        # save about 50 milliseconds by retrieving the prepared JSON-rows
        if self.to_srid == self.default_srid:
            geomCols = """kommune.punkt_i_omraade_json AS punkt_i_omrade,
                       kommune.bbox_json AS avgrensningsboks"""
        else:
            geomCols = """ST_AsGeoJSON(ST_Transform(kommune.punkt_i_omraade, {0}), 15, 2)::json AS punkt_i_omrade,
                    ST_AsGeoJSON(ST_Envelope(ST_Transform(kommune.omraade, {0})), 15, 2)::json AS avgrensningsboks""".format(self.to_srid)
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
                FROM kommuneinfo.kommune {0};""".format(where, geomCols)

    def kom_polygon(self, where=''):
        return """SELECT kommunenummer,
                        navn_pri_1 AS kommunenavn,
                        ST_AsGeoJSON(ST_Transform(kommune.omraade, {1}), 15, 2)::json AS omrade
                    FROM kommuneinfo.kommune {0};""".format(where, self.to_srid)

    def fylke_polygon(self, where=''):
        return """SELECT fylkesnummer,
                        navn_pri_1 AS fylkesnavn,
                        ST_AsGeoJSON(ST_Transform(fylke.omrade, {1}), 15, 2)::json AS omrade
                    FROM kommuneinfo.fylke {0};""".format(where, self.to_srid)
