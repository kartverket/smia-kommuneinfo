CREATE MATERIALIZED VIEW matview_kommuner AS
WITH multipol AS (SELECT kommune.omraade,
                         kl_kn.codevalue AS kommunenummer,
                         kommune.objtype,
                         kommune.samiskforvaltningsomraade AS samiskforvaltningsomrade,
                         kommune.objid
                  FROM kommune
                            LEFT JOIN kodeliste_kommunenummer kl_kn ON kl_kn.uuid = kommune.kommunenummer),
     fylke AS (SELECT fylke.objid,
                      nav.navn,
                      nav.administrativenhet_fylke_fk,
                      kl_fn.codevalue AS fylkesnummer
               FROM fylke
                        LEFT JOIN administrativenhetnavn nav ON nav.administrativenhet_fylke_fk = fylke.objid
                        LEFT JOIN kodeliste_fylkesnummer kl_fn ON kl_fn.uuid = fylke.fylkesnummer
               WHERE nav.rekkefoelge = 1
                  OR nav.rekkefoelge IS NULL),
     navnpri1 AS (SELECT nav.objid,
                         nav.navn,
                         spr.description                   AS sprak,
                         nav.administrativenhet_kommune_fk AS kommune_fk
                  FROM administrativenhetnavn nav
                           LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
                  WHERE nav.rekkefoelge = 1
                     OR nav.rekkefoelge IS NULL),
     navnpri2 AS (SELECT nav.objid,
                         nav.navn,
                         spr.description                   AS sprak,
                         nav.administrativenhet_kommune_fk AS kommune_fk
                  FROM administrativenhetnavn nav
                           LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
                  WHERE nav.rekkefoelge = 2),
     navnpri3 AS (SELECT nav.objid,
                         nav.navn,
                         spr.description                   AS sprak,
                         nav.administrativenhet_kommune_fk AS kommune_fk
                  FROM administrativenhetnavn nav
                           LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
                  WHERE nav.rekkefoelge = 3),
     navn_norsk AS (SELECT nav.objid,
                           nav.navn,
                           spr.description                   AS sprak,
                           nav.administrativenhet_kommune_fk AS kommune_fk
                    FROM administrativenhetnavn nav
                             LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
                    WHERE nav.spraak = 'nor')
SELECT multipol.objid,
       multipol.kommunenummer,
       multipol.samiskforvaltningsomrade,
       'Kommune'::text                                                AS objtype,
       fylke.navn                                                     AS fylkesnavn,
       fylke.fylkesnummer,
       navn_norsk.navn                                                AS navn_norsk,
       navnpri1.navn                                                  AS navn_pri_1,
       navnpri2.navn                                                  AS navn_pri_2,
       navnpri3.navn                                                  AS navn_pri_3,
       navnpri1.sprak                                                 AS navn_pri_1_sprak,
       navnpri2.sprak                                                 AS navn_pri_2_sprak,
       navnpri3.sprak                                                 AS navn_pri_3_sprak,
       multipol.omraade::geometry(Geometry, 25833)                    AS omrade,
       st_pointonsurface(multipol.omraade)::geometry(Geometry, 25833) AS punkt_i_omrade,
       st_asgeojson(st_pointonsurface(multipol.omraade), 12, 2)::json AS punkt_i_omrade_json,
       st_envelope(multipol.omraade)::geometry(Geometry, 25833)       AS bbox,
       st_asgeojson(st_envelope(multipol.omraade), 12, 2)::json       AS bbox_json,
       box2d(multipol.omraade)                                        AS bbox_enkel
FROM multipol
         LEFT JOIN fylke ON LEFT(multipol.kommunenummer, 2) = fylke.fylkesnummer
         LEFT JOIN navn_norsk ON multipol.objid = navn_norsk.kommune_fk
         LEFT JOIN navnpri1 ON multipol.objid = navnpri1.kommune_fk
         LEFT JOIN navnpri2 ON multipol.objid = navnpri2.kommune_fk
         LEFT JOIN navnpri3 ON multipol.objid = navnpri3.kommune_fk
