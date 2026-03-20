from flask import Flask, g
from .marketfactor import market_bp
from .combinationfactor import combination_bp
from .lawfactor import law_bp
from .techfactor import tech_bp
from .basicinfo import basic_info
from .evaluation import evaluation_bp
from .dataimport import import_bp
import os

'''
export FLASK_APP=app  # path to app
export FLASK_DEBUG=1
flask run
'''
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
app.config['ESURL'] = os.environ.get('ESURL', 'http://10.0.9.80:9200')
app.register_blueprint(market_bp)
app.register_blueprint(combination_bp)
app.register_blueprint(law_bp)
app.register_blueprint(tech_bp)
app.register_blueprint(basic_info)
app.register_blueprint(evaluation_bp)
app.register_blueprint(import_bp)


@app.route('/')
def root():
    return 'hello world!'
