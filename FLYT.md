## Overordnet flyt for data fra geonorge og ut i kommuneinfo-API.

1. Hver natt kl 03 kjøres det en jobb på jenkins: http://rin-ap0508:8080/job/geonorge_administrative_enheter_sjekk/
   - Denne gjør litt sjekker på at data ser i orden ut (kode: https://bitbucket.statkart.no/projects/I5DMS/repos/geonorge_tests/browse) 
2. Den har videre to post-build actions som starter følgende jobber: geonorge_administrative_enheter,geonorge_administrative_enheter_fellesbase
3. Jobben Geonorge_administrative_enheter (http://rin-ap0508:8080/job/geonorge_administrative_enheter/) kaller videre på geonorge_import_prod med noen parametre: ![TRIGGER_BUILD](/readme/geonorge_administrative_enheter.jpg "Trigger ny jobb") 
4. Geonorge_import_prod importerer data fra valgt geonorge-database til valgt import-database. Til denne jobben oppgis parametret db=administrative_enheter (som vist på skjermbilde). Det sørger for at fila administrative_enheter.sql kjører etter at importen er ferdig. Vi får med andre ord følgende steg:
   - vectordata_import_setup.py med administrative_enheter-setup.sql som input
   - import_from_pg_schema_to_pg_db.py for å importere data
   - vectordata_import_finalize.py med administrative_enheter.sql som input-parameter
   - Man kan også bruke parametret -r "kodeliste på geonorge" for å laste inn kodelister og legge de inn som tabeller i databasen: ![EKSTERNE_KODELISTER](/readme/eksterne_kodelister.jpg "Laster inn eksterne kodelister") 
5. administrative_enheter.sql (https://bitbucket.statkart.no/projects/I5DMS/repos/sql_to_run_on_import/browse/administrative_enheter.sql) er den som faktisk masserer dataene litt og oppretter mat. views. Her kan man da bruke kodelistene (hvis oppgitt)
6. Dersom en av jobbene på jenkins feiler sendes eposten til smia-alerts-aaaaiemizabhowhnquwxlyfzui@kartverketgroup.slack.com

## Tilpasninger til ny modell
Har endret på hvordan materialiserte views opprettes, se på matview_kommuner og matview_fylker i [administrative_enheter.sql](import_sql/administrative_enheter.sql)
Siden vi ikke oppretter kodelister automagisk som nevnt i steg 4 over har vi lagt inn et par små script for å kunne opprette disse lokalt/dev/test, se 
Ved å opprette disse to viewene kan man kjøre opp applikasjonen 