ORDER BY multipol.kommunenummer;

CREATE MATERIALIZED VIEW matview_fylker AS
WITH multipol AS (
    SELECT
        omraade,
        kl_fn.codevalue AS fylkesnummer,
        objtype,
        samiskforvaltningsomraade AS samiskforvaltningsomrade,
        objid
    FROM fylke
		LEFT JOIN kodeliste_fylkesnummer kl_fn ON kl_fn.uuid = fylke.fylkesnummer
),
navnpri1 AS (
	SELECT nav.objid,
		nav.navn,
		spr.description AS sprak,
		nav.administrativenhet_fylke_fk AS fylke_fk
	FROM administrativenhetnavn nav
		LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
	WHERE nav.rekkefoelge = 1 OR nav.rekkefoelge IS NULL
),
navnpri2 AS (
	SELECT nav.objid,
		nav.navn,
		spr.description AS sprak,
		nav.administrativenhet_fylke_fk AS fylke_fk
	FROM administrativenhetnavn nav
		LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
	WHERE nav.rekkefoelge = 2
),
navnpri3 AS (
	SELECT nav.objid,
		nav.navn,
		spr.description AS sprak,
		nav.administrativenhet_fylke_fk AS fylke_fk
	FROM administrativenhetnavn nav
		LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
	WHERE nav.rekkefoelge = 3
),
navn_norsk AS (
	SELECT nav.objid,
		nav.navn,
		spr.description AS sprak,
		nav.administrativenhet_fylke_fk AS fylke_fk
	FROM administrativenhetnavn nav
		LEFT JOIN spraakkode spr ON nav.spraak = spr.identifier
	WHERE nav.spraak = 'nor'
)
SELECT multipol.objid,
       multipol.fylkesnummer,
       multipol.samiskforvaltningsomrade,
       multipol.objtype,
       navn_norsk.navn AS navn_norsk,
       navnPri1.navn AS navn_pri_1,
       navnPri2.navn AS navn_pri_2,
       navnPri3.navn AS navn_pri_3,
       navnPri1.sprak AS navn_pri_1_sprak,
       navnPri2.sprak AS navn_pri_2_sprak,
       navnPri3.sprak AS navn_pri_3_sprak,
       multipol.omraade::geometry(Geometry,25833) AS omrade,
        ST_PointOnSurface(multipol.omraade)::geometry(Geometry,25833) AS punkt_i_omrade,
        ST_AsGeoJSON(ST_PointOnSurface(multipol.omraade), 12, 2)::json AS punkt_i_omrade_json,
        ST_Envelope(multipol.omraade)::geometry(Geometry,25833) AS bbox,
        ST_AsGeoJSON(ST_Envelope(multipol.omraade), 12, 2)::json AS bbox_json,
        Box2D(multipol.omraade) AS bbox_enkel
FROM multipol
         LEFT JOIN navn_norsk ON multipol.objid = navn_norsk.fylke_fk
         LEFT JOIN navnPri1 ON multipol.objid = navnPri1.fylke_fk
         LEFT JOIN navnPri2 ON multipol.objid = navnPri2.fylke_fk
         LEFT JOIN navnPri3 ON multipol.objid = navnPri3.fylke_fk
ORDER BY multipol.fylkesnummer;


--All SQL under her er fra gammelt repo: https://bitbucket.statkart.no/projects/I5DMS/repos/sql_to_run_on_import/browse/administrative_enheter.sql
/*
FDW cant use search_path, they need a "stable" schema.
So we have to create a copy of the matview in tableform in a stable schema (a view or matview would be dropped when we delete the underlying schema), and update it without causing problems for other jobs reading those same tables
*/
--fdw kommuner
CREATE TABLE IF NOT EXISTS public.kommuner_for_fdw
AS SELECT   kommunenummer,
            fylkesnavn,
            fylkesnummer,
            navn_norsk,
            navn_pri_1,
            omrade,
            st_transform(omrade, 25833) as omrade_25833,
            st_transform(omrade, 32633) as omrade_32633
   FROM {0}.matview_kommuner;

