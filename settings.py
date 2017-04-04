import datetime
import os
import psycopg2 as dbapi2
import json
import re

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import g
from flask.helpers import url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn
