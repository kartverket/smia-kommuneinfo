# REST-API over administrative-enheter datasettet.

Bygd i Python med Flask, marshmallow og apispec. Baserer seg på materialized view som forenkler datastrukturen i administrative-enheter-modellen.

## Lokal utvikling

1. Lag og aktiver et python virtual environment (https://python.land/virtual-environments/virtualenv).
   - `python -m venv venv`
2. Aktiver virtual environment. Hvordan du gjør det kommer an på om du er i cmd shell eller i et \*nix-shell:
   - cmd shell: `venv\Scripts\activate.bat`
   - \*nix-shell: `source venv\Scripts\activate`
   - MacOs / Linux: `source venv/bin/activate`
3. Installer avhengigheter med pip
   - Alle avhengigheter (for å kunne kjøre tester lokalt): `pip install -r dev_requirements.txt`
   - Avhengigheter bare for å kjøre opp applikasjonen: `pip install -r requirements.txt`
4. Sett følgende miljøvariabler:
   - `KOMMUNEINFO_DB_USER` - default `nibas`
   - `KOMMUNEINFO_DB_PASSWORD` - default `nibas`
   - `KOMMUNEINFO_DB_URI` - default `postgresql://localhost:5432/nibas`
   - `FLASK_DEBUG=True` - brukes kun under utvikling, gjør at du kan bruke OpenAPI lokalt for å teste endepunkter
5. Start flask dev-server: `flask run`
6. Appen kan nå nås på `http://localhost:5000`

### Kjøre tester

1.  Installer og aktiver dev-dependencies: `pip install -r dev_requirements.txt` i rot
2.  Kjør testene:

        $ TAVERN_TEST_URL=http://localhost:5000
        $ flask run
        $ pytest

Merk at testene ikke kjører opp en egen in-memory database eller liknende, og dermed må du ha databasen kjørende lokalt.

### TODO

- Tester som del av pipeline
- Tester burde helst ikke være integrasjonstester med database
- Ikke instansiere databaseconnection hver gang men bruke pooling