UPDATE public.kommuner_for_fdw t2
SET    (    kommunenummer,
           fylkesnavn,
           fylkesnummer,
           navn_norsk,
           navn_pri_1,
           omrade,
           omrade_25833,
           omrade_32633
           )
           = (       t1.kommunenummer,
                     t1.fylkesnavn,
                     t1.fylkesnummer,
                     t1.navn_norsk,
                     t1.navn_pri_1,
                     t1.omrade,
                     st_transform(t1.omrade, 25833),
                     st_transform(t1.omrade, 32633)
        )
    FROM   {0}.matview_kommuner t1
WHERE  t2.kommunenummer = t1.kommunenummer;

DELETE FROM public.kommuner_for_fdw kf
WHERE NOT EXISTS (
        SELECT FROM {0}.matview_kommuner mk
           WHERE mk.kommunenummer = kf.kommunenummer
    );

--fdw fylker
CREATE TABLE IF NOT EXISTS public.fylker_for_fdw
AS SELECT   fylkesnummer,
            navn_norsk,
            navn_pri_1,
            omrade,
            st_transform(omrade, 25833) as omrade_25833,
            st_transform(omrade, 32633) as omrade_32633
   FROM {0}.matview_fylker;

UPDATE public.fylker_for_fdw t2
SET    (    fylkesnummer,
           navn_norsk,
           navn_pri_1,
           omrade,
           omrade_25833,
           omrade_32633
           )
           = (       t1.fylkesnummer,
                     t1.navn_norsk,
                     t1.navn_pri_1,
                     t1.omrade,
                     st_transform(t1.omrade, 25833),
                     st_transform(t1.omrade, 32633)
        )
    FROM   {0}.matview_fylker t1
WHERE  t2.fylkesnummer = t1.fylkesnummer;

DELETE FROM public.fylker_for_fdw kf
WHERE NOT EXISTS (
        SELECT FROM {0}.matview_fylker mk
           WHERE mk.fylkesnummer = kf.fylkesnummer
    );


GRANT SELECT ON ALL TABLES IN SCHEMA public TO dbles;
CREATE INDEX IF NOT EXISTS public_fylker_for_fdw_omrade_gist ON public.fylker_for_fdw USING GIST(omrade);
CREATE INDEX IF NOT EXISTS public_fylker_for_fdw_omrade_25833_gist ON public.fylker_for_fdw USING GIST(omrade_25833);
CREATE INDEX IF NOT EXISTS public_fylker_for_fdw_omrade_32633_gist ON public.fylker_for_fdw USING GIST(omrade_32633);

CREATE INDEX IF NOT EXISTS public_kommuner_for_fdw_omrade_gist ON public.kommuner_for_fdw USING GIST(omrade);
CREATE INDEX IF NOT EXISTS public_kommuner_for_fdw_omrade_25833_gist ON public.kommuner_for_fdw USING GIST(omrade_25833);
CREATE INDEX IF NOT EXISTS public_kommuner_for_fdw_omrade_32633_gist ON public.kommuner_for_fdw USING GIST(omrade_32633);

-- *****************************************************
-- Materialized View: inspire_au40_lowerlevelunit

-- DROP MATERIALIZED VIEW inspire_au40_lowerlevelunit;

CREATE MATERIALIZED VIEW {0}.inspire_au40_lowerlevelunit AS
SELECT '0'::text AS nationalcode_up,
        '#AdministrativeUnit.'::text || fylke.fylkesnummer AS href_lo
FROM {0}.fylke
GROUP BY fylke.fylkesnummer
UNION ALL
SELECT f.fylkesnummer AS nationalcode_up,
       '#AdministrativeUnit.'::text || k.kommunenummer AS href_lo
