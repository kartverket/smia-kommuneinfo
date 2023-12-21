import locale

from flask import Flask
from flask_cors import CORS

import config as cf

app = Flask(__name__)
CORS(app)

locale.setlocale(locale.LC_ALL, cf.locale_choice)  # to sort æøå correctly
app.config['JSON_AS_ASCII'] = cf.set_json_as_ascii

from app import routes
