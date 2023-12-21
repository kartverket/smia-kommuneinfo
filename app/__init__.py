import locale
import re
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
import config as cf

app = Flask(__name__)

class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix
    
    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This route does not exist.".encode()]
        
metrics = PrometheusMetrics(app)
metrics.register_default(
    metrics.counter(
        'status_and_path', 'Request count by status and path',
        labels={'status': lambda r: r.status_code, 'path': lambda: request.generalized_path, 'resource': lambda: request.path}
    )
)
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=cf.basepath)

@app.before_request
def before_request():
    # Capture the URL rule pattern instead of the actual request path
    rule_pattern = request.url_rule.rule if request.url_rule else request.path
    generalized_path = re.sub(r'<[^>]*>', ':id', rule_pattern)  # Replace dynamic parts with :id
    request.generalized_path = generalized_path



locale.setlocale(locale.LC_ALL, cf.locale_choice)  # to sort æøå correctly
app.config['JSON_AS_ASCII'] = cf.set_json_as_ascii