FROM {0}.kommune k,
    {0}.fylke f
WHERE "left"(k.kommunenummer, 2) = f.fylkesnummer
GROUP BY f.fylkesnummer, k.kommunenummer;

-- *****************************************************
-- Materialized View: inspire_au40_nationallevelname

-- DROP MATERIALIZED VIEW inspire_au40_nationallevelname;

CREATE MATERIALIZED VIEW {0}.inspire_au40_nationallevelname AS
SELECT 3 AS levelnr,
       'kommune'::text AS nationallevelname,
        'no'::text AS lang
UNION
SELECT 2 AS levelnr,
       'fylke'::text AS nationallevelname,
        'no'::text AS lang
UNION
SELECT 1 AS levelnr,
       'nasjon'::text AS nationallevelname,
        'no'::text AS lang
UNION
SELECT 3 AS levelnr,
       'municipality'::character varying AS nationallevelname,
    'en'::text AS lang
UNION
SELECT 2 AS levelnr,
       'region'::character varying AS nationallevelname,
    'en'::text AS lang
UNION
SELECT 1 AS levelnr,
       'nation'::character varying AS nationallevelname,
    'en'::text AS lang;

--  **********************************************************
-- Materialized View: inspire_au40_administrative_unit_name

-- DROP MATERIALIZED VIEW inspire_au40_administrative_unit_name;

CREATE MATERIALIZED VIEW {0}.inspire_au40_administrative_unit_name AS
SELECT '0'::text AS nationalcode,
        'Norge'::text AS spellingtext,
        'nor'::text AS language,
    1 AS prioritet,
    'http://inspire.ec.europa.eu/codelist/NativenessValue/endonym/endonym'::text AS nativeness,
    'http://inspire.ec.europa.eu/codelist/NameStatusValue/official/official'::text AS namestatus,
    'Norwegian Placename Register'::text AS sourceofname,
    'Latn'::text AS spellingscript
UNION ALL
SELECT DISTINCT f.fylkesnummer AS nationalcode,
                n.navn AS spellingtext,
                n.sprak AS language,
    n.rekkefolge AS prioritet,
    'http://inspire.ec.europa.eu/codelist/NativenessValue/endonym/endonym'::text AS nativeness,
    'http://inspire.ec.europa.eu/codelist/NameStatusValue/official/official'::text AS namestatus,
    'Norwegian Placename Register'::text AS sourceofname,
    'Latn'::text AS spellingscript
FROM {0}.administrativenhetnavn n,
    {0}.fylke f
WHERE n.fylke_fk = f.objid
UNION ALL
SELECT DISTINCT k.kommunenummer AS nationalcode,
                n.navn AS spellingtext,
                n.sprak AS language,
    n.rekkefolge AS prioritet,
    'http://inspire.ec.europa.eu/codelist/NativenessValue/endonym/endonym'::text AS nativeness,
    'http://inspire.ec.europa.eu/codelist/NameStatusValue/official/official'::text AS namestatus,
    'Norwegian Placename Register'::text AS sourceofname,
    'Latn'::text AS spellingscript
FROM {0}.administrativenhetnavn n,
    {0}.kommune k
WHERE n.kommune_fk = k.objid;

--  **********************************************************
-- Materialized View: inspire_au40_administrative_units

-- DROP MATERIALIZED VIEW inspire_au40_administrative_units;

CREATE MATERIALIZED VIEW {0}.inspire_au40_administrative_units AS
SELECT st_multi(st_union(st_curvetoline(f.omrade))) AS geometry,
       1 AS level,
       0::text AS nationalcode,
        'AdministrativeUnit.'::text || '0'::text AS localid,
        'http://data.geonorge.no/inspire/au'::text AS namespace,
        'http://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/1stOrder'::text AS nationallevelhref,
   -- max(f.oppdateringsdato) AS beginlifespanversion,
        NULL AS beginlifespanversion,
       'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Missing'::text AS beginlifespanversion_nilreason,
        'true'::text AS beginlifespanversion_nil,
        NULL::text AS upperlevelunit,
        'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated'::Text AS boundary_nilreason,
        true::boolean AS boundary_nil
