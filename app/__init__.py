import locale

from flask import Flask

import config as cf

app = Flask(__name__)

locale.setlocale(locale.LC_ALL, cf.locale_choice)  # to sort æøå correctly
app.config['JSON_AS_ASCII'] = cf.set_json_as_ascii

from app import routes

