# verify that illustrasjonskart contains all kommuner
import requests

knavn_response = requests.get('https://ws.geonorge.no/kommuneinfo/v1/kommuner?filtrer=kommunenavn')

knavn = knavn_response.json()

illustrasjonskart = str(requests.get('https://ws.geonorge.no/kommuneinfo/v1/kommuner/illustrasjonskart').json())


for k in knavn:
    navn = k.get('kommunenavn')
    if navn not in illustrasjonskart:
        print('error navn %s' % navn)