FROM {0}.fylke f
GROUP BY 1::integer -- f.oppdateringsdato
UNION ALL
SELECT st_multi(st_collect(st_curvetoline(f.omrade))) AS geometry,
       2 AS level,
       f.fylkesnummer AS nationalcode,
       'AdministrativeUnit.'::text || f.fylkesnummer AS localid,
        'http://data.geonorge.no/inspire/au'::text AS namespace,
        'http://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/2ndOrder/'::text AS nationallevelhref,
        f.oppdateringsdato AS beginlifespanversion,
       CASE
           WHEN f.oppdateringsdato IS NULL THEN 'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Missing'::text
           ELSE NULL::text
           END AS beginlifespanversion_nilreason,
       CASE
           WHEN f.oppdateringsdato IS NULL THEN 'true'::text
           ELSE NULL::text
           END AS beginlifespanversion_nil,
       '#AdministrativeUnit.0'::text AS upperlevelunit,
        'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated'::Text AS boundary_nilreason,
        true::boolean AS boundary_nil
FROM {0}.fylke f
GROUP BY f.fylkesnummer, f.oppdateringsdato
UNION ALL
SELECT st_multi(st_collect(st_curvetoline(k.omrade))) AS geometry,
       3 AS level,
       k.kommunenummer AS nationalcode,
       'AdministrativeUnit.'::text || k.kommunenummer AS localid,
        'http://data.geonorge.no/inspire/au'::text AS namespace,
        'http://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/3rdOrder'::text AS nationallevelhref,
        k.oppdateringsdato AS beginlifespanversion,
       CASE
           WHEN k.oppdateringsdato IS NULL THEN 'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Missing'::text
           ELSE NULL::text
           END AS beginlifespanversion_nilreason,
       CASE
           WHEN k.oppdateringsdato IS NULL THEN 'true'::text
           ELSE NULL::text
           END AS beginlifespanversion_nil,
       '#AdministrativeUnit.'::text || "left"(k.kommunenummer, 2) AS upperlevelunit,
        'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated'::Text AS boundary_nilreason,
        true::boolean AS boundary_nil
FROM {0}.kommune k
GROUP BY k.kommunenummer, k.oppdateringsdato
;





--  **********************************************************

-- Materialized View: inspire_au40_administrative_boundary

-- DROP MATERIALIZED VIEW inspire_au40_administrative_boundary;

CREATE MATERIALIZED VIEW {0}.inspire_au40_administrative_boundary AS
SELECT st_curvetoline(r.grense) AS geometry,
       r.objid::text AS objid,
        'agreed'::text AS legalstatus,
        'edgeMatched'::text AS technicalstatus,
        'AdministrativeBoundary.'::text || r.objid::text AS localid,
        'http://data.geonorge.no/inspire/au'::text AS namespace,
        'http://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/1stOrder'::text AS nationallevelhref,
        r.oppdateringsdato AS beginlifespanversion,
       CASE
           WHEN r.oppdateringsdato IS NULL THEN 'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Missing'::text
           ELSE NULL::text
           END AS beginlifespanversion_nilreason,
       CASE
           WHEN r.oppdateringsdato IS NULL THEN 'true'::text
           ELSE NULL::text
           END AS beginlifespanversion_nil,
       'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated'::text AS admunit_nilreason,
        true AS admunit_nil
