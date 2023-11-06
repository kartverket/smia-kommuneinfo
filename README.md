# REST-API over administrative-enheter datasettet. 

Bygd i Python med Flask, marshmallow og apispec. Baserer seg på materialized view som forenkler datastrukturen i administrative-enheter-modellen. 

## Oppsett på windows
1. Installere python (via firmaportal)
2. Oppdater system-miljøvariable til å peke på python (installeres under program files om man bruker firmaportal) og python/Scripts
3. Lag og aktiver et python virtual environment (https://python.land/virtual-environments/virtualenv). To muligheter:
    - `python -m venv venv`
    - `virtualenv venv` (forutsetter at man har installert virtualenv: pip install virtualenv)
4. Aktiver virtual environment. Hvordan du gjør det kommer an på om du er i cmd shell eller i et *nix-shell:
    - cmd shell: `venv\Scripts\activate.bat`
    - *nix-shell: `source venv\Scripts\activate`
5. Installer avhengigheter vha pip (disse finner man igjen i venv/Lib/site-packages etter installasjon):
   a: NB! Grunnet problemer med psycopg2-binary==2.8.* lokalt (må brukes på centOS-serverne i prod) har jeg laget en egen requirements_v2.txt. Denne definerer bare at vi bruker psycopg2, da fungerer det lokalt
    - Alle avhengigheter (for å kunne kjøre tester lokalt): `pip install -r dev_requirements.txt` <-- Denne tar også med seg avhengigheter definert i requirements.txt
    - Avhengigheter bare for å kjøre opp applikasjonen: `pip install -r requirements_v2.txt`
6. Oppdater config.py med korrekte verdier for database og user, dvs kommenter inn de du ønsker/sett egne - foreløpig manuelt steg
7. Sett miljøvariable for hhv `DBCLUSTER_2` og `PG_PASS_ADM_ENH` for den databasen du ønsker å koble deg opp mot

## Oppsett mac

Som i Windows, men:

1. Endre locale i config.py til `no_NO.UTF-8`
2. Trenger også `psycopg2-binary`-pakken. Denne er nå lagt til i `dev_requirements.txt`

### Lokalt dev-miljø
6. Aktiver Flask debug mode: `export FLASK_DEBUG=True`
7. Start flask dev-server: `flask run`
8. Gå til <http://localhost:5000>
9. Dersom man skal teste endepunktene kan man ikke teste disse via den genererte siden ettersom disse går rett mot endepunktene på geonorge. Egne endepunkt ligger rett på localhost:5000, eksempelvis: http://localhost:5000/kommuner  

## Installering (rutine fra gammelt repo, basert på linux)
1. git clone dette repoet
2. Lag og aktiver et python virtual environment
3. Oppgrader pip
4. Installer pakkene i requirements.txt
5. Sett riktige environment variables. Se i config.py for å se hva som må settes.

### Kjøre tester
1. Installer og aktiver dev-dependencies.
2. Naviger til prosjektets root-mappe.
3. Kjør testene:
```Bash
# How to run the integration tests:
# 1 - The flask instance needs to be up and running
# 2 - Export the url you wish to test against.
# Either export it as a system variable or include it when running the test:
TAVERN_TEST_URL='http://localhost:5000/' pytest
```

## TODOS
- Kjøre opp applikasjonen i docker
- Oppgradere alt av avhengigheter - skrur på dependabot på github
- Deploy med github actions og argo
- Oppsett på mac