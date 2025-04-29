# REST-API For Administrative Enheter (kommuner, fylker)

Bygd i Python med Flask, marshmallow og apispec. Data er hentet fra NIBAS med en [import-jobb](https://github.com/kartverket/smia-kommuneinfo-import).

## Lokal utvikling

Det er anbefalt å kjøre import-jobb mot lokal database først. Det krever at du har satt opp en lokal instans av NIBAS Backend + DB, og Kommuneinfo DB. Docker compose i import-jobb repo er nyttig hjelp her.

1. Lag og aktiver et python virtual environment (https://python.land/virtual-environments/virtualenv).
   - `python -m venv venv`
2. Aktiver virtual environment. Hvordan du gjør det kommer an på om du er i cmd shell eller i et \*nix-shell:
   - cmd shell: `venv\Scripts\activate.bat`
   - MacOs / Linux: `source venv/bin/activate`
3. Installer avhengigheter med pip
   - Alle avhengigheter (for å kunne kjøre tester lokalt): `pip install -r dev_requirements.txt`
   - Avhengigheter bare for å kjøre opp applikasjonen: `pip install -r requirements.txt`
4. Sett følgende miljøvariabler:
   - `KOMMUNEINFO_DB_USER` - default `nibas`
   - `KOMMUNEINFO_DB_PASSWORD` - default `nibas`
   - `KOMMUNEINFO_DB_URI` - default `postgresql://localhost:5432/nibas`
5. Start flask dev-server: `flask run`
   Kan eventuelte start gunicorn server med: `gunicorn -c gunicorn_config.py main:app`. Merk at det har vært trøbbel her med å bruke gunicorn i virtual environment.
6. Appen kan nå nås på `http://localhost:5000`

### Kjøre tester

1.  Installer og aktiver dev-dependencies: `pip install -r dev_requirements.txt` i rot
2.  Kjør testene:

        $ TAVERN_TEST_URL=http://localhost:5000
        $ flask run
        $ pytest

Merk at testene ikke kjører opp en egen in-memory database eller liknende, og dermed må du ha databasen kjørende lokalt.

### Kjøre tester mot deployerte miljøer (med skript)

Etter å ha installert dev-dependencies (`pip install -r dev_requirements.txt`) kan du bruke `run_tests.sh`-skriptet for å kjøre Tavern-integrasjonstestene mot de ulike deployerte miljøene.

NB: Du må kanskje gjøre skriptet kjørbart én gang først:
```bash
chmod +x run_tests.sh
```

Skriptet tar miljøet du vil teste mot som argument (`dev`, `test`, eller `prod`).

**Eksempler:**

*   Kjør tester mot **dev**-miljøet:
    ```bash
    ./run_tests.sh dev
    ```
*   Kjør tester mot **test**-miljøet:
    ```bash
    ./run_tests.sh test
    ```
*   Kjør tester mot **prod**-miljøet:
    ```bash
    ./run_tests.sh prod
    ```

Skriptet setter automatisk `TAVERN_TEST_URL` basert på valgt miljø og kjører `tavern-ci`.

### TODO

- Tester som del av pipeline
- Tester burde helst ikke være integrasjonstester med database