FROM {0}.riksgrense r
UNION ALL
SELECT st_curvetoline(f.grense) AS geometry,
       f.objid::text AS objid,
        'agreed'::text AS legalstatus,
        'edgeMatched'::text AS technicalstatus,
        'AdministrativeBoundary.'::text || f.objid::text AS localid,
        'http://data.geonorge.no/inspire/au'::text AS namespace,
        'http://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/2ndOrder'::text AS nationallevelhref,
        f.oppdateringsdato AS beginlifespanversion,
       CASE
           WHEN f.oppdateringsdato IS NULL THEN 'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Missing'::text
           ELSE NULL::text
           END AS beginlifespanversion_nilreason,
       CASE
           WHEN f.oppdateringsdato IS NULL THEN 'true'::text
           ELSE NULL::text
           END AS beginlifespanversion_nil,
       'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated'::text AS admunit_nilreason,
        true AS admunit_nil
FROM {0}.fylkesgrense f
UNION ALL
SELECT st_curvetoline(k.grense) AS geometry,
       k.objid::text AS objid,
        'agreed'::text AS legalstatus,
        'edgeMatched'::text AS technicalstatus,
        'AdministrativeBoundary.'::text || k.objid::text AS localid,
        'http://data.geonorge.no/inspire/au'::text AS namespace,
        'http://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/3rdOrder'::text AS nationallevelhref,
        k.oppdateringsdato AS beginlifespanversion,
       CASE
           WHEN k.oppdateringsdato IS NULL THEN 'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Missing'::text
           ELSE NULL::text
           END AS beginlifespanversion_nilreason,
       CASE
           WHEN k.oppdateringsdato IS NULL THEN 'true'::text
           ELSE NULL::text
           END AS beginlifespanversion_nil,
       'http://inspire.ec.europa.eu/codelist/VoidReasonValue/Unpopulated'::text AS admunit_nilreason,
        true AS admunit_nil
FROM {0}.kommunegrense k;

----- Views for wfs for administrative enheter

CREATE OR REPLACE VIEW {0}.wfs_fylkesgrense AS
SELECT fylkesgrense.objid,
       fylkesgrense.objtype,
       st_curvetoline(fylkesgrense.grense) AS grense,
       fylkesgrense.omtvistet,
       fylkesgrense.lokalid,
       fylkesgrense.navnerom,
       fylkesgrense.versjonid,
       fylkesgrense.datafangstdato,
       fylkesgrense.oppdateringsdato,
       fylkesgrense.datauttaksdato,
       fylkesgrense.noyaktighet,
       fylkesgrense.opphav,
       fylkesgrense.omradeid,
       fylkesgrense.originaldatavert,
       fylkesgrense.kopidato,
       fylkesgrense.noyaktighetsklasse,
       fylkesgrense.grensestatus,
       fylkesgrense.fastsettingstype,
       fylkesgrense.folgerterrengdetalj,
       fylkesgrense.malemetode
FROM {0}.fylkesgrense;

CREATE OR REPLACE VIEW {0}.wfs_kommunegrense AS
SELECT kommunegrense.objid,
       kommunegrense.objtype,
       st_curvetoline(kommunegrense.grense) AS grense,
       kommunegrense.omtvistet,
       kommunegrense.lokalid,
       kommunegrense.navnerom,
       kommunegrense.versjonid,
       kommunegrense.datafangstdato,
       kommunegrense.oppdateringsdato,
       kommunegrense.datauttaksdato,
       kommunegrense.noyaktighet,
       kommunegrense.opphav,
       kommunegrense.omradeid,
       kommunegrense.originaldatavert,
       kommunegrense.kopidato,
       kommunegrense.noyaktighetsklasse,
       kommunegrense.grensestatus,
       kommunegrense.fastsettingstype,
       kommunegrense.folgerterrengdetalj,
       kommunegrense.malemetode
FROM {0}.kommunegrense;

CREATE OR REPLACE VIEW {0}.wfs_nasjon
AS SELECT nasjon.objid,
          nasjon.objtype,
          nasjon.lokalid,
          nasjon.navnerom,
          nasjon.versjonid,
          nasjon.datafangstdato,
          nasjon.oppdateringsdato,
          nasjon.datauttaksdato,
          nasjon.opphav,
          st_curvetoline(nasjon.omrade) AS omrade
   FROM {0}.nasjon;

CREATE OR REPLACE VIEW {0}.wfs_fylke
AS SELECT fylke.objid,
          fylke.objtype,
          fylke.samiskforvaltningsomrade,
          fylke.lokalid,
          fylke.navnerom,
          fylke.versjonid,
          fylke.datafangstdato,
          fylke.oppdateringsdato,
          fylke.datauttaksdato,
          fylke.opphav,
          fylke.fylkesnummer,
          st_curvetoline(fylke.omrade) AS omrade
   FROM {0}.fylke;

CREATE OR REPLACE VIEW {0}.wfs_kommune
AS SELECT kommune.objid,
          kommune.objtype,
          kommune.samiskforvaltningsomrade,
          kommune.lokalid,
          kommune.navnerom,
          kommune.versjonid,
          kommune.datafangstdato,
          kommune.oppdateringsdato,
          kommune.datauttaksdato,
          kommune.opphav,
          kommune.kommunenummer,
          st_curvetoline(kommune.omrade) AS omrade
   FROM {0}.kommune;



----------Illustrasjonskart med forenklede kommuner. Brukes i apiet

CREATE MATERIALIZED VIEW {0}.matview_api_kommuner_illustrasjonskart as
with kommuner_nocurves AS (
        SELECT objid, kommunenummer, st_curvetoline(omrade) AS kommunepolygon
        FROM {0}.kommune
),
navnPri1 AS (
    SELECT
        objid,
        navn,
        spr.description AS sprak,
        kommune_fk
    FROM {0}.administrativenhetnavn nav
    LEFT JOIN {0}.sprakkode spr ON nav.sprak = spr.identifier
    WHERE rekkefolge = 1 OR rekkefolge IS NULL
),
kommunenavn_joined AS (
  SELECT k.objid, k.kommunenummer, navnPri1.navn AS kommunenavn, k.kommunepolygon
  FROM kommuner_nocurves k
  LEFT JOIN navnPri1 ON k.objid = navnPri1.kommune_fk
),
extring AS (
  SELECT kommunenummer, ST_EXTERIORRING((ST_DUMPRINGS(kommunepolygon)).geom) AS kommunelinestring
  FROM kommunenavn_joined
),
linemerged AS (
  SELECT st_simplifyPreserveTopology(st_linemerge(st_union(kommunelinestring)), 0.04) AS omrade
  FROM extring
),
polygonized AS (
  SELECT (st_dump(st_polygonize(distinct st_node(omrade)))).geom AS simplified_polygon
  FROM linemerged
)
SELECT
    k.kommunenummer::text,
        ST_RemoveRepeatedPoints(ST_Union(p.simplified_polygon::geometry(Geometry, 4258)), 0.001) AS omrade,
    k.kommunenavn
FROM kommunenavn_joined k, polygonized p
where st_intersects(k.kommunepolygon, p.simplified_polygon)
  and st_area(st_intersection(k.kommunepolygon, p.simplified_polygon))/st_area(p.simplified_polygon) > 0.5
group by kommunenavn, kommunenummer;

CREATE MATERIALIZED VIEW {0}.matview_api_kommuner_illustrasjonskart_geojson as
SELECT jsonb_build_object(
               'type',     'FeatureCollection',
               'features', jsonb_agg(features.feature)
           ) AS featurecollection
FROM (
         SELECT jsonb_build_object(
                        'type',       'Feature',
                        'geometry',   ST_AsGeoJSON(omrade, 3, 0)::jsonb,
                        'properties', jsonb_build_object('kommunenummer', kommunenummer,
                                                         'kommunenavn', kommunenavn )
                    ) AS feature
         FROM (SELECT * FROM {0}.matview_api_kommuner_illustrasjonskart) inputs) features;